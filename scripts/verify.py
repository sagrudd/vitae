#!/usr/bin/env python3
"""Fail the build when required PDFs, page counts, or essential text are wrong."""
import re
import shutil
import subprocess
import sys
from pathlib import Path

directory = Path(sys.argv[1])
expected = {"Executive_CV.pdf": 2, "Executive_Portfolio.pdf": 6, "Executive_Biography.pdf": 1, "Cover_Letter_Template.pdf": 1}
errors = []
for filename, pages in expected.items():
    path = directory / filename
    if not path.exists() or path.stat().st_size < 10_000:
        errors.append(f"{filename}: missing or unexpectedly small")
        continue
    if shutil.which("pdfinfo"):
        info = subprocess.check_output(["pdfinfo", str(path)], text=True)
        match = re.search(r"^Pages:\s+(\d+)", info, re.M)
        actual = int(match.group(1)) if match else -1
    else:
        from pypdf import PdfReader
        actual = len(PdfReader(str(path)).pages)
    if actual != pages:
        errors.append(f"{filename}: expected {pages} page(s), found {actual}")
    if shutil.which("pdftotext"):
        text = subprocess.check_output(["pdftotext", str(path), "-"], text=True)
    else:
        from pypdf import PdfReader
        text = "\n".join(page.extract_text() or "" for page in PdfReader(str(path)).pages)
    if "Stephen Rudd" not in text or len(text.strip()) < 300:
        errors.append(f"{filename}: essential text missing")
if errors:
    raise SystemExit("PDF verification failed:\n- " + "\n- ".join(errors))
print("Verified four PDFs: page counts, file sizes, and essential text are valid.")
