# Repository guidance

- Treat `content/profile.json` and `content/publications.bib` as the canonical content sources.
- Never hand-edit files in `build/`, `site/`, or `output/`; they are generated.
- Preserve the separation between content (`content/`), typography (`style/`), document composition (`src/`), and build tooling (`scripts/`).
- Run `make pdf` for a clean Docker build and `make verify` for artifact checks.
- Render and inspect every PDF after material layout changes.
- Use ASCII hyphens in source prose for portable PDF text extraction.
