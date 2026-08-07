# Publishing guide

`make platform` produces the static website, object pages, JSON APIs, JSON Resume, LinkedIn snippets, search index, graph, timeline and RSS feed. `make pdf` creates publication-quality document artifacts. Both commands are deterministic for a fixed repository revision.

The GitHub Pages workflow invokes `make website`, which now runs the same platform build. A release should publish the generated PDFs alongside the static `site/` directory, dashboard JSON, BibTeX and API files.

Before publishing:

1. Run `make platform-check` and resolve every relationship error.
2. Run `make platform` and inspect the primary pages locally.
3. Run `make pdf`, `make verify` and render PDFs after a typography change.
4. Tag the exact revision that generated the archive.

The RSS feed and all APIs are static files, so they are suitable for long-term archival and for future AI or research-information-system integrations.

## Publication integrations

The bibliography is authoritative; external services only provide a dated metrics cache. Run `make publications-enrich` to retrieve Crossref, OpenAlex and Semantic Scholar counts after `scripts/import_publications.py` has refreshed the catalogue. Review the resulting diff before retaining it. An optional `scripts/sync_orcid.py --orcid <iD>` writes the public ORCID works response to `dashboard/orcid_sync.json`; it is an import queue for review, never an automatic bibliography overwrite.
