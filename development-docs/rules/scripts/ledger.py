#!/usr/bin/env python3
"""ledger — CLI entry point for ledger-flow.

Usage:
    python scripts/ledger.py <command> [subcommand] [options]

Commands:
    init              Transcribe ledger-flow framework into a project
    review create     Create a review evidence file
    log add           Add a development log entry
    roadmap create    Create a new roadmap file
    backlog validate  Validate feature backlog format
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Ensure the ledger-flow root (parent of scripts/) is on sys.path so that
# ``from scripts.commands.xxx import run`` works regardless of the caller's cwd.
_LEDGER_ROOT = str(Path(__file__).resolve().parent.parent)
if _LEDGER_ROOT not in sys.path:
    sys.path.insert(0, _LEDGER_ROOT)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ledger",
        description="ledger-flow CLI",
    )
    parser.add_argument(
        "--base-dir",
        default="./development-docs",
        help="Base directory for development-docs (default: ./development-docs)",
    )

    sub = parser.add_subparsers(dest="command", help="Available commands")

    # init
    init_p = sub.add_parser("init", help="Transcribe ledger-flow framework into a project")
    init_p.add_argument(
        "--doc-lang",
        default="English",
        help="Documentation Language (default: English)",
    )
    init_p.add_argument(
        "--dev-lang",
        default=None,
        help="Development Language (default: none)",
    )
    init_p.add_argument(
        "--docs-path",
        default="development-docs",
        help="Project progress files path (default: development-docs)",
    )
    init_p.add_argument(
        "--no-pre-commit",
        action="store_true",
        default=False,
        help="Skip .pre-commit-config.yaml generation",
    )

    # review
    review = sub.add_parser("review", help="Review evidence commands")
    review_sub = review.add_subparsers(dest="review_command")
    rc = review_sub.add_parser("create", help="Create a review evidence file")
    rc.add_argument("--scope", required=True, help="Review scope (kebab-case)")
    rc.add_argument("--type", default="document review", help="Review type")

    # log
    log = sub.add_parser("log", help="Development log commands")
    log_sub = log.add_subparsers(dest="log_command")
    la = log_sub.add_parser("add", help="Add a development log entry")
    la.add_argument("--task", required=True, help="Task description")
    la.add_argument("--author", required=True, help="Author name")

    # roadmap
    roadmap = sub.add_parser("roadmap", help="Roadmap commands")
    roadmap_sub = roadmap.add_subparsers(dest="roadmap_command")
    rmc = roadmap_sub.add_parser("create", help="Create a new roadmap file")
    rmc.add_argument("--scope", required=True, help="Roadmap scope (kebab-case)")

    # backlog
    backlog = sub.add_parser("backlog", help="Backlog commands")
    backlog_sub = backlog.add_subparsers(dest="backlog_command")
    backlog_sub.add_parser("validate", help="Validate feature backlog format")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command is None:
        parser.print_help()
        return 1

    if args.command == "init":
        from scripts.commands.init import run
        return run(args)

    if args.command == "review" and getattr(args, "review_command", None) == "create":
        from scripts.commands.review import run
        return run(args)

    if args.command == "log" and getattr(args, "log_command", None) == "add":
        from scripts.commands.log import run
        return run(args)

    if args.command == "roadmap" and getattr(args, "roadmap_command", None) == "create":
        from scripts.commands.roadmap import run
        return run(args)

    if args.command == "backlog" and getattr(args, "backlog_command", None) == "validate":
        from scripts.commands.backlog import run
        return run(args)

    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
