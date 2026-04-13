## Common References (all roles must read)

- development-docs/rules/AI_RUNTIME_RULES.md (safety rules)
- development-docs/project-policies.md (project-specific policies)

These references are non-negotiable and apply regardless of role.

## Role Router

Determine what the user is asking for, then read the corresponding role file.

- **Implementation, code changes, bug fixes** -> Worker -> development-docs/rules/roles/worker.md
- **Roadmap, planning, milestone consultation** -> Planning Lead -> development-docs/rules/roles/planning-lead.md
- **Code review request** -> Devil's Advocate -> development-docs/rules/roles/devils-advocate.md
- **Language / format / compliance check** -> Compliance Auditor -> development-docs/rules/roles/compliance-auditor.md
- **Code quality / test design check** -> Code Quality Auditor -> development-docs/rules/roles/code-quality-auditor.md

**After completing implementation work**, the Worker role handles spawning review agents -- see the spawn rules defined in development-docs/rules/roles/worker.md.

## Project Paths

- Framework rules: development-docs/rules/
- Role definitions: development-docs/rules/roles/
- Templates: development-docs/rules/templates/
- Project documents: development-docs/project/
- Project policies: development-docs/project-policies.md

## CLI Quick Reference

- `python3 development-docs/rules/scripts/ledger.py log add --task "..." --author "..."`
- `python3 development-docs/rules/scripts/ledger.py review create --scope "..."`
- `python3 development-docs/rules/scripts/ledger.py roadmap create --scope "..."`

## Project-Specific Rules

<!-- Add project-specific rules below this line. -->
