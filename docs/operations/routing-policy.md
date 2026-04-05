# Routing Policy

This document defines the initial automatic routing rules used by `services/dispatcher`.

The rule source is `services/dispatcher/rules.json`.

## Goal

- Let the user submit a single task without choosing Claude or Codex manually.
- Keep the first dispatcher deterministic and easy to debug.
- Route knowledge lookups separately from implementation work.
- Accept plain-language requests from the frontdoor and only use manual override when needed.

## Initial Rules

- Route to `knowledge` when the request includes `query` or `path`.
- Route to `knowledge` when the prompt contains knowledge-oriented English or Japanese keywords such as `search`, `read`, `spec`, `adr`, `検索`, `読んで`, `仕様`, or `要件`.
- When `knowledge` is selected from a plain-language prompt, the dispatcher strips common request words before sending the search query to the knowledge adapter.
- Route to `claude` when the prompt contains local-environment or bug-fix keywords such as `terminal`, `debug`, `docker`, `fix`, `bug`, `調査`, `不具合`, or `直して`.
- Route to `codex` when the prompt contains implementation keywords such as `implement`, `build`, `refactor`, `feature`, `実装`, `追加`, or `プロトタイプ`.
- Default to `codex` when no rule matches.

## Overrides

- `workerHint` can force `claude`, `codex`, or `knowledge`.
- Overrides are intended for testing and debugging while the dispatcher is still simple.
- The Open WebUI dispatch pipe accepts plain text by default and JSON only when the caller needs override fields.

## Limits

- The current dispatcher is rule-based, not model-based.
- It does not yet consider task history, repository state, or cost.
- It does not merge responses from multiple workers.
- Knowledge search is still keyword- and path-match based; semantic retrieval is out of scope for this phase.
