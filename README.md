# Stephen Rudd - Executive Portfolio

A reproducible, publication-quality portfolio for senior computational biology, bioinformatics product, and scientific software leadership roles.

The repository is deliberately structured like a software product: one canonical content model drives four PDFs and a static website, while typography, composition, and build tooling remain independent.

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

`make website` regenerates the static site in `site/`.

## Architecture

```text
content/profile.json       canonical narrative and career data
content/publications.bib   canonical bibliography
scripts/generate.py        adapters for LaTeX and HTML
style/vitae.cls            shared design system and environments
src/*.tex                  document composition only
build/generated/           generated LaTeX fragments (ignored)
site/                      generated GitHub Pages site (ignored)
output/                    final PDFs (ignored except release assets)
```

## Editing

Change facts and prose in `content/profile.json`; change references in `content/publications.bib`; change presentation in `style/vitae.cls`. See [CONTRIBUTING.md](CONTRIBUTING.md) for checks and publication guidance.

## GitHub Pages

The workflow in `.github/workflows/pages.yml` regenerates and publishes the website from the same content model on every push to `main`.

## Licensing

Portfolio content is licensed under CC BY 4.0. Build scripts and helper utilities are MIT licensed. See `LICENSES/`.
