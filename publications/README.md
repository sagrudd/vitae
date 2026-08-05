# Publications knowledge base

This directory is a generated scholarly archive for Stephen Rudd. The sole source of publication facts is [`../content/publications.bib`](../content/publications.bib). Do not hand-edit generated records here.

## Build

Run `make publications` for a Docker-only import, classification, dashboard, timeline and catalogue build. Run `make publications-metrics` when an online best-effort refresh of OpenAlex citation counts and open-access metadata is wanted. Neither unavailable network services nor missing optional metadata fail the archive build.

## Generated record

- `publications.yaml` is JSON-compatible YAML containing all structured fields and the raw BibTeX provenance.
- `bibliography.bib`, `publications.json`, `publications.csv`, and `publications.md` are complete bibliographic views.
- `selected.yaml`, `executive_publications.tex`, `complete_publications.tex`, and `career_contributions.tex` are document-ready selections.
- `software.yaml`, `databases.yaml`, `reviews.yaml`, `methods.yaml`, `products.yaml`, and `scientific_contributions.yaml` are classification views.
- `publication_dashboard.*` and `publication_timeline.*` are presentation views; PDFs are written to `output/`.

The import records any exact duplicate DOI/title/year merge in `publications.yaml`. `verify_dois.py` checks required identity fields, DOI syntax, and duplicates.
