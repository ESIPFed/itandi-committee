# AGENTS.md — ESIP IT&I Committee repository

Operational context for AI agents working in this repository. Read it before making changes.

If you see that this document is out of sync with the repository, stop and say so.

Changes to this repository are not finished until the change is reflected here.

## What the IT&I Committee is

The Information Technology and Interoperability Committee is a standing committee of the ESIP Federation (Earth Science Information Partners). It was established to ensure that data, information, and services can be readily exchanged and integrated to improve Earth science data, information, products, and services; to encourage the use of standards and protocols relevant to interoperability; and to encourage the use of best information technology practices. Its chair sits on the ESIP Executive Committee. The committee's recurring work is the monthly Tech Dive webinar series — experts walking the community through a tool or technique in Earth science data — run alongside the USGS Community for Data Integration. The current chair is Chris Battisto.

## What this repository is for

This repository is the committee's home on GitHub, hosted as a GitHub Pages site. Its scope grows in phases, in this order:

1. **Wiki archive.** Host a durable, readable archive of the committee's twenty years of content from the ESIP MediaWiki — the first and current scope.
2. **Awesome list.** Curate an IT Interoperability awesome list.
3. **Help tracker.** Run an open IT Interoperability help issue tracker.
4. **Meetings and activities.** Curate topics for upcoming meetings and promote awareness of committee activities such as demonstrations and collaborative technology evaluations.

Work on a later phase only when the earlier ones are in place or the request names it.

## Relationship to the harvest repository

The raw material for phase one may live in a sibling repository, `esip_wiki` (at `../esip_wiki` in a normal checkout layout). That repository harvested the full ESIP wiki to disk — wikitext, full-history XML, rendered HTML, and attachments — and drew the IT&I scope as an explicit boundary of 211 titles (113 articles plus the files, categories, and templates they depend on), recorded in its `iti-titles.txt` and `iti-scope.json`. It is the source; this repository is the published archive. A MediaWiki title is not a filename there, and the mapping is not one to one: read its `manifest.json` and `files-index.json` to go from a file back to its page, rather than reconstructing titles from paths. Read that repository's `CONTEXT.md` before relying on any harvest detail.

## How the archive is built

The published archive lives in `docs/` and is served by MkDocs (Material theme), built and deployed to GitHub Pages by `.github/workflows/pages.yml` on every push to `main`. The site is a project page at `https://esipfed.github.io/itandi-committee/`.

Conversion from the harvest is a **local authoring step, not a CI step**: the `../esip_wiki/archive/` harvest (~4.5 GB) is not committed, so the workflow only builds the Markdown already in `docs/`. To regenerate the archive, run `python tools/convert.py` from the repo root with the `esip_wiki` sibling checked out and `pandoc` on the PATH. Building the site locally needs `mkdocs-material` (`pip install -r requirements.txt`, then `mkdocs serve`).

`tools/convert.py`:
- reads which pages to re-host from `tools/scope.tsv` (the curated worklist — one row per candidate article with an `include`/`exclude` decision);
- converts each page's wikitext with pandoc, falling back to the rendered-HTML track when pandoc cannot parse the wikitext, and to the full-history XML when a page has no current revision;
- rewrites internal links to local pages, resolves images and attachments into `docs/files/`, and points every out-of-archive link at the live wiki;
- writes `tools/slugmap.json` (title → page slug), `tools/external-links.json` (every link that now points back to `wiki.esipfed.org` — a worklist for when more pages are archived), and the grouped site nav into `mkdocs.yml` between the `# NAV` markers.

## Scope of the archive

The harvest bounded IT&I to 211 titles by a depth-4 link walk, but that walk reaches federation-wide and other-cluster pages the committee only linked to (the overall ESIP strategic plan, whole-meeting schedules, Federated Search / Preservation / Semantic Web topic pages, and so on). `tools/scope.tsv` narrows this to the committee's own content — its governance, the Tech Dive and Rants & Raves webinar series, telecons and meeting notes, the technical workshops it ran, and its demonstrations — currently **32 published pages** with their attachments. Everything excluded resolves to the live wiki and is logged in `tools/external-links.json`. Changing scope means editing `scope.tsv` and re-running the converter.

## Current state

Phase one is in place: 32 curated pages with their attachments under `docs/`, the MkDocs build, the Pages workflow, and the curation worklist. Enabling Pages (source: GitHub Actions) in the repository settings is a one-time manual step on github.com. Later phases — awesome list, help tracker, meetings and activities — are not started.
