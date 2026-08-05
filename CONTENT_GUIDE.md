# Content guide

Add an employer, role, product, project, talk, training course, or technology as one JSON-compatible YAML file in `content/<type>/`. Give it a stable lowercase `id`, a `type`, the object’s own facts, and relationship IDs. Do not copy employer names or product descriptions into related objects.

Run `make knowledge` after adding objects. Add scholarly records only to `content/publications.bib`, then run `make publications`.
