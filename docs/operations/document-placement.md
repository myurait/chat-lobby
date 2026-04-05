# Document Placement Convention

This document defines where stable Markdown documents must be stored in the shared canonical Git repository.

## Purpose

- Keep publish destinations deterministic for automation.
- Prevent ambiguity between stable documents, temporary notes, and implementation code.
- Ensure Claude Code, Codex, and the frontdoor all reference the same document layout.

## Canonical Repository Layout

The shared canonical repository must contain these top-level directories:

- `docs/`: stable operational or project-wide documents that are not feature specifications
- `specs/`: requirement documents, feature specifications, and specification revisions
- `decisions/`: ADRs and other durable decision records
- `worklog/`: task-oriented work logs and execution summaries
- `src/`: implementation code

## Placement Rules

- Publish feature or requirement documents to `specs/`.
- Publish architectural or policy decisions to `decisions/`.
- Publish work execution records to `worklog/`.
- Use `docs/` only for stable operational documents that are broader than one feature.
- Do not publish stable project documents into the root directory of the canonical repository.
- Do not mix draft notes with the canonical directories above; draft material belongs in Open WebUI Notes or other temporary working areas until promoted.

## Naming Rules

- File names must use `YYYY-MM-DD-<slug>.md`.
- The slug must be kebab-case and derived from the document title unless a clearer custom slug is needed.
- Keep titles human-readable inside the Markdown file even if the slug is abbreviated.

## Tooling Contract

- `tools/publish_to_repo.py` is the current CLI entry point for writing templated Markdown documents into the canonical repository.
- The tool expects the canonical repository layout above to exist before publishing.
- The shared template layout under `workspace/templates/chatlobby-canonical/` is the baseline structure to copy when bootstrapping a new canonical repository.
