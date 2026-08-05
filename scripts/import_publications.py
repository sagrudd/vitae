#!/usr/bin/env python3
"""Build the publications knowledge base from the canonical BibTeX source.

This importer deliberately has no third-party dependency.  It retains the raw
BibTeX record, emits JSON-compatible YAML, and makes every derived file
repeatable from content/publications.bib.
"""
from __future__ import annotations

import csv
import json
import re
import shutil
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "content" / "publications.bib"
OUT = ROOT / "publications"

PRODUCTS = {
    "sputnik": ("Sputnik", "Comparative plant-genomics data needed a durable integration layer.", "A database platform for comparative plant genomics."),
    "opensputnik": ("openSputnik", "Unsaturated EST collections were difficult to compare and reuse.", "An EST-oriented comparative plant-genomics database."),
    "plantmarkers": ("PlantMarkers", "Plant molecular-marker discovery was fragmented.", "A database of predicted molecular markers from plants."),
    "eclair": ("Eclair", "Mixed host-interface sequence samples obscure organismal origin.", "A web service to separate sampled sequence origins."),
    "mips": ("MIPS", "Genome and protein annotation required integrated reference resources.", "A genome and protein-sequence database resource."),
    "arabidopsis": ("Arabidopsis Genome", "The first plant genome needed a reusable community reference.", "Genome analysis and biological knowledge resources for Arabidopsis."),
    "mygenome": ("MyGenome", "Personal genome interpretation requires an accessible product layer.", "Genome interpretation resource contribution."),
}

HIGH_IMPACT = {"Nature", "Cell", "Genome Research", "Cancer Research", "PLOS Pathogens", "PLOS Computational Biology"}


def clean(value: str) -> str:
    value = re.sub(r"[{}]", "", value or "")
    return re.sub(r"\s+", " ", value).strip()


def parse_bib(text: str) -> list[dict]:
    records, start, depth = [], None, 0
    for index, char in enumerate(text):
        if text.startswith("@", index) and start is None:
            start, depth = index, 0
        if start is not None:
            depth += char == "{"
            depth -= char == "}"
            if depth == 0 and char == "}":
                block = text[start:index + 1]
                start = None
                header = re.match(r"@(\w+)\s*\{\s*([^,]+),", block, re.S)
                if not header:
                    continue
                fields = {"entry_type": header.group(1), "key": header.group(2).strip(), "raw_bibtex": block.strip()}
                body = block[header.end():-1]
                pos = 0
                while pos < len(body):
                    match = re.search(r"([\w-]+)\s*=\s*\{", body[pos:], re.S)
                    if not match:
                        break
                    name = match.group(1).lower()
                    open_at = pos + match.end() - 1
                    level, close_at = 0, open_at
                    for close_at in range(open_at, len(body)):
                        level += body[close_at] == "{"
                        level -= body[close_at] == "}"
                        if level == 0:
                            break
                    fields[name] = clean(body[open_at + 1:close_at])
                    pos = close_at + 1
                records.append(fields)
    return records


def categories(title: str, journal: str) -> list[str]:
    blob = f"{title} {journal}".lower()
    rules = [
        ("Genome Resources", r"genome|genomic|chromosome"), ("Comparative Genomics", r"comparative|mapping"),
        ("Transcriptomics", r"transcript|rna|expressed sequence|est"), ("Cancer Genomics", r"cancer|mesothelioma"),
        ("Clinical Genomics", r"clinical|patient|renal|diabetes|intellectual disability"),
        ("Population Genomics", r"population|polymorphism|snp"), ("Metagenomics", r"metagenom|microbiome"),
        ("Plant Genomics", r"plant|arabidopsis|barley|maize|cassava|rye|gerbera|ginkgo|cycas|solanum|populus|spruce"),
        ("Bioinformatics Infrastructure", r"bioinformatics|platform|web service"), ("Bioinformatics Databases", r"database|datdb"),
        ("Software", r"software|web service|sputnik|eclair"), ("Methods", r"method|analysis|screen|profiling|clustering|machine|support vector"),
        ("Machine Learning", r"machine|support vector|clustering"), ("Reviews", r"review|perspective|alternative or complement"),
        ("Resources", r"resource|library|dataset|collection"), ("Long-read Sequencing", r"long-read|nanopore"),
    ]
    found = [name for name, pattern in rules if re.search(pattern, blob)]
    return found or ["Other"]


def phase(year: int) -> tuple[str, str]:
    if year <= 2002: return "Genome-era resources", "MIPS / Munich"
    if year <= 2007: return "Comparative genomics", "MIPS / Munich"
    if year <= 2013: return "Applied transcriptomics", "International collaborations"
    return "Clinical and data science", "Australia / industry"


def role(authors: str) -> tuple[bool, bool, bool]:
    parts = [clean(item) for item in re.split(r"\s+and\s+", authors)]
    rudd = [i for i, part in enumerate(parts) if re.search(r"\bRudd\b", part, re.I)]
    consortium = bool(re.search(r"consortium|initiative|institute", authors, re.I))
    return (bool(rudd and rudd[0] == 0), bool(rudd and rudd[-1] == len(parts) - 1), consortium)


