#!/usr/bin/env python3
"""Build Vitae's professional knowledge graph, APIs, and static knowledge site.

All inputs are object-per-file JSON-compatible YAML in ``content/`` plus the
canonical BibTeX bibliography.  This module is deliberately dependency-free so
the public site and machine-readable archive can be rebuilt anywhere Python is
available.
"""
from __future__ import annotations

import argparse
import csv
import html
import json
import re
import shutil
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "content"
GRAPH = ROOT / "dashboard"
SITE = ROOT / "site"
PUBLICATIONS = ROOT / "publications" / "publications.yaml"

OBJECT_DIRECTORIES = (
    "person", "employers", "roles", "projects", "products", "software",
    "talks", "training", "grants", "awards", "patents", "technologies",
    "institutions", "countries", "domains", "customers", "mentors", "students",
)
RELATION_KEYS = {
    "employer", "employers", "roles", "projects", "products", "software",
    "publications", "talks", "training", "technologies", "institutions",
    "countries", "customers", "mentors", "students", "grants", "awards",
    "patents", "domains",
}
ROUTES = {
    "career": ("Career", {"Role", "Employer"}),
    "projects": ("Projects", {"Project"}),
    "products": ("Products", {"Product", "Software"}),
    "software": ("Software", {"Software", "Product"}),
    "publications": ("Publications", {"Publication"}),
    "teaching": ("Teaching", {"Talk", "Training Course"}),
}


def write(path: Path, value: str | dict | list) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(value, (dict, list)):
        value = json.dumps(value, indent=2, ensure_ascii=False) + "\n"
    path.write_text(value)


def slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")


def text(value: object) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        return " ".join(text(item) for item in value)
    if isinstance(value, dict):
        return " ".join(text(item) for item in value.values())
    return str(value or "")


def title(record: dict) -> str:
    return str(record.get("name") or record.get("title") or record.get("description") or record["id"])


def summary(record: dict) -> str:
    return str(record.get("summary") or record.get("description") or record.get("solution") or "")


def object_path(record: dict) -> str:
    return f"/objects/{record['id']}/"


def load_objects() -> list[dict]:
    records: list[dict] = []
    for directory in OBJECT_DIRECTORIES:
        path = CONTENT / directory
        if not path.exists():
            continue
        for file in sorted(path.glob("*.yaml")):
            item = json.loads(file.read_text())
            item.setdefault("id", file.stem)
            item.setdefault("type", directory.rstrip("s").replace("training", "Training Course").title())
            item["source"] = file.relative_to(ROOT).as_posix()
            records.append(item)

    if PUBLICATIONS.exists():
        source = json.loads(PUBLICATIONS.read_text())
        for publication in source["records"]:
            records.append({
                "id": publication["id"], "type": "Publication", "name": publication["title"],
                "year": publication["year"], "journal": publication["journal"],
                "summary": "; ".join(publication.get("category", [])),
                "authors": publication.get("authors", ""), "doi": publication.get("doi", ""),
                "relationships": {
                    "products": publication.get("projects", []),
                    "technologies": publication.get("technologies", []),
                },
                "source": "content/publications.bib",
            })
    return records


