"""ledger log add — Add a development log entry."""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from pathlib import Path

from scripts.lib.common import file_timestamp, iso_timestamp, now_local


def _active_log_files(logs_dir: Path) -> list[Path]:
    results = []
    for f in logs_dir.iterdir():
        if f.is_dir():
            continue
        if f.suffix == ".md" and f.name.startswith("log_"):
            results.append(f)
    results.sort(key=lambda p: p.name)
    return results


def _count_entries(filepath: Path) -> int:
    content = filepath.read_text(encoding="utf-8")
    return len(re.findall(r"^## Entry \d+", content, re.MULTILINE))


def _create_new_log(logs_dir: Path, ts: str) -> Path:
    filename = f"log_{ts}.md"
    filepath = logs_dir / filename
    filepath.write_text(f"# Development Log — {ts}\n\n", encoding="utf-8")
    return filepath


def run(args: argparse.Namespace) -> int:
    base = Path(args.base_dir)
    logs_dir = base / "project" / "logs"
    archives_dir = logs_dir / "archives"

    if not logs_dir.is_dir():
        print(f"Error: logs directory not found: {logs_dir}", file=sys.stderr)
        return 1

    task = args.task
    author = args.author
    now = now_local()
    ts_file = file_timestamp(now)
    ts_iso = iso_timestamp(now)

    active = _active_log_files(logs_dir)

    if not active:
        log_file = _create_new_log(logs_dir, ts_file)
        print(f"Created: {log_file}")
    else:
        log_file = active[-1]

    entry_count = _count_entries(log_file)
    max_entries = 20

    if entry_count >= max_entries:
        archives_dir.mkdir(parents=True, exist_ok=True)
        dest = archives_dir / log_file.name
        shutil.move(str(log_file), str(dest))
        print(f"Archived: {dest} ({max_entries} entries reached)")
        log_file = _create_new_log(logs_dir, ts_file)
        print(f"Created: {log_file}")
        entry_count = 0

    new_entry_num = entry_count + 1
    entry_block = (
        f"\n## Entry {new_entry_num}\n\n"
        f"- Date: {ts_iso}\n"
        f"- Author: {author}\n"
        f"- Task: {task}\n"
    )

    with open(log_file, "a", encoding="utf-8") as f:
        f.write(entry_block)

    print(f"Added entry to: {log_file}")
    print(f"  Date: {ts_iso}")
    print(f"  Author: {author}")
    print(f"  Task: {task}")
    print(f"  Entry count: {new_entry_num}/{max_entries}")

    return 0
