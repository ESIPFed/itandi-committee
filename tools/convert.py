#!/usr/bin/env python3
"""Convert the IT&I wiki harvest into Markdown for the GitHub Pages archive.

This is a local authoring tool, not a CI step: it reads the sibling esip_wiki
harvest (../esip_wiki/archive, ~4.5 GB, not committed) and writes Markdown and
attachments into docs/. The GitHub Action builds only what this writes.

Per page it:
  1. loads the wikitext from the manifest path (or the full-history XML for the
     handful of pages with no current revision, e.g. DIAL),
  2. protects MediaWiki <html>...</html> raw blocks (the YouTube <iframe> embeds
     pandoc would otherwise escape) behind placeholders,
  3. runs `pandoc -f mediawiki -t gfm`,
  4. restores the raw blocks and rewrites links/images: internal links to local
     pages resolve to their slug; in-archive File:/Media: resolve to docs/files/;
     everything else points at the live wiki and is logged to external-links.json.

Run from the repo root:  python tools/convert.py [--only "Title;Title"]
"""
from __future__ import annotations

import argparse
import html
import json
import re
import shutil
import subprocess
import sys
import unicodedata
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import unquote

REPO = Path(__file__).resolve().parent.parent
HARVEST = REPO / ".." / "esip_wiki" / "archive"
DOCS = REPO / "docs"
FILES_OUT = DOCS / "files"
TOOLS = REPO / "tools"
LIVE = "https://wiki.esipfed.org/"

def log(msg: str) -> None:
    print(msg, file=sys.stderr)


# --- scope and title normalization -----------------------------------------

NS_PREFIXES = ("File:", "Category:", "Template:", "Media:", "Image:")


def load_included_articles() -> list[str]:
    """Article titles marked 'include' in the curated tools/scope.tsv worklist."""
    titles = []
    for line in (TOOLS / "scope.tsv").read_text(encoding="utf-8").splitlines()[1:]:
        if not line.strip():
            continue
        decision, _depth, title, *_ = line.split("\t")
        if decision == "include":
            titles.append(title)
    return titles


def norm_title(t: str) -> str:
    """MediaWiki title normalization: underscores->spaces, trim, cap first char."""
    t = t.replace("_", " ").strip()
    return t[:1].upper() + t[1:] if t else t


def make_slug(title: str) -> str:
    s = title.replace("/", "-")
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    s = re.sub(r"[^A-Za-z0-9]+", "-", s).strip("-").lower()
    return s or "page"


def build_slugmap(articles: list[str]) -> dict[str, str]:
    """Map normalized article title -> slug, stable and collision-free."""
    slugmap: dict[str, str] = {}
    used: set[str] = set()
    for title in sorted(articles):
        base = make_slug(title)
        slug = base
        n = 2
        while slug in used:
            slug = f"{base}-{n}"
            n += 1
        used.add(slug)
        slugmap[norm_title(title)] = slug
    return slugmap


# --- file (attachment) resolution -------------------------------------------


def build_filemap() -> dict[str, str]:
    """Map several spellings of an upload name -> on-disk local filename."""
    fi = json.loads((HARVEST / "files-index.json").read_text(encoding="utf-8"))
    fmap: dict[str, str] = {}
    for rec in fi:
        local = rec.get("local")
        if not local:
            continue
        title = rec.get("title", "")  # "File:Name With Spaces.pdf"
        name = title.split(":", 1)[1] if ":" in title else title
        for key in {name, name.replace(" ", "_"), rec.get("name", "")}:
            if key:
                fmap[key] = local
                fmap[norm_title(key)] = local
    return fmap


# --- wikitext loading --------------------------------------------------------


def load_manifest() -> dict:
    return json.loads((HARVEST / "manifest.json").read_text(encoding="utf-8"))


def wikitext_for(title: str, manifest: dict) -> str | None:
    entry = manifest.get(title)
    if entry:
        path = HARVEST / "wikitext" / entry["path"]
        if path.exists():
            return path.read_text(encoding="utf-8")
    return None