def normalize(records: list[dict]) -> tuple[list[dict], list[dict], list[dict]]:
    ids: set[str] = set()
    aliases: dict[str, str] = {}
    errors: list[dict] = []
    for record in records:
        if record["id"] in ids:
            errors.append({"kind": "duplicate_id", "id": record["id"], "source": record["source"]})
        ids.add(record["id"])
        aliases[record["id"]] = record["id"]
        for alias in record.get("aliases", []):
            aliases[alias] = record["id"]

    edges: list[dict] = []
    for record in records:
        relationship_map = dict(record.get("relationships", {}))
        for key in RELATION_KEYS:
            if key in record:
                relationship_map[key] = record[key]
        normalized: dict[str, list[str]] = {}
        for key, values in relationship_map.items():
            if key not in RELATION_KEYS:
                continue
            if not isinstance(values, list):
                values = [values]
            targets: list[str] = []
            for raw in values:
                raw = str(raw)
                target = aliases.get(raw, aliases.get(slug(raw), raw))
                if target in ids:
                    targets.append(target)
                    edges.append({"source": record["id"], "target": target, "kind": key})
                else:
                    errors.append({"kind": "unresolved_relationship", "source": record["id"], "relationship": key, "target": raw})
            if targets:
                normalized[key] = sorted(set(targets))
        record["relationships"] = normalized
        record["search_text"] = text({k: v for k, v in record.items() if k not in {"source", "relationships"}}).lower()
    return records, edges, errors


def linked_by(records: list[dict], edges: list[dict]) -> dict[str, list[dict]]:
    by_id = {record["id"]: record for record in records}
    result: dict[str, list[dict]] = defaultdict(list)
    for edge in edges:
        result[edge["target"]].append({"id": edge["source"], "kind": edge["kind"], "name": title(by_id[edge["source"]]), "type": by_id[edge["source"]]["type"]})
    return {key: sorted(value, key=lambda item: (item["type"], item["name"])) for key, value in result.items()}


def nav() -> str:
    return "".join(f'<a href="/{path}/">{label}</a>' for path, (label, _) in ROUTES.items()) + '<a href="/timeline/">Timeline</a><a href="/dashboard/">Dashboard</a><a href="/relationships/">Relationships</a><a href="/search/">Search</a>'


def page(title_text: str, body: str, description: str = "") -> str:
    description = html.escape(description or "Professional knowledge platform generated from structured, version-controlled data.")
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="description" content="{description}"><title>{html.escape(title_text)} | Vitae</title><link rel="stylesheet" href="/platform.css"></head>
<body><header class="site-header"><a class="mark" href="/">Vitae</a><nav>{nav()}</nav></header><main>{body}</main>
<footer>Generated from structured, version-controlled professional data. <a href="/api/index.json">API</a> <a href="/feed.xml">RSS</a></footer></body></html>'''


def card(record: dict, prefix: str = "") -> str:
    period = f'<p class="meta">{html.escape(str(record["period"]))}</p>' if record.get("period") else ""
    year = f'<p class="meta">{html.escape(str(record["year"]))}</p>' if record.get("year") else ""
    return f'''<article class="card"><p class="kind">{html.escape(record["type"])}{year}</p>
<h2><a href="{prefix}{object_path(record)}">{html.escape(title(record))}</a></h2>{period}<p>{html.escape(summary(record))}</p></article>'''


def home(records: list[dict], counts: Counter) -> str:
    featured = [record for record in records if record["type"] in {"Product", "Project", "Role"}][:9]
    stats = "".join(f'<li><strong>{count}</strong><span>{html.escape(kind)}</span></li>' for kind, count in sorted(counts.items()))
    return page("Vitae", f'''<section class="hero"><p class="eyebrow">Open professional knowledge platform</p><h1>A professional life, represented as knowledge.</h1><p class="lede">Vitae generates documents, a website, dashboards and machine-readable APIs from one structured, version-controlled knowledge base.</p><p><a class="button" href="/search/">Explore the knowledge base</a></p></section>
