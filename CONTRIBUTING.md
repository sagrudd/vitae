# Contributing

Corrections and improvements are welcome.

1. Edit career material in `content/profile.json`, publications in `content/publications.bib`, talks in the `talks` list, and product case studies in `products/`.
2. Run `make pdf` and confirm all four files are produced.
3. Run `make verify` to check page counts, metadata, and PDF text.
4. Visually inspect rendered pages with `make render`.
5. Keep claims factual, concise, and outcome-led. Do not introduce duplicated prose into `src/`.

Use conventional, focused commits. Publication corrections should include a DOI or other primary source where possible.

## Tailored documents

Keep the canonical career record unchanged. Create a new composition file in `src/` that selects existing generated fragments, then add it to `DOCS` in the Makefile. This retains the shared design system and prevents recruiter-specific prose from drifting into the master portfolio.

## Publications, employers and talks

Add a BibTeX entry with a DOI where available; bibliography pages are rendered automatically by Biber. Add employers to the `experience` array in reverse chronology with a concise chapter summary and achievement-led bullets. Add talks as plain entries in the `talks` array. Rebuild all PDFs after each factual change.
