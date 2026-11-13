# ESIP IT&I Committee

## **Website: <https://esipfed.github.io/itandi-committee/>**

The ESIP Information Technology and Interoperability (IT&I) committee is a standing ESIP committee focused on ESIP community-wide IT interoperability topics. The committee convenes monthly conversations on topics of broad interest in an effort to provide a venue for continuity and coordination of IT&I topics between ESIP January and July meetings. 

This github is the committee's home to track historical and ongoing activities.

The [committee website](https://esipfed.github.io/itandi-committee/) has three parts:

- **[Home](https://esipfed.github.io/itandi-committee/)** — what the committee
  does, its meeting format, and how to get involved.
- **[Meetings](https://esipfed.github.io/itandi-committee/meetings/)** — short
  summaries of recent monthly meetings, newest first.
- **[Wiki Archive](https://esipfed.github.io/itandi-committee/wiki-archive/)** —
  a readable archive of the committee's content migrated from the ESIP MediaWiki:
  its governance, the Tech Dive and Rants & Raves webinar series, telecons and
  meeting notes, the technical workshops it ran, and its demonstrations (32
  pages). Pages outside this curated set link back to the live wiki at
  <https://wiki.esipfed.org/>.

Have a question about an IT interoperability topic? Open a
[discussion](https://github.com/ESIPFed/itandi-committee/discussions). Have an
idea for a meeting topic? Record it as an
[issue](https://github.com/ESIPFed/itandi-committee/issues).

## Building the site

```sh
pip install -r requirements.txt
mkdocs serve          # preview at http://127.0.0.1:8000/itandi-committee/
```

GitHub Pages builds and deploys `docs/` automatically on every push to `main`
(see `.github/workflows/pages.yml`).

The home page (`docs/index.md`) and the Meetings page (`docs/meetings.md`) are
written by hand. Add new pages to the `nav:` in `mkdocs.yml` outside the
`# NAV` markers.

## Regenerating the archive

The Wiki Archive pages in `docs/` are generated from the `esip_wiki` harvest,
which is not committed here. To rebuild them, check out `esip_wiki` as a sibling
directory, install [pandoc](https://pandoc.org/), and run:

```sh
python tools/convert.py
```

Which pages are re-hosted is controlled by `tools/scope.tsv`. See `AGENTS.md`
for how the conversion works.
