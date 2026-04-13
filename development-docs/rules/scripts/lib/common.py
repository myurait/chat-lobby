"""Shared utilities for ledger-flow CLI commands."""

from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path


def now_local() -> datetime:
    """Return current local time with UTC offset."""
    return datetime.now(timezone.utc).astimezone()


def iso_timestamp(dt: datetime | None = None) -> str:
    """ISO 8601 with timezone offset, e.g. 2026-04-10T14:30:52+09:00."""
    if dt is None:
        dt = now_local()
    return dt.isoformat(timespec="seconds")


def file_timestamp(dt: datetime | None = None) -> str:
    """Compact timestamp for file names: YYYYMMDDhhmmss."""
    if dt is None:
        dt = now_local()
    return dt.strftime("%Y%m%d%H%M%S")


def to_kebab(raw: str) -> str:
    """Normalise a string to kebab-case (lowercase, ASCII only, hyphens)."""
    s = raw.strip().lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")


# ---------------------------------------------------------------------------
# Path resolution
# ---------------------------------------------------------------------------

def resolve_project_root() -> Path:
    """Return the project root (current working directory)."""
    return Path.cwd()


# ---------------------------------------------------------------------------
# Template rendering
# ---------------------------------------------------------------------------

def render_template(content: str, variables: dict[str, str]) -> str:
    """Replace ``{{key}}`` placeholders with values from *variables*."""
    for key, value in variables.items():
        content = content.replace("{{" + key + "}}", value)
    return content


# ---------------------------------------------------------------------------
# .ledger.json I/O
# ---------------------------------------------------------------------------

def load_ledger_json(project_root: Path) -> dict:
    """Load and return ``.ledger.json`` from the development-docs directory.

    In the init-and-done model, .ledger.json lives at
    ``<project_root>/development-docs/.ledger.json``.
    Falls back to ``<project_root>/.ledger.json`` for legacy compatibility.

    Exits with code 1 if the file is missing or malformed.
    """
    path = project_root / "development-docs" / ".ledger.json"
    if not path.is_file():
        # Legacy fallback
        path = project_root / ".ledger.json"
    if not path.is_file():
        print(f"Error: .ledger.json not found", file=sys.stderr)
        sys.exit(1)
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"Error: .ledger.json is malformed: {exc}", file=sys.stderr)
        sys.exit(1)


def save_ledger_json(project_root: Path, data: dict) -> None:
    """Write *data* to ``.ledger.json`` in the development-docs directory."""
    path = project_root / "development-docs" / ".ledger.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
