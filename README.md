# ESIP IT&I Committee

The ESIP Information Technology and Interoperability (IT&I) committee is a standing ESIP committee focused on ESIP community-wide IT interoperability topics. The committee convenes monthly conversations on topics of broad interest in an effort to provide a venue for continuity and coordination of IT&I topics between ESIP January and July meetings. 

This github is the committee's home to track historical and ongoing activities.

The current content is **phase one**: a [readable archive of the committee's
content migrated from the ESIP MediaWiki](https://esipfed.github.io/itandi-committee/)
 — its governance, the Tech Dive and
Rants & Raves webinar series, telecons and meeting notes, the technical
workshops it ran, and its demonstrations (32 pages). Pages outside this curated
set link back to the live wiki at <https://wiki.esipfed.org/>.

## Building the site

```sh
pip install -r requirements.txt
mkdocs serve          # preview at http://127.0.0.1:8000
```

GitHub Pages builds and deploys `docs/` automatically on every push to `main`
(see `.github/workflows/pages.yml`).

## Regenerating the archive

The Markdown in `docs/` is generated from the `esip_wiki` harvest, which is not
committed here. To rebuild it, check out `esip_wiki` as a sibling directory,
install [pandoc](https://pandoc.org/), and run:

```sh
python tools/convert.py
```

Which pages are re-hosted is controlled by `tools/scope.tsv`. See `AGENTS.md`
for how the conversion works.
