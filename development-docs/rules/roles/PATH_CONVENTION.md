# Path Convention for Role Definitions

## How Paths Work in Role Definitions

After `ledger init`, all framework files are transcribed into `development-docs/` within the project. Role definitions use project-root-relative paths.

### Framework paths (inside development-docs/rules/)

Paths like `development-docs/rules/...`, `development-docs/rules/roles/...`, `development-docs/rules/templates/...` are relative to the project root. These correspond to the framework's `rules/`, `roles/`, and `templates/` directories that were transcribed by `ledger init`.

### Project paths (inside development-docs/project/)

Paths like `development-docs/project/logs/`, `development-docs/project/reviews/`, `development-docs/project/roadmap/`, `development-docs/project/design/`, `development-docs/project/features/`, `development-docs/project/decisions.md`, `development-docs/project/knowledge.md` are relative to the project root.

### Path mapping from framework source to project

After transcription, the mapping is:

- `rules/` -> `development-docs/rules/`
- `roles/` -> `development-docs/rules/roles/`
- `templates/` -> `development-docs/rules/templates/`
- `logs/` -> `development-docs/project/logs/`
- `reviews/` -> `development-docs/project/reviews/`
- `roadmap/` -> `development-docs/project/roadmap/`
- `design/` -> `development-docs/project/design/`
- `features/` -> `development-docs/project/features/`
- `decisions.md` -> `development-docs/project/decisions.md`
- `knowledge.md` -> `development-docs/project/knowledge.md`
- `project-policies.md` -> `development-docs/project-policies.md`

### Changing paths

After `ledger init`, the project owns all transcribed files. To change directory names or structure, edit the files directly. There is no framework command to regenerate or update them.