def enrich(record: dict) -> dict:
    title, journal, year = record.get("title", ""), record.get("journal", ""), int(record.get("year", 0) or 0)
    first, senior, consortium = role(record.get("author", ""))
    matches = [slug for slug in PRODUCTS if slug in title.lower()]
    cats = categories(title, journal)
    is_database = any(c in cats for c in ["Bioinformatics Databases", "Bioinformatics Infrastructure"])
    is_software = "Software" in cats
    is_method = "Methods" in cats or "Machine Learning" in cats
    is_review = "Reviews" in cats
    career_phase, institution = phase(year)
    return {
        "id": record["key"], "title": title, "year": year, "journal": journal,
        "volume": record.get("volume", ""), "issue": record.get("number", ""), "pages": record.get("pages", ""),
        "doi": record.get("doi", "").lower(), "pmid": record.get("pmid", ""), "url": f"https://doi.org/{record['doi']}" if record.get("doi") else "",
        "publication_type": record.get("entry_type", "article"), "category": cats, "role": "first author" if first else ("senior author" if senior else "contributor"),
        "first_author": first, "corresponding_author": False, "consortium": consortium, "software": is_software, "database": is_database,
        "methods": is_method, "review": is_review, "open_access": journal.startswith(("BMC", "PLOS", "Genome Biology")),
        "impact_factor": None, "citations": None, "citation_source": "not yet enriched", "abstract": "", "keywords": cats,
        "organisations": [institution], "employers": [institution], "projects": matches, "technologies": ["genomics"] + (["bioinformatics"] if is_database or is_software else []),
        "notes": record.get("note", ""), "authors": record.get("author", ""), "career_phase": career_phase, "raw_bibtex": record["raw_bibtex"],
    }


def dump_json_yaml(path: Path, data: object) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")


def bibliography_markdown(records: list[dict]) -> str:
    lines = ["# Complete publications", "", "Generated from `content/publications.bib`; do not edit this file manually.", ""]
    for r in sorted(records, key=lambda x: (-x["year"], x["title"])):
        doi = f" [DOI](https://doi.org/{r['doi']})" if r["doi"] else ""
        lines.append(f"- {r['authors']} ({r['year']}). *{r['title']}*. {r['journal']} {r['volume']} ({r['issue']}), {r['pages']}.{doi}")
    return "\n".join(lines) + "\n"


def tex_entries(records: list[dict], title: str) -> str:
    keys = ",".join(r["id"] for r in records)
    return f"% Generated by scripts/import_publications.py - do not edit.\n% {title}\n\\nocite{{{keys}}}\n"


def main() -> None:
    OUT.mkdir(exist_ok=True)
    raw = SOURCE.read_text()
    parsed = parse_bib(raw)
    seen, duplicate_keys, unique = {}, [], []
    for item in parsed:
        identity = (item.get("doi", "").lower(), clean(item.get("title", "")).lower(), item.get("year", ""))
        if identity in seen:
            duplicate_keys.append({"kept": seen[identity], "merged": item["key"], "reason": "matching DOI/title/year"})
        else:
            seen[identity] = item["key"]; unique.append(item)
    records = [enrich(item) for item in unique]
    records.sort(key=lambda r: (r["year"], r["id"]))
    selected = sorted(records, key=lambda r: (not (r["first_author"] or r["software"] or r["database"] or r["consortium"]), -r["year"], r["id"]))
    executive, portfolio = selected[:6], selected[:15]
    products = []
    for slug, (name, problem, contribution) in PRODUCTS.items():
        linked = [r["id"] for r in records if slug in " ".join([r["title"], " ".join(r["projects"])]).lower()]
        if linked:
            products.append({"name": name, "problem": problem, "solution": contribution, "scientific_contribution": contribution, "publications": linked,
                             "associated_employers": sorted({x for r in records if r["id"] in linked for x in r["employers"]}), "associated_technologies": sorted({x for r in records if r["id"] in linked for x in r["technologies"]})})
    defining = sorted(records, key=lambda r: (not (r["first_author"] or r["software"] or r["database"] or r["consortium"] or r["journal"] in HIGH_IMPACT), -r["year"]))[:20]
    shutil.copyfile(SOURCE, OUT / "bibliography.bib")
    shutil.copyfile(SOURCE, OUT / "publications.bib")
    dump_json_yaml(OUT / "publications.yaml", {"schema_version": 1, "source": "content/publications.bib", "records": records, "duplicate_merges": duplicate_keys})
    dump_json_yaml(OUT / "selected.yaml", {"executive_cv": [r["id"] for r in executive], "executive_portfolio": [r["id"] for r in portfolio]})
    for filename, predicate in [("software.yaml", lambda r: r["software"]), ("databases.yaml", lambda r: r["database"]), ("reviews.yaml", lambda r: r["review"]), ("methods.yaml", lambda r: r["methods"])]:
        dump_json_yaml(OUT / filename, [r["id"] for r in records if predicate(r)])
    dump_json_yaml(OUT / "products.yaml", products)
    dump_json_yaml(OUT / "scientific_contributions.yaml", [{"publication": r["id"], "title": r["title"], "why_it_matters": ", ".join(r["category"])} for r in defining])
    (OUT / "publications.json").write_text(json.dumps(records, indent=2, ensure_ascii=False) + "\n")
    with (OUT / "publications.csv").open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=["id", "year", "title", "journal", "doi", "category", "role", "career_phase"], lineterminator="\n")
        writer.writeheader(); writer.writerows([{k: "; ".join(v) if isinstance(v, list) else v for k, v in r.items() if k in writer.fieldnames} for r in records])
    (OUT / "publications.md").write_text(bibliography_markdown(records))
    (OUT / "selected_publications.tex").write_text(tex_entries(executive, "Executive CV selection"))
    (OUT / "executive_publications.tex").write_text(tex_entries(executive, "Executive CV selection"))
    (OUT / "portfolio_publications.tex").write_text(tex_entries(portfolio, "Executive portfolio selection"))
    (OUT / "complete_publications.tex").write_text(tex_entries(records, "Complete publication record"))
    (OUT / "career_contributions.tex").write_text(tex_entries(defining, "Career-defining contributions"))
    print(f"Imported {len(records)} unique publications; detected {len(duplicate_keys)} duplicate records.")


if __name__ == "__main__":
    main()
