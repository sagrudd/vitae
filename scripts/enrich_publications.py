#!/usr/bin/env python3
"""Optional, failure-tolerant Crossref/OpenAlex enrichment for publication records."""
from __future__ import annotations
import json
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "publications" / "publications.yaml"

def fetch(url: str) -> dict | None:
    try:
        request = urllib.request.Request(url, headers={"User-Agent": "vitae-publications/1.0 (scholarly archive)"})
        with urllib.request.urlopen(request, timeout=8) as response:
            return json.load(response)
    except (urllib.error.URLError, TimeoutError, ValueError):
        return None

def main() -> None:
    payload=json.loads(PATH.read_text()); updated=0
    for record in payload["records"]:
        doi=record.get("doi")
        if not doi: continue
        openalex=fetch(f"https://api.openalex.org/works/https://doi.org/{doi}")
        if openalex:
            record["citations"]=openalex.get("cited_by_count")
            record["citation_source"]="OpenAlex"
            record["open_access"]=bool(openalex.get("open_access",{}).get("is_oa"))
            updated += 1
        else:
            record["citation_source"]="OpenAlex unavailable during last refresh"
    PATH.write_text(json.dumps(payload,indent=2,ensure_ascii=False)+"\n")
    print(f"Enriched {updated} records; unavailable services were recorded without failing the build.")

if __name__ == "__main__": main()