<section><h2>Professional record</h2><ul class="stats">{stats}</ul></section><section><h2>Selected connections</h2><div class="grid">{''.join(card(record) for record in featured)}</div></section>''')


def route_page(route: str, records: list[dict]) -> str:
    label, accepted = ROUTES[route]
    selected = [record for record in records if record["type"] in accepted]
    if route == "software":
        selected = [record for record in selected if record["type"] == "Software" or record.get("technologies") or record.get("solution")]
    if route == "publications":
        selected.sort(key=lambda record: (-int(record.get("year", 0)), title(record)))
    elif route == "career":
        selected.sort(key=lambda record: title(record))
    return page(label, f'<section class="page-intro"><p class="eyebrow">Knowledge view</p><h1>{label}</h1><p class="lede">A generated view over the same professional knowledge base.</p></section><section class="grid">{"".join(card(record) for record in selected)}</section>')


def object_page(record: dict, by_id: dict[str, dict], inverse: dict[str, list[dict]]) -> str:
    relationship_cards: list[str] = []
    for kind, ids in record["relationships"].items():
        links = ", ".join(f'<a href="{object_path(by_id[item])}">{html.escape(title(by_id[item]))}</a>' for item in ids)
        relationship_cards.append(f'<li><strong>{html.escape(kind.replace("_", " ").title())}</strong><span>{links}</span></li>')
    related = inverse.get(record["id"], [])
    incoming = ", ".join(f'<a href="{object_path(by_id[item["id"]])}">{html.escape(item["name"])}</a>' for item in related)
    details = []
    for key in ("problem", "scientific_context", "solution", "design_decisions", "impact", "future_evolution", "achievements"):
        value = record.get(key)
        if value:
            rendered = "<ul>" + "".join(f"<li>{html.escape(str(item))}</li>" for item in value) + "</ul>" if isinstance(value, list) else f"<p>{html.escape(str(value))}</p>"
            details.append(f'<section><h2>{html.escape(key.replace("_", " ").title())}</h2>{rendered}</section>')
    provenance = f'<p class="meta">Source: {html.escape(record["source"])}</p>'
    return page(title(record), f'''<section class="page-intro"><p class="eyebrow">{html.escape(record["type"])}</p><h1>{html.escape(title(record))}</h1><p class="lede">{html.escape(summary(record))}</p>{provenance}</section>{''.join(details)}
