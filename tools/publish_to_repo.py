#!/usr/bin/env python3
"""Publish a Markdown document into the canonical Git repository layout."""

from __future__ import annotations

import argparse
import datetime as dt
import re
import sys
from dataclasses import dataclass
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
TEMPLATES_DIR = ROOT_DIR / "docs" / "templates"

KIND_TO_DIRECTORY = {
    "spec": "specs",
    "adr": "decisions",
    "worklog": "worklog",
}


@dataclass(frozen=True)
class PublishRequest:
    repo_path: Path
    kind: str
    title: str
    slug: str
    body: str
    date: str
    author: str


def slugify(value: str) -> str:
    """Convert a title-like string into a filesystem-safe kebab-case slug."""
    normalized = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower())
    slug = normalized.strip("-")
    if not slug:
        raise ValueError("Slug cannot be empty")
    return slug


def load_body(args: argparse.Namespace) -> str:
    if args.source_file:
        return Path(args.source_file).read_text(encoding="utf-8").strip()
    if args.body:
        return args.body.strip()
    return ""


def build_request(args: argparse.Namespace) -> PublishRequest:
    slug = slugify(args.slug or args.title)
    date_value = args.date or dt.date.today().isoformat()
    return PublishRequest(
        repo_path=Path(args.repo).resolve(),
        kind=args.kind,
        title=args.title.strip(),
        slug=slug,
        body=load_body(args),
        date=date_value,
        author=args.author,
    )


def validate_repo_layout(repo_path: Path) -> None:
    missing = [name for name in ("docs", "specs", "decisions", "worklog") if not (repo_path / name).exists()]
    if missing:
        missing_dirs = ", ".join(missing)
        raise FileNotFoundError(f"Target repository is missing required directories: {missing_dirs}")


def template_path_for(kind: str) -> Path:
    template_path = TEMPLATES_DIR / f"{kind}.md"
    if not template_path.exists():
        raise FileNotFoundError(f"Template not found: {template_path}")
    return template_path


def target_path_for(request: PublishRequest) -> Path:
    target_directory = request.repo_path / KIND_TO_DIRECTORY[request.kind]
    filename = f"{request.date}-{request.slug}.md"
    return target_directory / filename


def render_document(request: PublishRequest) -> str:
    template_text = template_path_for(request.kind).read_text(encoding="utf-8")
    return (
        template_text.replace("{{title}}", request.title)
        .replace("{{date}}", request.date)
        .replace("{{slug}}", request.slug)
        .replace("{{author}}", request.author)
        .replace("{{body}}", request.body)
    )


def publish_document(request: PublishRequest, overwrite: bool = False) -> Path:
    validate_repo_layout(request.repo_path)
    target_path = target_path_for(request)
    if target_path.exists() and not overwrite:
        raise FileExistsError(f"Target file already exists: {target_path}")

    target_path.parent.mkdir(parents=True, exist_ok=True)
    target_path.write_text(render_document(request), encoding="utf-8")
    return target_path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Publish a spec, ADR, or worklog Markdown file into the canonical repo layout."
    )
    parser.add_argument("--repo", required=True, help="Path to the target canonical repository")
    parser.add_argument("--kind", choices=sorted(KIND_TO_DIRECTORY), required=True, help="Document kind to publish")
    parser.add_argument("--title", required=True, help="Document title")
    parser.add_argument("--slug", help="Optional custom slug for the output file name")
    parser.add_argument("--body", help="Optional inline Markdown body")
    parser.add_argument("--source-file", help="Optional Markdown source file to embed in the template")
    parser.add_argument("--date", help="Document date in YYYY-MM-DD format")
    parser.add_argument("--author", default="ChatLobby", help="Author label to insert into the template")
    parser.add_argument("--overwrite", action="store_true", help="Allow replacing an existing target file")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.body and args.source_file:
        parser.error("--body and --source-file cannot be used together")

    request = build_request(args)
    try:
        target_path = publish_document(request, overwrite=args.overwrite)
    except (FileExistsError, FileNotFoundError, ValueError) as error:
        print(str(error), file=sys.stderr)
        return 1

    print(target_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
