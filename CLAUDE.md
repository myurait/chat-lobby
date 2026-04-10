# AI Entry Point

Before doing any work, read the following files in order. This is mandatory and non-negotiable. Do not skip any item or defer reading until later.

1. `development-docs/rules/AI_RUNTIME_RULES.md`
2. `development-docs/AI_KNOWLEDGE.md`
3. `README.md`

# Review Process

When the development flow requires a review (Step 9 in `development-docs/rules/development-process.md`), you MUST NOT review your own work inline. Instead, spawn a separate agent using the Agent tool with the `devils-advocate` agent defined in `.claude/agents/devils-advocate.md`. The canonical role definition lives in `development-docs/roles/devils-advocate.md`.

- Pass the agent the list of changed files and the purpose of the changes.
- The agent reviews from a Devil's Advocate stance, enforcing project rules as a strict guardian.
- Record the agent's findings as review evidence in `development-docs/reviews/`.
- Fix Critical and High findings before proceeding.
- After fixes, spawn the agent again for follow-up review. Append the result to the same review file.

Runtimes that cannot spawn subagents (e.g., Codex) must still apply the review criteria defined in `development-docs/roles/devils-advocate.md` inline before committing. The canonical role definition is the sole authoritative source; `.claude/agents/devils-advocate.md` is a local convenience wrapper that is not version-controlled.
