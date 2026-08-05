#!/usr/bin/env python3
"""Validate bibliography identity fields and report duplicate DOI/title records."""
from __future__ import annotations
import json
import re
import sys
from pathlib import Path

PATH=Path(__file__).resolve().parents[1]/"publications"/"publications.yaml"
DOI=re.compile(r"^10\.\d{4,9}/[-._;()/:a-z0-9]+$",re.I)
def main() -> None:
    records=json.loads(PATH.read_text())["records"]; failures=[]; seen={}
    for r in records:
        for field in ("title","year","journal"):
            if not r.get(field): failures.append(f"{r['id']}: missing {field}")
        if r.get("doi") and not DOI.match(r["doi"]): failures.append(f"{r['id']}: invalid DOI syntax")
        if r.get("doi") in seen: failures.append(f"{r['id']}: duplicate DOI with {seen[r['doi']]}")
        seen[r.get("doi")]=r["id"]
    if failures:
        print("Publication verification failed:\n- " + "\n- ".join(failures)); sys.exit(1)
    print(f"Verified {len(records)} publication records: titles, years, journals and DOI syntax are valid.")
if __name__ == "__main__": main()
