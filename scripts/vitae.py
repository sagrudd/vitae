#!/usr/bin/env python3
"""Small, dependency-free command line interface for the Vitae platform."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OBJECT_TYPES = ("person", "employers", "roles", "projects", "products", "software", "publications", "talks", "teaching", "training", "grants", "awards", "patents", "technologies", "institutions", "countries", "customers", "mentors", "students")


def run(*command: str) -> None:
    subprocess.run(command, cwd=ROOT, check=True)


def initialise(destination: Path) -> None:
    destination = destination.resolve()
    if destination.exists() and any(destination.iterdir()):
        raise SystemExit(f"Refusing to initialise non-empty directory: {destination}")
    for kind in OBJECT_TYPES:
        (destination / "content" / kind).mkdir(parents=True, exist_ok=True)
    (destination / "content" / "person" / "person.yaml").write_text(json.dumps({"id": "your_name", "type": "Person", "name": "Your Name", "professional_title": "Your field", "relationships": {}}, indent=2) + "\n")
    (destination / "content" / "publications.bib").write_text("% Add BibTeX records here.\n")
    (destination / "README.md").write_text("# Vitae professional knowledge base\n\nRun `vitae build` after adding structured objects.\n")
    print(f"Initialised Vitae knowledge base in {destination}")


def main() -> None:
    parser = argparse.ArgumentParser(prog="vitae", description="Build a professional knowledge platform from structured records.")
    parser.add_argument("--version", action="version", version="vitae 0.2")
    commands = parser.add_subparsers(dest="command", required=True)
    init = commands.add_parser("init", help="create a reusable object-per-file knowledge base")
    init.add_argument("directory", type=Path)
    commands.add_parser("build", help="build website, APIs, graph and publication views")
    commands.add_parser("validate", help="validate all relationship identifiers")
    commands.add_parser("api", help="build machine-readable API projections")
    args = parser.parse_args()
    if args.command == "init":
        initialise(args.directory)
    elif args.command in {"build", "api"}:
        run("make", "platform")
    elif args.command == "validate":
        run("make", "platform-check")


if __name__ == "__main__":
    main()
