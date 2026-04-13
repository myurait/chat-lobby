"""ledger review create — Create a review evidence file."""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

from scripts.lib.common import file_timestamp, iso_timestamp, now_local, to_kebab

_INLINE_TEMPLATE = """\
# Review

Use flat bullets and headings. Do not use Markdown tables in review evidence.

- Date: {date}
- Reviewer:
- Base Commit:
- Scope: {scope}
- Review Type: {review_type}
- Trigger:
- Criteria:
  - Was the chosen approach justified against simpler alternatives?
  - Did the change add unnecessary complexity or layers?
  - Can the user understand why this change exists and what it enables?

---

## Findings

### Critical

- None

### High

- None

### Medium

- None

### Low

- None

## Review Dimensions

## Implementation Response Plan

- Date:
- Reviewer:
- Base Commit:
- Plan Summary:
- Planned Fixes:
- Deferred Items:

## Follow-Up Review History
"""


def _inject_fields(content: str, date: str, scope: str, review_type: str) -> str:
    lines: list[str] = []
    for line in content.splitlines(keepends=True):
        stripped = line.lstrip()
        if stripped.startswith("- Date:") and stripped.strip() == "- Date:":
            line = f"- Date: {date}\n"
        elif stripped.startswith("- Scope:") and stripped.strip() == "- Scope:":
            line = f"- Scope: {scope}\n"
        elif stripped.startswith("- Review Type:") and "code review | tech lead review" in stripped:
            line = f"- Review Type: {review_type}\n"
        lines.append(line)
    return "".join(lines)


def _review_files(reviews_dir: Path) -> list[Path]:
    results = []
    for f in reviews_dir.iterdir():
        if f.is_dir():
            continue
        name = f.name.lower()
        if name in ("readme.md",) or "template" in name:
            continue
        if f.suffix == ".md" and f.name.startswith("review_"):
            results.append(f)
    results.sort(key=lambda p: p.name)
    return results


def run(args: argparse.Namespace) -> int:
    base = Path(args.base_dir)
    reviews_dir = base / "project" / "reviews"
    archives_dir = reviews_dir / "archives"

    if not reviews_dir.is_dir():
        print(f"Error: reviews directory not found: {reviews_dir}", file=sys.stderr)
        return 1

    scope = to_kebab(args.scope)
    if not scope:
        print("Error: --scope must be a non-empty string", file=sys.stderr)
        return 1

    review_type = args.type
    now = now_local()
    ts_file = file_timestamp(now)
    ts_iso = iso_timestamp(now)

    filename = f"review_{ts_file}_{scope}.md"
    filepath = reviews_dir / filename

    # Resolve template
    template_path = base / "rules" / "templates" / "review_template.md"

    if template_path.is_file():
        raw = template_path.read_text(encoding="utf-8")
        content = _inject_fields(raw, ts_iso, scope, review_type)
    else:
        content = _INLINE_TEMPLATE.format(date=ts_iso, scope=scope, review_type=review_type)

    filepath.write_text(content, encoding="utf-8")
    print(f"Created: {filepath}")

    # Archive oldest if exceeding 5-file limit
    archives_dir.mkdir(parents=True, exist_ok=True)
    existing = _review_files(reviews_dir)
    max_files = 5
    while len(existing) > max_files:
        oldest = existing.pop(0)
        dest = archives_dir / oldest.name
        shutil.move(str(oldest), str(dest))
        print(f"Archived: {dest} (exceeded {max_files}-file limit)")
        existing = _review_files(reviews_dir)

    return 0
