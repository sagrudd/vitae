#!/usr/bin/env python3
"""Download the public ORCID works inventory as a reviewable, non-destructive cache."""
from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
PERSON = ROOT / "content" / "person" / "stephen_rudd.yaml"
OUTPUT = ROOT / "dashboard" / "orcid_sync.json"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--orcid", help="Public ORCID iD. Overrides content/person/stephen_rudd.yaml.")
    args = parser.parse_args()
    person = json.loads(PERSON.read_text())
    orcid = args.orcid or person.get("orcid")
    if not orcid:
        print("No ORCID iD configured; nothing was downloaded. Add `orcid` to the Person record or pass --orcid.")
        return
    url = f"https://pub.orcid.org/v3.0/{orcid}/works"
    try:
        request = Request(url, headers={"Accept": "application/json", "User-Agent": "vitae-publications/1.0"})
        with urlopen(request, timeout=15) as response:
            works = json.load(response)
    except (HTTPError, URLError, TimeoutError, ValueError, OSError) as error:
        raise SystemExit(f"ORCID sync failed: {error}")
    OUTPUT.parent.mkdir(exist_ok=True)
    OUTPUT.write_text(json.dumps({"orcid": orcid, "retrieved_at": datetime.now(UTC).isoformat(timespec="seconds"), "works": works}, indent=2) + "\n")
    print(f"Saved public ORCID works inventory to {OUTPUT.relative_to(ROOT)} for review.")


if __name__ == "__main__":
    main()
