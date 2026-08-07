# Contributing

Corrections and improvements are welcome.

1. Add or correct facts in the appropriate `content/<type>/<id>.yaml` record; use relationship IDs instead of copied names or prose.
2. Add publications only to `content/publications.bib` and product case-study prose only to `products/`.
3. Run `make platform-check`, then `make platform`.
4. Run `make pdf` and `make verify`; visually inspect rendered pages with `make render` after a layout change.
5. Keep claims factual, concise and outcome-led. Do not introduce duplicated prose into `src/` or edit generated outputs.

Use conventional, focused commits. Publication corrections should include a DOI or other primary source where possible.

## Tailored documents

Keep the canonical career record unchanged. Create a new composition file in `src/` that selects existing generated fragments, then add it to `DOCS` in the Makefile. This retains the shared design system and prevents recruiter-specific prose from drifting into the master portfolio.

## Publications, employers and talks

Add a BibTeX entry with a DOI where available; bibliography pages and publication objects are rendered automatically. Add employers, roles, talks and training as their own records with explicit relationships. Rebuild the platform after each factual change.