<section><h2>Relationships</h2><ul class="relationship-list">{''.join(relationship_cards) or '<li>No explicit outgoing relationships yet.</li>'}</ul></section>
<section><h2>Referenced by</h2><p>{incoming or 'No incoming relationships yet.'}</p></section>''')


def timeline_page(publications: list[dict]) -> str:
    counts = Counter(int(record.get("year", 0)) for record in publications if record.get("year"))
    rows = "".join(f"<tr><td>{year}</td><td>{count}</td></tr>" for year, count in sorted(counts.items()))
    return page("Timeline", f'<section class="page-intro"><p class="eyebrow">Career evolution</p><h1>Publication timeline</h1><p class="lede">A deterministic annual view generated from the canonical BibTeX bibliography.</p></section><section><table><thead><tr><th>Year</th><th>Publications</th></tr></thead><tbody>{rows}</tbody></table></section>')


def relationships_page(edges: list[dict], by_id: dict[str, dict]) -> str:
    rows = "".join(f'<li><a href="{object_path(by_id[edge["source"]])}">{html.escape(title(by_id[edge["source"]]))}</a><span>{html.escape(edge["kind"].replace("_", " "))}</span><a href="{object_path(by_id[edge["target"]])}">{html.escape(title(by_id[edge["target"]]))}</a></li>' for edge in edges)
    return page("Relationships", f'<section class="page-intro"><p class="eyebrow">Knowledge graph</p><h1>Explicit relationships</h1><p class="lede">Every displayed relationship resolves to stable object identifiers and is available through the API.</p></section><section><ul class="edge-list">{rows}</ul></section>')


def search_page(records: list[dict]) -> str:
    rows = "".join(f'<li data-search="{html.escape(record["search_text"])}"><a href="{object_path(record)}">{html.escape(title(record))}</a><span>{html.escape(record["type"])}</span></li>' for record in records)
    script = """<script>const q=document.querySelector('#q'),r=[...document.querySelectorAll('[data-search]')];q.addEventListener('input',()=>{const v=q.value.toLowerCase();r.forEach(x=>x.hidden=!x.dataset.search.includes(v))})</script>"""
    return page("Search", f'<section class="page-intro"><p class="eyebrow">Query the record</p><h1>Search</h1><input id="q" type="search" placeholder="Search publications, projects, products, roles, talks or technologies" autofocus></section><section><ul class="search-results">{rows}</ul></section>{script}')


def analytics(records: list[dict], edges: list[dict]) -> dict:
    by_id = {record["id"]: record for record in records}
    country_rules = {"United Kingdom": "United Kingdom", "Germany": "Germany", "Finland": "Finland", "Malaysia": "Malaysia", "Australia": "Australia", "Singapore": "Singapore", "India": "India", "Asia-Pacific": "Asia-Pacific", "Brisbane": "Australia", "Munich": "Germany", "Turku": "Finland", "Kuala Lumpur": "Malaysia"}
    country_counts: Counter = Counter()
    for employer in (record for record in records if record["type"] == "Employer"):
        for location in employer.get("locations", []):
            for needle, country in country_rules.items():
                if needle.lower() in str(location).lower():
                    country_counts[country] += 1
    technology_counts: Counter = Counter()
    for edge in edges:
        target = by_id[edge["target"]]
        if target["type"] == "Technology":
            technology_counts[title(target)] += 1
    coauthors: Counter = Counter()
    for publication in (record for record in records if record["type"] == "Publication"):
        for author in re.split(r"\s+and\s+", publication.get("authors", "")):
            author = author.strip()
            if author and "Rudd" not in author:
                coauthors[author] += 1
    role_records = [record for record in records if record["type"] == "Role"]
    organisation_edges = [edge for edge in edges if by_id[edge["source"]]["type"] == "Role" and by_id[edge["target"]]["type"] == "Employer"]
    project_ids = {record["id"] for record in records if record["type"] == "Project"}
    project_edges = [edge for edge in edges if edge["source"] in project_ids or edge["target"] in project_ids]
    return {
        "country_map": [{"country": country, "connections": count} for country, count in sorted(country_counts.items())],
        "technology_evolution": [{"technology": name, "connections": count} for name, count in technology_counts.most_common()],
        "coauthor_graph": {"nodes": [{"name": name, "publication_count": count} for name, count in coauthors.most_common()], "focal_author": "Stephen Rudd"},
        "organisation_graph": organisation_edges,
        "project_graph": project_edges,
        "career_evolution": [{"role": record.get("title", ""), "period": record.get("period", ""), "employer": record.get("employer", "")} for record in role_records],
    }


def dashboard_page(counts: Counter, analysis: dict) -> str:
    countries = "".join(f'<li><strong>{html.escape(item["country"])}</strong><span>{item["connections"]} connections</span></li>' for item in analysis["country_map"])
    technologies = "".join(f'<li><strong>{html.escape(item["technology"])}</strong><span>{item["connections"]} relationships</span></li>' for item in analysis["technology_evolution"])
    return page("Dashboard", f'''<section class="page-intro"><p class="eyebrow">Generated analytics</p><h1>Professional knowledge dashboard</h1><p class="lede">Career, technology, organisation, project and publication views generated from explicit relationships.</p></section>
<section class="grid"><article class="card"><p class="kind">Knowledge graph</p><h2>{sum(counts.values())} objects</h2><p>All records resolve through stable identifiers.</p></article><article class="card"><p class="kind">Countries</p><h2>{len(analysis["country_map"])} represented</h2><p>Derived from employer locations.</p></article><article class="card"><p class="kind">Co-authors</p><h2>{len(analysis["coauthor_graph"]["nodes"])} connected</h2><p>Derived from the canonical bibliography.</p></article></section>
<section class="split"><article><h2>Country map data</h2><ul class="search-results">{countries}</ul></article><article><h2>Technology evolution</h2><ul class="search-results">{technologies}</ul></article></section>
<section><h2>Machine-readable dashboards</h2><p><a href="/api/dashboard/country-map.json">Country map</a> · <a href="/api/dashboard/technology-evolution.json">Technology evolution</a> · <a href="/api/dashboard/coauthor-graph.json">Co-author graph</a> · <a href="/api/dashboard/organisation-graph.json">Organisation graph</a> · <a href="/api/dashboard/project-graph.json">Project graph</a> · <a href="/api/dashboard/career-evolution.json">Career evolution</a></p></section>''')


def css() -> str:
    return '''@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600&family=Libertinus+Serif:ital,wght@0,400;0,600;1,400&display=swap');
