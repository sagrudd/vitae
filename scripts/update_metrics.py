#!/usr/bin/env python3
"""Refresh best-effort metrics, then rebuild dashboard derivatives."""
from pathlib import Path
import subprocess
ROOT=Path(__file__).resolve().parents[1]
subprocess.run(["python3", str(ROOT/"scripts"/"enrich_publications.py")], check=False)
subprocess.run(["python3", str(ROOT/"scripts"/"build_dashboard.py")], check=True)
