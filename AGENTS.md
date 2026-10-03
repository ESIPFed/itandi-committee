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

The raw material for phase may live in a sibling repository, `esip_wiki` (at `../esip_wiki` in a normal checkout layout). That repository harvested the full ESIP wiki to disk — wikitext, full-history XML, rendered HTML, and attachments — and drew the IT&I scope as an explicit boundary of 211 titles (113 articles plus the files, categories, and templates they depend on), recorded in its `iti-titles.txt` and `iti-scope.json`. It is the source; this repository is the published archive. A MediaWiki title is not a filename there, and the mapping is not one to one: read its `manifest.json` and `files-index.json` to go from a file back to its page, rather than reconstructing titles from paths. Read that repository's `CONTEXT.md` before relying on any harvest detail.

## Current state

Phase one is starting from an effectively empty repository — this file and a stub README. The archive content, the Pages build, and the curation decisions about what belongs in a permanent archive are not yet in place.
