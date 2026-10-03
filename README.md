# ESIP IT&I Committee

Home of the ESIP Information Technology & Interoperability (IT&I) Committee on
GitHub, served as a GitHub Pages site: <https://esipfed.github.io/itandi-committee/>.

The current content is **phase one**: a readable archive of the committee's
content migrated from the ESIP MediaWiki — its governance, the Tech Dive and
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
