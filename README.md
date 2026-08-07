# Vitae - professional knowledge platform

Vitae is an open-source, structured representation of a professional life. Stephen Rudd's record is the reference implementation; the platform is designed so a scientist, engineer or research-software leader can generate publication-quality documents, a website, dashboards and machine-readable APIs from one version-controlled knowledge base.

The executive CV is one view. The primary record is object-per-file professional data in `content/`, with explicit, queryable relationships between roles, employers, projects, products, technologies, talks, training and publications.

## Build

The only host requirements are Docker with Compose and GNU Make.

```bash
make pdf
```

Outputs are written to `output/`:

- `Executive_CV.pdf` - two-page executive CV
- `Executive_Portfolio.pdf` - six-page leadership portfolio
- `Executive_Biography.pdf` - one-page biography
- `Cover_Letter_Template.pdf` - one-page adaptable letter

The command runs LuaLaTeX through `latexmk` inside a pinned TeX Live container. No local TeX installation is used.

Other focused commands are available: `make cv`, `make portfolio`, `make biography`, `make website`, `make publications`, `make knowledge`, `make dashboard`, `make talks`, `make timeline`, `make docker`, `make verify`, `make render` and `make clean`. `make release VERSION=v2026.1` builds, tags and pushes a semantic release; the release workflow attaches the PDFs automatically.

`make publications-enrich` refreshes a dated, reviewable cache of Crossref, OpenAlex and Semantic Scholar metrics; it never changes the canonical BibTeX. `make publications-orcid` downloads a public ORCID works inventory when an `orcid` value has been added to the Person record (or is passed to `scripts/sync_orcid.py --orcid`).

## Platform build

```bash
make platform-check
make platform
```

This produces a responsive website with career, projects, products, software, publications, teaching, timeline, relationship and search views. It also emits a queryable knowledge graph, full-text search index, object APIs, JSON Resume, LinkedIn snippets, RSS feed and archival dashboard PDFs.

The portable command-line entry point is available as `bin/vitae`:

```bash
bin/vitae validate
bin/vitae build
bin/vitae init ../my-professional-record
```

## Architecture

```text
content/<object-type>/*.yaml object-per-file professional knowledge graph
content/publications.bib   canonical bibliography
content/profile.json       legacy compatibility adapter for current PDF compositions
products/*.md              canonical product case-study prose
dashboard/                 generated knowledge graph, search index and dashboards
scripts/build_knowledge_graph.py graph, API and static platform builder
scripts/generate.py        adapters for existing LaTeX compositions
style/vitae.cls            shared design system and environments
src/*.tex                  document composition only
build/generated/           generated LaTeX fragments (ignored)
site/                      generated GitHub Pages site (ignored)
output/                    final PDFs (ignored except release assets)
```

## Editing

Add professional facts as object records in `content/<object-type>/`; add references to `content/publications.bib`; add rich product narratives in `products/`; and change presentation in `style/vitae.cls`. See [CONTENT_GUIDE.md](CONTENT_GUIDE.md) and [CONTRIBUTING.md](CONTRIBUTING.md) for the workflow.

For the model and publishing workflow, read [SCHEMA.md](SCHEMA.md), [ARCHITECTURE.md](ARCHITECTURE.md), [CONTENT_GUIDE.md](CONTENT_GUIDE.md), [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md) and [PUBLISHING_GUIDE.md](PUBLISHING_GUIDE.md).

## GitHub Pages

The workflow in `.github/workflows/pages.yml` regenerates and publishes the platform from the same content model on every push to `main`.

## Licensing

Portfolio content is licensed under CC BY 4.0. Build scripts and helper utilities are MIT licensed. See `LICENSES/`.