def wikitext_from_xml(title: str) -> str | None:
    """Last revision's text for a title, scanning the dump its sidecar names."""
    xml_dir = HARVEST / "xml"
    for titles_file in sorted(xml_dir.glob("*.titles")):
        listed = titles_file.read_text(encoding="utf-8").splitlines()
        if title not in listed:
            continue
        dump = titles_file.with_suffix(".xml")
        ns = "{http://www.mediawiki.org/xml/export-0.11/}"
        text = None
        for _, elem in ET.iterparse(dump, events=("end",)):
            if elem.tag == f"{ns}page":
                t = elem.findtext(f"{ns}title")
                if t == title:
                    revs = elem.findall(f"{ns}revision")
                    if revs:
                        text = revs[-1].findtext(f"{ns}text")
                    elem.clear()
                    return text
                elem.clear()
    return None


# --- conversion --------------------------------------------------------------

RAWHTML = re.compile(r"<html>(.*?)</html>", re.S | re.I)


def protect_rawhtml(wikitext: str) -> tuple[str, list[str]]:
    blocks: list[str] = []

    def repl(m):
        blocks.append(m.group(1).strip())
        return f"\n\nRAWHTMLBLOCK{len(blocks) - 1}ENDRAWHTML\n\n"

    return RAWHTML.sub(repl, wikitext), blocks


