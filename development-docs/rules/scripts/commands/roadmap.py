"""ledger roadmap create — Create a new roadmap file."""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

from scripts.lib.common import file_timestamp, iso_timestamp, now_local, to_kebab

_TEMPLATE = """\
# Roadmap — {scope}

Created: {date}

## Current Phase

## Milestones

## Backlog Items

## Notes
"""


def _active_roadmap_files(roadmap_dir: Path) -> list[Path]:
    results = []
    for f in roadmap_dir.iterdir():
        if f.is_dir():
            continue
        name = f.name.lower()
        if name in ("readme.md",) or "template" in name:
            continue
        if f.suffix == ".md" and f.name.startswith("roadmap_"):
            results.append(f)
    results.sort(key=lambda p: p.name)
    return results


def run(args: argparse.Namespace) -> int:
    base = Path(args.base_dir)
    roadmap_dir = base / "project" / "roadmap"
    archives_dir = roadmap_dir / "archives"

    if not roadmap_dir.is_dir():
        print(f"Error: roadmap directory not found: {roadmap_dir}", file=sys.stderr)
        return 1

    scope = to_kebab(args.scope)
    if not scope:
        print("Error: --scope must be a non-empty string", file=sys.stderr)
        return 1

    now = now_local()
    ts_file = file_timestamp(now)
    ts_iso = iso_timestamp(now)

    # Archive existing active roadmaps
    archives_dir.mkdir(parents=True, exist_ok=True)
    for existing in _active_roadmap_files(roadmap_dir):
        dest = archives_dir / existing.name
        shutil.move(str(existing), str(dest))
        print(f"Archived: {dest}")

    filename = f"roadmap_{ts_file}_{scope}.md"
    filepath = roadmap_dir / filename
    content = _TEMPLATE.format(scope=scope, date=ts_iso)
    filepath.write_text(content, encoding="utf-8")
    print(f"Created: {filepath}")

    return 0
