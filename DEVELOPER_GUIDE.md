# Developer guide

Vitae intentionally uses Python's standard library for its core graph and static site build. Docker is required only for LaTeX PDF generation.

Run these checks before a release:

```bash
make platform-check
make platform
make pdf
make verify
```

Keep content, generation and presentation separate:

- `content/` holds canonical records and BibTeX.
- `scripts/` derives graph, APIs, static views and LaTeX fragments.
- `src/` selects document views.
- `style/` owns typography.

When adding an object type, add its directory to `OBJECT_DIRECTORIES` in `scripts/build_knowledge_graph.py`, document its fields in `SCHEMA.md`, and add a fixture record only when there is a real fact to represent. Add a relationship type only when it is stable and queryable across more than one object.

Do not introduce a database or JavaScript framework merely to render static, version-controlled knowledge. Prefer explicit IDs, portable JSON, deterministic transforms and browser-native search filtering.