def pandoc(text: str, fmt: str = "mediawiki") -> str:
    proc = subprocess.run(
        ["pandoc", "-f", fmt, "-t", "gfm"],
        input=text,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if proc.returncode != 0:
        raise RuntimeError(f"pandoc failed: {proc.stderr.strip()}")
    return proc.stdout


def restore_rawhtml(md: str, blocks: list[str]) -> str:
    for i, block in enumerate(blocks):
        md = md.replace(f"RAWHTMLBLOCK{i}ENDRAWHTML", block)
    return md


# --- rendered-HTML fallback (for pages pandoc's wikitext reader can't parse) --

EDITSECTION = re.compile(r'<span class="mw-editsection">.*?</span>', re.S)
HTML_COMMENT = re.compile(r"<!--.*?-->", re.S)
# Internal links in the HTML track are root-relative (/Underscored_Title) or
# absolute wiki URLs; media is an absolute S3 URL. Normalize both so the common
# post-processor (wikilink anchors + bare filenames) can resolve them.
S3URL = re.compile(
    r'https?://wikiworks-esip-images\.s3\.amazonaws\.com/[^\s)"\'<>]+'
)
MDLINK = re.compile(r'(?<!!)\[([^\]]*)\]\(([^)\s]+)\)')


def s3_to_name(url: str) -> str:
    """Original upload filename behind an S3 URL (drops thumbnail 'NNNpx-' wrappers)."""
    from urllib.parse import urlparse

    parts = unquote(urlparse(url).path).strip("/").split("/")
    last = parts[-1]
    if re.match(r"\d+px-", last) and len(parts) >= 2:
        return parts[-2]  # .../15/Name.png/300px-Name.png -> Name.png
    return last


def html_path_for(title: str, manifest: dict) -> Path | None:
    entry = manifest.get(title)
    if not entry:
        return None
    rel = entry["path"]
    if rel.endswith(".wiki"):
        rel = rel[: -len(".wiki")] + ".html"
    path = HARVEST / "html" / rel
    return path if path.exists() else None


def convert_from_html(title: str, manifest: dict) -> str | None:
    path = html_path_for(title, manifest)
    if path is None:
        return None
    frag = path.read_text(encoding="utf-8")
    frag = EDITSECTION.sub("", frag)
    frag = HTML_COMMENT.sub("", frag)
    md = pandoc(frag, fmt="html")
    md = S3URL.sub(lambda m: s3_to_name(m.group(0)), md)

    def to_wikilink(m: re.Match) -> str:
        label, target = m.group(1), html.unescape(m.group(2))
        if target.startswith("/"):
            t = target[1:]
        elif target.startswith(LIVE):
            t = target[len(LIVE):]
        else:
            return m.group(0)  # a real external link, or already files/<name>
        return f'<a href="{t}" class="wikilink">{label}</a>'

    return MDLINK.sub(to_wikilink, md)


# Pandoc renders every internal wiki link as <a ... class="wikilink">...</a>,
# file embeds as a Markdown image ![alt](Name "title") or an <img>/<embed>
# src="Name" inside a <figure>, and leaves {{magic words}} it cannot expand.
ANCHOR = re.compile(r'<a\s+([^>]*?)>(.*?)</a>', re.S)
HREF = re.compile(r'href="([^"]*)"')
IMG_MD = re.compile(r'!\[([^\]]*)\]\(([^)\s]+)(?:\s+"([^"]*)")?\)')
SRC_ATTR = re.compile(r'(<(?:img|embed)\b[^>]*?\bsrc=")([^"]+)("[^>]*/?>)', re.I)
MAGIC = re.compile(r"\{\{[^{}]*\}\}")
IMAGE_EXT = {".png", ".jpg", ".jpeg", ".gif", ".svg", ".tif", ".tiff", ".webp", ".bmp"}


def has_scheme(s: str) -> bool:
    return bool(re.match(r"[a-z][a-z0-9+.-]*:", s, re.I)) or s.startswith(("/", "#", "files/"))


class Resolver:
    def __init__(self, slugmap, filemap, current_title, referenced_files, external):
        self.slugmap = slugmap
        self.filemap = filemap
        self.current = current_title
        self.referenced = referenced_files
        self.external = external

    def file_local(self, name: str) -> str | None:
        """On-disk local filename for an upload name, or None; records the hit."""
        name = html.unescape(name).strip()
        if ":" in name.split("/")[0]:  # strip a File:/Image:/Media: prefix
            name = name.split(":", 1)[1].strip()
        local = (
            self.filemap.get(name)
            or self.filemap.get(name.replace(" ", "_"))
            or self.filemap.get(norm_title(name))
        )
        if local:
            self.referenced.add(local)
        return local

    def resolve(self, raw_href: str):
        """Resolve a wikilink href -> ('local'|'file'|'external'|'drop', value)."""
        href = html.unescape(raw_href).split("#", 1)[0]
        target = unquote(href).strip()
        if "{{" in target:  # an unexpanded magic word leaked into a link
            return ("drop", None)
        low = target.lower()
        if low.startswith("category:"):
            return ("drop", None)
        if low.startswith(("media:", "file:", "image:")):
            local = self.file_local(target)
            if local:
                return ("file", f"files/{local}")
            name = target.split(":", 1)[1].strip()
            return ("external", LIVE + name.replace(" ", "_"))
        if low.startswith("special:"):
            return ("external", LIVE + target.replace(" ", "_"))
        if target.startswith("/"):
            target = f"{self.current}/{target[1:]}"
        norm = norm_title(target)
        if norm in self.slugmap:
            return ("local", f"{self.slugmap[norm]}.md")
        return ("external", LIVE + norm.replace(" ", "_"))

    def sub_anchor(self, m: re.Match) -> str:
        attrs, label = m.group(1), m.group(2)
        if "wikilink" not in attrs:
            return m.group(0)
        href_m = HREF.search(attrs)
        if not href_m:
            return label
        kind, value = self.resolve(href_m.group(1))
        if kind == "drop":
            return ""
        if kind == "external":
            self.external.append(
                {"from": self.current, "label": re.sub(r"\s+", " ", label).strip(),
                 "target": value}
            )
        return f"[{label.strip()}]({value})"

    def sub_img_md(self, m: re.Match) -> str:
        alt, target, title = m.group(1), m.group(2), m.group(3)
        if has_scheme(target):
            return m.group(0)
        local = self.file_local(target)
        if not local:
            return m.group(0)
        if Path(local).suffix.lower() in IMAGE_EXT:
            tt = f' "{title}"' if title else ""
            return f"![{alt}](files/{local}{tt})"
        text = (title or alt or local).strip()
        return f"[{text}](files/{local})"  # non-image media -> download link

    def sub_src(self, m: re.Match) -> str:
        pre, src, post = m.group(1), m.group(2), m.group(3)
        if has_scheme(src):
            return m.group(0)
        local = self.file_local(src)
        return f"{pre}files/{local}{post}" if local else m.group(0)


def rewrite(md: str, resolver: Resolver) -> str:
    md = IMG_MD.sub(resolver.sub_img_md, md)
    md = SRC_ATTR.sub(resolver.sub_src, md)
    md = ANCHOR.sub(resolver.sub_anchor, md)
    md = MAGIC.sub("", md)  # drop any remaining unexpanded {{magic words}}
    return md


# --- page emission -----------------------------------------------------------


def banner(title: str) -> str:
    url = LIVE + norm_title(title).replace(" ", "_")
    return (
        f'<div class="wiki-archive-note" markdown="span">'
        f"Archived from the ESIP wiki page "
        f'<a href="{url}">{html.escape(title)}</a>.'
        f"</div>\n\n"
    )


def render_page(title, manifest):
    """Markdown body for a title (no link rewriting yet), or None if no content."""
    wikitext = wikitext_for(title, manifest)
    source = "wikitext"
    if wikitext is None:  # no current revision; fall back to the full-history XML
        wikitext = wikitext_from_xml(title)
        source = "xml"
    if wikitext is None:
        log(f"  SKIP (no content): {title}")
        return None
    try:
        protected, blocks = protect_rawhtml(wikitext)
        return restore_rawhtml(pandoc(protected), blocks), source
    except RuntimeError as e:
        # pandoc's mediawiki reader chokes on some constructs (e.g. a heading
        # inside a table); the rendered-HTML track already parsed them cleanly.
        md = convert_from_html(title, manifest)
        if md is None:
            log(f"  SKIP (pandoc failed, no HTML track): {title} -- {e}")
            return None
        return md, source + "->html"


def emit_page(title, raw_md, slug, slugmap, filemap, referenced, external):
    resolver = Resolver(slugmap, filemap, title, referenced, external)
    md = rewrite(raw_md, resolver)
    out = DOCS / ("index.md" if slug == "interoperability-and-technology" else f"{slug}.md")
    front = f"---\ntitle: {json.dumps(title)}\n---\n\n"
    out.write_text(f"{front}# {title}\n\n{banner(title)}{md.strip()}\n", encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", help="semicolon-separated titles to convert (pilot)")
    args = ap.parse_args()

    if not HARVEST.exists():
        log(f"harvest not found at {HARVEST}; clone esip_wiki as a sibling repo")
        return 1

    # The curated worklist decides which articles are re-hosted locally; links to
    # any other title route to the live wiki and land in external-links.json.
    articles = load_included_articles()
    filemap = build_filemap()
    manifest = load_manifest()
    targets = (
        [t.strip() for t in args.only.split(";") if t.strip()] if args.only else articles
    )

    DOCS.mkdir(exist_ok=True)
    FILES_OUT.mkdir(exist_ok=True)
    referenced: set[str] = set()
    external: list[dict] = []

    # Phase 1: convert bodies. Only pages that actually produce content go into
    # the slug map, so inbound links to content-less pages (e.g. redirects) fall
    # through to the live wiki instead of dangling.
    log(f"converting {len(targets)} page(s)")
    rendered = {}
    for title in targets:
        result = render_page(title, manifest)
        if result is not None:
            rendered[title] = result

    slugmap = build_slugmap(list(rendered))

    # Phase 2: rewrite links against the final slug map and write the pages.
    for title, (raw_md, source) in rendered.items():
        slug = slugmap[norm_title(title)]
        emit_page(title, raw_md, slug, slugmap, filemap, referenced, external)
        log(f"  wrote {slug}.md (from {source})")

    # Copy only the attachments the converted pages actually reference.
    copied = 0
    for local in sorted(referenced):
        src = HARVEST / "files" / local
        if src.exists():
            shutil.copy2(src, FILES_OUT / local)
            copied += 1
        else:
            log(f"  MISSING attachment on disk: {local}")
    log(f"copied {copied} attachment(s) into {FILES_OUT.relative_to(REPO)}")

    (TOOLS / "slugmap.json").write_text(
        json.dumps(slugmap, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    (TOOLS / "external-links.json").write_text(
        json.dumps(external, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    log(f"logged {len(external)} external link(s) to tools/external-links.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
