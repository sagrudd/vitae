# Content guide

Add one fact once. Put it in the object that owns it, then link to it elsewhere by ID.

For example, an EPI2ME talk belongs in `content/talks/`; it links to `epi2me` and `nextflow`. Do not repeat the talk description in the product or technology record. The graph will create the reverse links automatically.

1. Create `content/<type>/<id>.yaml` using JSON-compatible YAML.
2. Give the record a stable lowercase `id`, a `type`, a human-readable `name` or `title`, and explicit relationship IDs.
3. Put scholarly metadata only in `content/publications.bib`.
4. Run `make platform-check`.
5. Run `make platform` to generate the website, APIs and graph.

Use product fields to explain the scientific problem, context, solution, decisions and impact. Use project records for time-bounded or collaborative programmes. Use role records for appointments. Use talks and training records independently: a workshop is not merely a bullet in a role.

`content/profile.json` and `products/*.md` remain compatibility inputs for existing PDF compositions. New information belongs in object records. Do not edit `site/`, `dashboard/`, `build/`, `output/` or `publications/` derived files.
