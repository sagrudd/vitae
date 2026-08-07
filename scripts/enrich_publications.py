#!/usr/bin/env python3
"""Fetch non-authoritative publication metrics without changing bibliography facts.

The BibTeX file remains the scholarly source of record.  This command adds a
dated `metrics` cache to the generated publication catalogue after it has been
imported.  Failed providers are recorded per publication; a temporary API
failure never makes a platform build fail.
"""
from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path
from urllib.error import URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
CATALOGUE = ROOT / "publications" / "publications.yaml"
DEFAULT_PROVIDERS = ("crossref", "openalex", "semantic_scholar")


def fetch(url: str) -> dict | None:
    try:
        request = Request(url, headers={"User-Agent": "vitae-publications/1.0 (scholarly archive)"})
        with urlopen(request, timeout=12) as response:
            return json.load(response)
    except (URLError, TimeoutError, ValueError, OSError):
        return None


def metric(provider: str, doi: str) -> dict | None:
    encoded = quote(doi, safe="")
    if provider == "crossref":
        data = fetch(f"https://api.crossref.org/works/{encoded}")
        message = data.get("message", {}) if data else {}
        return {"citations": message.get("is-referenced-by-count"), "url": f"https://doi.org/{doi}"} if data else None
    if provider == "openalex":
        data = fetch(f"https://api.openalex.org/works/https://doi.org/{doi}")
        return {"citations": data.get("cited_by_count"), "open_access": bool(data.get("open_access", {}).get("is_oa"))} if data else None
    if provider == "semantic_scholar":
        data = fetch(f"https://api.semanticscholar.org/graph/v1/paper/DOI:{encoded}?fields=citationCount")
        return {"citations": data.get("citationCount")} if data else None
    raise ValueError(f"Unknown provider: {provider}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--providers", default=",".join(DEFAULT_PROVIDERS), help="Comma-separated providers")
    args = parser.parse_args()
    providers = tuple(item.strip() for item in args.providers.split(",") if item.strip())
    unknown = sorted(set(providers) - set(DEFAULT_PROVIDERS))
    if unknown:
        parser.error("Unknown provider(s): " + ", ".join(unknown))

    payload = json.loads(CATALOGUE.read_text())
    refreshed_at = datetime.now(UTC).isoformat(timespec="seconds")
    updated = 0
    for record in payload["records"]:
        doi = record.get("doi")
        if not doi:
            continue
        metrics = record.setdefault("metrics", {})
        for provider in providers:
            result = metric(provider, doi)
            metrics[provider] = {"checked_at": refreshed_at, **(result or {"status": "unavailable"})}
            updated += bool(result)
        # Preserve the familiar display field while retaining every provider's result.
        preferred = metrics.get("openalex") or metrics.get("crossref") or metrics.get("semantic_scholar")
        if preferred and "citations" in preferred:
            record["citations"] = preferred["citations"]
            record["citation_source"] = "OpenAlex" if "openalex" in metrics and "citations" in metrics["openalex"] else "Crossref"
    payload["metrics_refreshed_at"] = refreshed_at
    payload["metric_providers"] = list(providers)
    CATALOGUE.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")
    print(f"Retrieved {updated} provider records; unavailable services were retained as status data.")


if __name__ == "__main__":
    main()
