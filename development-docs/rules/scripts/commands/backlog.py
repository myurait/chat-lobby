"""ledger backlog validate — Validate feature backlog format."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


def _parse_items(content: str) -> list[dict]:
    """Parse backlog items from markdown.

    Each item starts with a ## heading. Fields are lines starting with
    ``- field_name:`` or ``- **field_name**:`` (bold variant).
    """
    items: list[dict] = []
    current: dict | None = None
    for line in content.splitlines():
        heading = re.match(r"^##\s+(.+)", line)
        if heading:
            if current is not None:
                items.append(current)
            current = {"name": heading.group(1).strip(), "fields": {}}
            continue
        if current is None:
            continue
        field = re.match(r"^-\s+\*{0,2}([^*:]+?)\*{0,2}\s*[:：]\s*(.*)", line)
        if field:
            key = field.group(1).strip().lower()
            val = field.group(2).strip()
            current["fields"][key] = val
    if current is not None:
        items.append(current)
    return items


COMMON_REQUIRED = {
    "type": ["type"],
    "summary": ["summary", "概要"],
    "priority": ["priority", "優先度"],
    "blockers": ["blockers", "ブロッカー"],
    "design constraint": ["design constraint", "設計制約", "design constraints"],
}

EXPERIENCE_TIE_KEYS = ["experience tie", "体験紐付け"]
IMPACT_AREA_KEYS = ["impact area", "影響範囲", "design impact"]


def run(args: argparse.Namespace) -> int:
    base = Path(args.base_dir)
    backlog_path = base / "project" / "features" / "01-feature-backlog.md"

    if not backlog_path.is_file():
        print(f"Error: backlog file not found: {backlog_path}", file=sys.stderr)
        return 1

    content = backlog_path.read_text(encoding="utf-8")
    items = _parse_items(content)

    if not items:
        print("Error: no backlog items found", file=sys.stderr)
        return 1

    violations: list[str] = []

    for item in items:
        fields = item["fields"]
        name = item["name"]

        for label, aliases in COMMON_REQUIRED.items():
            if not any(fields.get(a) for a in aliases):
                violations.append(f'[Medium] "{name}": missing "{label}"')

        item_type = fields.get("type", "").strip().lower()

        if item_type == "feature":
            if not any(fields.get(a) for a in EXPERIENCE_TIE_KEYS):
                violations.append(
                    f'[High] "{name}": type=feature but Experience Tie is empty'
                )
        elif item_type == "debt":
            if not any(fields.get(a) for a in IMPACT_AREA_KEYS):
                violations.append(
                    f'[High] "{name}": type=debt but Impact Area is empty'
                )

    if violations:
        print(f"Backlog validation: {len(violations)} violation(s)\n")
        for v in violations:
            print(f"- {v}")
        return 1

    print(f"Backlog validation: OK ({len(items)} items, 0 violations)")
    return 0
