# Architecture

Vitae is a structured professional knowledge platform. PDFs are projections, not the database.

```text
content/*.yaml + content/publications.bib
                 |
                 +--> publication importer --> derived publication records
                 |
                 +--> graph builder --> dashboard JSON, search index, APIs, RSS
                 |                     --> static website and object pages
                 |
                 +--> document adapters --> LaTeX fragments --> PDFs
```

The graph builder is dependency-free Python. It normalises object relationships, resolves aliases, derives reverse links and refuses unresolved relationship IDs in `--check` mode. Its outputs are deterministic for the same content tree.

`make platform` is the complete static publishing path. It imports the canonical BibTeX bibliography, curates derived publication views, generates legacy document fragments, and builds the knowledge graph, APIs and website. GitHub Pages runs this same target.

The `bin/vitae` command exposes the portable platform workflow:

```bash
vitae init my-profile
vitae validate
vitae build
```

The reference implementation is Stephen Rudd's record, but object types, graph IDs, templates and generated views are not tied to any individual.
