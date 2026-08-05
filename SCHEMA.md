# Professional knowledge graph

The repository is a personal CRIS and document-publishing system. Object files in `content/<type>/` are JSON-compatible YAML, one object per file. Their `id` values are stable relationship keys; an object references another object only by key, never by copied prose.

## Object types

`Employer`, `Role`, `Project`, `Product`, `Publication`, `Talk`, `Training Course`, and `Technology` are supported now. Future `Grant`, `Award`, `Patent`, `Customer`, `Institution`, and `Country` records use the same shape: `id`, `type`, human-readable fields, and `relationships`.

```yaml
{
  "id": "ep i2me",
  "type": "Product",
  "name": "EPI2ME",
  "technologies": ["nextflow", "genomics"],
  "employers": ["oxford_nanopore_technologies"]
}
```

## Pipeline

`content/profile.json` and `content/publications.bib` remain backwards-compatible inputs. `make knowledge` bootstraps object files on its first run, then builds `dashboard/knowledge_graph.json`, a universal `dashboard/search.json`, timeline views, career analytics and website pages. `make publications` produces bibliography derivatives. `make pdf` retains the existing document outputs.

Add an object by copying the shape above into the appropriate `content/<type>/` directory, then run `make knowledge`. Never edit `dashboard/`, `site/`, or generated publication files by hand.
