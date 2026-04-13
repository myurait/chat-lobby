"""ledger init — Transcribe ledger-flow framework into a project (init-and-done model)."""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

from scripts.lib.common import (
    iso_timestamp,
    render_template,
    resolve_project_root,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_VERSION = "0.1.0"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _resolve_ledger_flow_root() -> Path:
    """Detect the ledger-flow repository root from this script's location.

    Follows symlinks so that the script can be invoked via a symlink.
    The layout is: ledger-flow/scripts/commands/init.py -> scripts/ parent is root.
    """
    return Path(__file__).resolve().parent.parent.parent


def _build_variables(args: argparse.Namespace) -> dict[str, str]:
    """Build template variable mapping from CLI arguments."""
    return {
        "documentationLanguage": args.doc_lang,
        "developmentLanguage": args.dev_lang or "",
        "codeInternalLanguage": "English",
        "productLanguages": args.doc_lang,
        "setupDate": iso_timestamp(),
        "version": _VERSION,
    }


def _build_ledger_json(args: argparse.Namespace, setup_date: str) -> dict:
    """Build the .ledger.json provenance snapshot."""
    return {
        "version": _VERSION,
        "setupDate": setup_date,
        "setupBy": "ledger init",
        "projectPolicies": {
            "documentationLanguage": args.doc_lang,
            "developmentLanguage": args.dev_lang or "",
            "codeInternalLanguage": "English",
            "productLanguages": [args.doc_lang],
        },
    }


def _write_file(path: Path, content: str, created: list[str]) -> None:
    """Write *content* to *path* if it does not already exist (idempotent)."""
    if path.exists():
        print(f"  [skip] {path}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    created.append(f"  [file] {path}")


def _copy_file(src: Path, dest: Path, created: list[str]) -> None:
    """Copy *src* to *dest* if *dest* does not already exist (idempotent)."""
    if dest.exists():
        print(f"  [skip] {dest}")
        return
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(str(src), str(dest))
    created.append(f"  [file] {dest}")


def _copy_tree(src_dir: Path, dest_dir: Path, created: list[str]) -> None:
    """Recursively copy all files from *src_dir* to *dest_dir* (idempotent).

    Skips files that already exist at the destination. Ignores __pycache__
    directories and .pyc files.
    """
    if not src_dir.is_dir():
        return
    for src in sorted(src_dir.rglob("*")):
        if src.is_dir():
            continue
        # Skip Python cache files
        if "__pycache__" in src.parts or src.suffix == ".pyc":
            continue
        rel = src.relative_to(src_dir)
        dest = dest_dir / rel
        _copy_file(src, dest, created)


def _ensure_dir(path: Path, created: list[str]) -> None:
    """Create directory (and parents) if it does not exist."""
    if path.exists():
        return
    path.mkdir(parents=True, exist_ok=True)
    created.append(f"  [dir]  {path}")


# ---------------------------------------------------------------------------
# Template processing
# ---------------------------------------------------------------------------

def _process_root_templates(
    template_dir: Path,
    project_root: Path,
    variables: dict[str, str],
    docs_path: str,
    created: list[str],
    skip_pre_commit: bool = False,
) -> None:
    """Process templates/project/ for root-level and .claude/agents/ files.

    - ``.tmpl`` files at the root of templates/project/ -> project root (rendered)
    - ``claude-agents/*.tmpl`` -> ``.claude/agents/`` (rendered)
    - ``project/design/*``, ``project/features/*``, ``project/requirements/*``
      -> ``{docsPath}/project/``
    - ``design/*``, ``features/*``, ``requirements/*`` at templates/project/
      -> ``{docsPath}/project/`` (project scaffold content)
    """
    if not template_dir.is_dir():
        return

    for src in sorted(template_dir.rglob("*")):
        if src.is_dir():
            continue

        rel = src.relative_to(template_dir)
        parts = rel.parts

        # claude-agents/ -> .claude/agents/
        if parts[0] == "claude-agents":
            dest_name = rel.name
            if dest_name.endswith(".tmpl"):
                dest_name = dest_name[: -len(".tmpl")]
                content = src.read_text(encoding="utf-8")
                rendered = render_template(content, variables)
                dest = project_root / ".claude" / "agents" / dest_name
                _write_file(dest, rendered, created)
            else:
                dest = project_root / ".claude" / "agents" / dest_name
                _copy_file(src, dest, created)
            continue

        # design/, features/, requirements/ -> docsPath/project/
        if parts[0] in ("design", "features", "requirements"):
            dest = project_root / docs_path / "project" / rel
            _copy_file(src, dest, created)
            continue

        # .tmpl files at the top level -> project root (rendered)
        # Skip entry-point.md.tmpl and project-policies.md.tmpl here;
        # they are handled in Step 8 as development-docs/ cross-cutting files.
        _DOCS_ONLY_TEMPLATES = {"entry-point.md.tmpl", "project-policies.md.tmpl"}
        if src.name.endswith(".tmpl") and len(parts) == 1:
            if src.name in _DOCS_ONLY_TEMPLATES:
                continue
            dest_name = src.name[: -len(".tmpl")]
            # Skip pre-commit config if --no-pre-commit
            if dest_name == ".pre-commit-config.yaml" and skip_pre_commit:
                continue
            content = src.read_text(encoding="utf-8")
            rendered = render_template(content, variables)
            dest = project_root / dest_name
            _write_file(dest, rendered, created)
            continue


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def run(args: argparse.Namespace) -> int:
    project_root = resolve_project_root()
    ledger_root = _resolve_ledger_flow_root()

    variables = _build_variables(args)
    setup_date = variables["setupDate"]
    docs_path = args.docs_path
    skip_pre_commit = getattr(args, "no_pre_commit", False)
    created: list[str] = []

    docs_dir = project_root / docs_path
    rules_dir = docs_dir / "rules"
    project_dir = docs_dir / "project"

    # ------------------------------------------------------------------
    # Step 1: Transcribe framework rules/ -> development-docs/rules/
    # ------------------------------------------------------------------
    _copy_tree(ledger_root / "rules", rules_dir, created)

    # ------------------------------------------------------------------
    # Step 2: Transcribe framework roles/ -> development-docs/rules/roles/
    # ------------------------------------------------------------------
    _copy_tree(ledger_root / "roles", rules_dir / "roles", created)

    # ------------------------------------------------------------------
    # Step 3: Transcribe framework templates/ -> development-docs/rules/templates/
    #         (only the top-level template files, not templates/project/)
    # ------------------------------------------------------------------
    fw_templates_dir = ledger_root / "templates"
    if fw_templates_dir.is_dir():
        for src in sorted(fw_templates_dir.iterdir()):
            if src.is_file():
                dest = rules_dir / "templates" / src.name
                _copy_file(src, dest, created)

    # ------------------------------------------------------------------
    # Step 4: Transcribe framework scripts/ -> development-docs/rules/scripts/
    # ------------------------------------------------------------------
    _copy_tree(ledger_root / "scripts", rules_dir / "scripts", created)

    # ------------------------------------------------------------------
    # Step 5: Transcribe project scaffold content
    #         templates/project/design/    -> development-docs/project/design/
    #         templates/project/features/  -> development-docs/project/features/
    #         templates/project/requirements/ -> development-docs/project/requirements/
    # ------------------------------------------------------------------
    template_dir = ledger_root / "templates" / "project"
    _process_root_templates(
        template_dir, project_root, variables, docs_path, created, skip_pre_commit,
    )

    # ------------------------------------------------------------------
    # Step 6: Create project directories under development-docs/project/
    # ------------------------------------------------------------------
    project_dirs = [
        project_dir / "logs" / "archives",
        project_dir / "reviews" / "archives",
        project_dir / "roadmap" / "archives",
        project_dir / "reference" / "historical-documents",
        project_dir / "features" / "epics",
    ]
    for d in project_dirs:
        _ensure_dir(d, created)

    # ------------------------------------------------------------------
    # Step 7: Generate decisions.md and knowledge.md
    # ------------------------------------------------------------------
    _write_file(
        project_dir / "decisions.md",
        "# Architecture Decision Log\n",
        created,
    )
    _write_file(
        project_dir / "knowledge.md",
        "# Project Knowledge\n",
        created,
    )

    # ------------------------------------------------------------------
    # Step 8: Generate development-docs/ cross-cutting files
    # ------------------------------------------------------------------

    # entry-point.md from template (with variable substitution)
    entry_point_tmpl = template_dir / "entry-point.md.tmpl"
    if entry_point_tmpl.is_file():
        content = entry_point_tmpl.read_text(encoding="utf-8")
        rendered = render_template(content, variables)
        _write_file(docs_dir / "entry-point.md", rendered, created)

    # project-policies.md from template (with variable substitution)
    policies_tmpl = template_dir / "project-policies.md.tmpl"
    if policies_tmpl.is_file():
        content = policies_tmpl.read_text(encoding="utf-8")
        rendered = render_template(content, variables)
        _write_file(docs_dir / "project-policies.md", rendered, created)

    # ------------------------------------------------------------------
    # Step 9: Generate .ledger.json (provenance snapshot)
    # ------------------------------------------------------------------
    ledger_json_path = docs_dir / ".ledger.json"
    if not ledger_json_path.exists():
        ledger_json_path.parent.mkdir(parents=True, exist_ok=True)
        data = _build_ledger_json(args, setup_date)
        ledger_json_path.write_text(
            json.dumps(data, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        created.append(f"  [file] {ledger_json_path}")
    else:
        print(f"  [skip] {ledger_json_path}")

    # ------------------------------------------------------------------
    # Report
    # ------------------------------------------------------------------
    if created:
        print("Created:")
        for line in created:
            print(line)
    else:
        print("All files and directories already exist. Nothing to do.")

    print()
    print("ledger init complete.")
    print()
    print("  Next steps:")
    if not skip_pre_commit:
        print("  1. Install pre-commit hooks:   pre-commit install")
        print("  2. Review CLAUDE.md and customize if needed.")
    else:
        print("  1. Review CLAUDE.md and customize if needed.")

    return 0
