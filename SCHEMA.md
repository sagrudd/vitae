# Vitae schema

Vitae represents a professional life as a graph of stable, object-per-file records. JSON-compatible YAML is used so the platform has no runtime YAML dependency. A record belongs in `content/<type>/<id>.yaml`; its filename and `id` should agree.

Every object has:

```json
{
  "id": "stable_lowercase_identifier",
  "type": "Product",
  "name": "Human-readable name",
  "relationships": {"technologies": ["nextflow"]}
}
```

Relationship values are stable object IDs, never copied names or prose. The build derives reverse links, graph edges, search documents, website pages, APIs and document views. `make platform-check` fails if an ID is duplicated or a relationship cannot be resolved.

Supported object directories are `person`, `employers`, `roles`, `projects`, `products`, `software`, `talks`, `teaching`, `training`, `grants`, `awards`, `patents`, `technologies`, `institutions`, `countries`, `domains`, `customers`, `mentors` and `students`. Empty directories are valid: absence of a grant record is not a placeholder for one.

Products may use the following optional fields:

```json
{
  "problem": "The scientific or operational problem.",
  "scientific_context": "Why the problem matters.",
  "solution": "What was built or delivered.",
  "design_decisions": ["Decision and rationale."],
  "impact": "Observed outcome or durable value.",
  "future_evolution": "Current direction, where appropriate."
}
```

Publications remain canonical BibTeX in `content/publications.bib`. The importer creates publication objects only as a derived view; do not hand-edit `publications/` or `dashboard/`.

## Views

Views select objects and relationships; they do not create a second source of truth. The platform currently emits an executive CV, portfolio, biography, cover letter, publication views, website, JSON Resume, LinkedIn snippets, searchable APIs, dashboards, timeline and RSS feed. Additional document templates should be compositions over the same IDs.
