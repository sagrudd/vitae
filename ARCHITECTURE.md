# Architecture

The repository keeps facts, presentation, and generated outputs separate. Legacy canonical inputs (`content/profile.json`, `content/publications.bib`, and product Markdown) remain valid. The knowledge-graph layer adds normalized object records in `content/` and emits the dashboard, universal search index, website extensions, and structured APIs.

`make knowledge` runs in Docker, builds `dashboard/knowledge_graph.json`, and publishes site-compatible pages. `make publications` derives bibliography views. `make pdf` builds the executive document set. Generated directories are outputs, not editing surfaces.