:root{--blue:#12263a;--accent:#38647a;--ink:#17202a;--muted:#607080;--line:#d8e0e5;--paper:#f5f7f7}*{box-sizing:border-box}body{margin:0;color:var(--ink);font:16px/1.55 'IBM Plex Sans',sans-serif;background:#fff}.site-header{max-width:1240px;margin:auto;padding:1.2rem 2rem;display:flex;align-items:center;justify-content:space-between;border-bottom:1px solid var(--line)}.mark{font-weight:600;color:var(--blue);text-decoration:none;letter-spacing:.08em;text-transform:uppercase}.site-header nav{display:flex;gap:1.15rem;flex-wrap:wrap;justify-content:flex-end}.site-header nav a,footer a{color:var(--accent);text-decoration:none;font-size:.85rem}main{max-width:1240px;margin:auto;padding:0 2rem 5rem}.hero,.page-intro{padding:7rem 0 4rem;max-width:900px}.eyebrow,.kind,.meta{font-size:.78rem;letter-spacing:.08em;text-transform:uppercase;color:var(--accent)}h1,h2{color:var(--blue);line-height:1.1}h1{font:400 clamp(2.8rem,7vw,6rem)/.94 'Libertinus Serif',serif;letter-spacing:-.025em;margin:.6rem 0 1.4rem}h2{font-size:1.35rem;margin:0 0 .65rem}.lede{font:400 1.3rem/1.55 'Libertinus Serif',serif;max-width:760px}.button{display:inline-block;padding:.7rem 1rem;background:var(--blue);color:#fff;text-decoration:none;font-weight:600}.grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));border-top:1px solid var(--line)}.split{display:grid;grid-template-columns:1fr 1fr;gap:3rem}.card{padding:1.5rem 1.5rem 1.5rem 0;border-bottom:1px solid var(--line)}.card:nth-child(3n+2),.card:nth-child(3n+3){padding-left:1.5rem;border-left:1px solid var(--line)}.card h2 a{color:inherit;text-decoration:none}.card p{margin:.35rem 0;color:var(--muted)}.kind{margin:0 0 .35rem}.stats{display:flex;flex-wrap:wrap;gap:1px;padding:0;margin:0;list-style:none;background:var(--line)}.stats li{padding:1.2rem;min-width:120px;flex:1;background:#fff}.stats strong{display:block;font-size:1.8rem;color:var(--blue)}.stats span{color:var(--muted);font-size:.85rem}.relationship-list,.edge-list,.search-results{list-style:none;padding:0}.relationship-list li{display:grid;grid-template-columns:190px 1fr;gap:1rem;padding:.8rem 0;border-bottom:1px solid var(--line)}.relationship-list a,.edge-list a,.search-results a{color:var(--accent)}.edge-list li,.search-results li{display:flex;gap:.65rem;padding:.7rem 0;border-bottom:1px solid var(--line)}.edge-list span,.search-results span{color:var(--muted);font-size:.85rem}input{width:100%;padding:1rem;border:1px solid var(--line);font:inherit}table{width:100%;border-collapse:collapse}th,td{text-align:left;padding:.8rem;border-bottom:1px solid var(--line)}footer{padding:2rem;max-width:1240px;margin:auto;border-top:1px solid var(--line);color:var(--muted);font-size:.85rem}@media(max-width:760px){.site-header{align-items:flex-start;gap:1rem;flex-direction:column;padding:1rem}.site-header nav{gap:.8rem;justify-content:flex-start}main{padding:0 1rem 3rem}.hero,.page-intro{padding:4rem 0 2.5rem}.grid,.split{display:block}.card,.card:nth-child(3n+2),.card:nth-child(3n+3){padding:1.25rem 0;border-left:0}.relationship-list li{display:block}.relationship-list span{display:block;margin-top:.25rem}.edge-list li{display:block}.edge-list span{display:block;margin:.2rem 0}}'''


def json_resume(records: list[dict]) -> dict:
    person = next((record for record in records if record["type"] == "Person"), {})
    roles = [record for record in records if record["type"] == "Role"]
    return {"basics": {"name": title(person), "label": person.get("professional_title", ""), "location": {"address": person.get("location", "")}, "profiles": person.get("profiles", [])}, "work": [{"name": record.get("employer", ""), "position": record.get("title", ""), "summary": record.get("summary", ""), "highlights": record.get("achievements", [])} for record in roles], "publications": [{"name": title(record), "releaseDate": str(record.get("year", "")), "publisher": record.get("journal", ""), "url": f"https://doi.org/{record['doi']}" if record.get("doi") else ""} for record in records if record["type"] == "Publication"]}


def dashboard_pdfs(counts: Counter, timeline: list[dict], edges: list[dict]) -> None:
    """Create archival dashboard PDFs when the optional reporting runtime exists."""
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
        from reportlab.lib.units import mm
        from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
    except ImportError:
        return
    output = ROOT / "output"
    output.mkdir(exist_ok=True)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("DashboardTitle", parent=styles["Title"], textColor=colors.HexColor("#12263A"), fontName="Helvetica-Bold")
    body_style = ParagraphStyle("DashboardBody", parent=styles["BodyText"], leading=14)

    def build_pdf(filename: str, heading: str, introduction: str, rows: list[list[str]]) -> None:
        table = Table(rows, colWidths=[85 * mm, 75 * mm], repeatRows=1)
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#12263A")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#D8E0E5")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F5F7F7")]),
            ("LEFTPADDING", (0, 0), (-1, -1), 8), ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ("TOPPADDING", (0, 0), (-1, -1), 7), ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ]))
        story = [Paragraph(heading, title_style), Spacer(1, 6 * mm), Paragraph(introduction, body_style), Spacer(1, 8 * mm), table]
        SimpleDocTemplate(str(output / filename), pagesize=A4, rightMargin=20 * mm, leftMargin=20 * mm, topMargin=20 * mm, bottomMargin=20 * mm, title=heading, author="Vitae").build(story)

    build_pdf("career_dashboard.pdf", "Career dashboard", "A reproducible summary generated from the Vitae professional knowledge graph.", [["Object type", "Count"], *[[kind, str(count)] for kind, count in sorted(counts.items())], ["Explicit relationships", str(len(edges))]])
    build_pdf("career_timeline.pdf", "Career timeline", "Annual publication activity generated from the canonical BibTeX bibliography.", [["Year", "Publications"], *[[str(item["year"]), str(item["publication_count"])] for item in timeline]])
    product_count = sum(1 for edge in edges if edge["kind"] in {"products", "software"})
    build_pdf("software_dashboard.pdf", "Software dashboard", "Relationships connecting products and software to the wider professional record.", [["Measure", "Count"], ["Product and software objects", str(counts.get("Product", 0) + counts.get("Software", 0))], ["Product and software relationships", str(product_count)], ["All explicit relationships", str(len(edges))]])


def build() -> None:
    records = load_objects()
    records, edges, errors = normalize(records)
    by_id = {record["id"]: record for record in records}
    inverse = linked_by(records, edges)
    counts = Counter(record["type"] for record in records)
    publications = [record for record in records if record["type"] == "Publication"]
    graph = {"schema_version": 2, "generated": date.today().isoformat(), "nodes": records, "edges": edges, "validation": {"errors": errors, "object_count": len(records), "edge_count": len(edges)}}
    write(GRAPH / "knowledge_graph.json", graph)
    write(GRAPH / "search.json", [{"id": record["id"], "type": record["type"], "name": title(record), "summary": summary(record), "path": object_path(record), "search_text": record["search_text"]} for record in records])
    timeline = [{"year": year, "publication_count": count} for year, count in sorted(Counter(record.get("year") for record in publications if record.get("year")).items())]
    analysis = analytics(records, edges)
    write(GRAPH / "timeline.json", timeline)
    with (GRAPH / "timeline.csv").open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=["year", "publication_count"], lineterminator="\n")
        writer.writeheader(); writer.writerows(timeline)
    write(GRAPH / "career_dashboard.json", {"schema_version": 2, "objects": dict(sorted(counts.items())), "relationships": len(edges), "validation_errors": len(errors), "timeline": timeline})
    for name, payload in analysis.items():
        write(GRAPH / f"{name}.json", payload)
    dashboard_pdfs(counts, timeline, edges)

    shutil.rmtree(SITE / "api", ignore_errors=True)
    write(SITE / "platform.css", css())
    write(SITE / "index.html", home(records, counts))
    for route in ROUTES:
        write(SITE / route / "index.html", route_page(route, records))
    write(SITE / "timeline" / "index.html", timeline_page(publications))
    write(SITE / "dashboard" / "index.html", dashboard_page(counts, analysis))
    write(SITE / "relationships" / "index.html", relationships_page(edges, by_id))
    write(SITE / "search" / "index.html", search_page(records))
    for record in records:
        write(SITE / "objects" / record["id"] / "index.html", object_page(record, by_id, inverse))
        payload = dict(record); payload["referenced_by"] = inverse.get(record["id"], [])
        write(SITE / "api" / "objects" / f"{record['id']}.json", payload)
    write(SITE / "api" / "index.json", {"schema_version": 2, "endpoints": {"objects": "/api/objects/{id}.json", "search": "/api/search.json", "relationships": "/api/relationships.json", "json_resume": "/api/json-resume.json"}, "object_count": len(records), "relationship_count": len(edges)})
    write(SITE / "api" / "search.json", json.loads((GRAPH / "search.json").read_text()))
    write(SITE / "api" / "relationships.json", edges)
    for name, payload in analysis.items():
        write(SITE / "api" / "dashboard" / f"{name.replace('_', '-')}.json", payload)
    write(SITE / "api" / "json-resume.json", json_resume(records))
    write(SITE / "api" / "linkedin-snippets.json", {"headline": next((record.get("professional_title") for record in records if record["type"] == "Person"), ""), "roles": [{"title": record.get("title", ""), "summary": summary(record)} for record in records if record["type"] == "Role"]})
    feed_items = "".join(f'<item><title>{html.escape(title(record))}</title><link>{object_path(record)}</link><description>{html.escape(summary(record))}</description></item>' for record in records[:30])
    write(SITE / "feed.xml", f'<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel><title>Vitae professional knowledge base</title><link>/</link><description>Structured professional knowledge</description>{feed_items}</channel></rss>')
    print(f"Built platform with {len(records)} objects, {len(edges)} relationships, and {len(errors)} unresolved references.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the Vitae professional knowledge platform.")
    parser.add_argument("--check", action="store_true", help="Fail when object IDs or relationship targets are invalid.")
    args = parser.parse_args()
    build()
    report = json.loads((GRAPH / "knowledge_graph.json").read_text())["validation"]["errors"]
    if args.check and report:
        raise SystemExit(f"Knowledge graph validation failed with {len(report)} issue(s).")


if __name__ == "__main__":
    main()
