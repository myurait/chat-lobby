English | [日本語](README.ja.md)

# ChatLobby

A self-hosted integrated chat platform that connects multiple AI agents (Claude Code, Codex, etc.)
behind a single conversational interface powered by Open WebUI.

ChatLobby enables you to manage the full development lifecycle — from investigation and spec authoring
to implementation requests, status monitoring, and spec revisions — all from a single chat, including mobile.

## Prerequisites

- Docker Compose for the Open WebUI stack
- Node.js 22 or newer for running the host-side TypeScript services directly
- Python 3 for sync helpers and the current automated test suite
- A shared bearer token in `.env` for Open WebUI to reach host-side adapters and dispatcher

## Setup

```bash
# 1. Prepare local settings
cp .env.example .env

# 2. Start the local stack
docker compose up -d

# 3. Pull at least one local model for Open WebUI
docker compose exec ollama ollama pull qwen3:8b
```

Open `http://localhost:3000` and sign in with the admin account defined in `.env`.
The first boot creates the admin user automatically and keeps public sign-up disabled.
If port `3000` is already in use on your machine, set `OPEN_WEBUI_PORT` and `WEBUI_URL` in `.env`
before starting the stack, for example `3001` and `http://localhost:3001`.

Open Terminal is pre-configured through the internal Docker network, so the terminal and file browser are
available from Open WebUI without exposing the terminal API to the host.
The host-side [`workspace/`](/Users/fox4foofighter/dev/chat-lobby/workspace/README.md) directory is mounted into the
terminal container at `/workspace` as the dedicated working area.
`CHATLOBBY_INTERNAL_API_TOKEN` from `.env` is also passed into the Open WebUI container.

## Development

```bash
# Validate the compose definition
WEBUI_SECRET_KEY=test-secret \
WEBUI_ADMIN_EMAIL=admin@example.com \
WEBUI_ADMIN_PASSWORD=test-password \
OPEN_TERMINAL_API_KEY=test-terminal-key \
docker compose config

# Publish a spec into the canonical repo layout
python3 tools/publish_to_repo.py \
  --repo workspace/templates/chatlobby-canonical \
  --kind spec \
  --title "Example feature spec" \
  --body "Initial summary"

# Register the Open WebUI publish pipe
python3 tools/sync_openwebui_publish_pipe.py \
  --webui-url http://localhost:3000 \
  --email admin@example.com \
  --password chatlobby-admin-password

# Load .env into the current shell before starting host-side services
set -a
source .env
set +a

# Start the local Claude adapter
CLAUDE_ADAPTER_HOST=0.0.0.0 node services/claude-adapter/src/server.ts

# Register the Open WebUI Claude task pipe
python3 tools/sync_openwebui_claude_pipe.py \
  --webui-url http://localhost:3000 \
  --email admin@example.com \
  --password chatlobby-admin-password

# Register the Open WebUI Codex task pipe
python3 tools/sync_openwebui_codex_pipe.py \
  --webui-url http://localhost:3000 \
  --email admin@example.com \
  --password chatlobby-admin-password

# Register the Open WebUI knowledge query pipe
python3 tools/sync_openwebui_knowledge_pipe.py \
  --webui-url http://localhost:3000 \
  --email admin@example.com \
  --password chatlobby-admin-password

# Register the Open WebUI dispatch pipe
python3 tools/sync_openwebui_dispatch_pipe.py \
  --webui-url http://localhost:3000 \
  --email admin@example.com \
  --password chatlobby-admin-password
```

Replace the URL above if you changed `OPEN_WEBUI_PORT`.
The `typecheck` script expects `tsc` to be available in your shell.

## Shared Repo Template

- `workspace/templates/chatlobby-canonical/` provides the initial directory layout for the shared canonical Git repository.
- `workspace/repos/` is reserved for runtime clones and scratch repositories opened from Open Terminal.
- The dedicated workspace mount narrows terminal access to the intended project work area instead of the full host filesystem.
- `tools/publish_to_repo.py` writes templated Markdown into the canonical repository layout.
- `tools/openwebui/chatlobby_publish_pipe.py` is the Open WebUI pipe that exposes publish-from-chat.
- `tools/sync_openwebui_publish_pipe.py` registers or updates that pipe through the Open WebUI admin API.

## Chat Publish

After syncing the pipe, select the `ChatLobby Publish` model in Open WebUI and send a JSON message like this:

```json
{
  "kind": "spec",
  "title": "Example feature spec",
  "body": "Summarize the feature here.",
  "slug": "example-feature-spec"
}
```

The pipe writes the document into the canonical repository and replies with the saved path.

## Claude Adapter

The first Phase C adapter is a local HTTP service that wraps `claude -p --output-format json`.

```bash
# Start the adapter for Open WebUI integration
CLAUDE_ADAPTER_HOST=0.0.0.0 node services/claude-adapter/src/server.ts

# Create a Claude task
curl -X POST http://127.0.0.1:8787/tasks \
  -H "Authorization: Bearer ${CHATLOBBY_INTERNAL_API_TOKEN}" \
  -H 'Content-Type: application/json' \
  -d '{"prompt":"Reply with exactly ok.","workingDirectory":"'"$(pwd)"'"}'

# Poll task status
curl http://127.0.0.1:8787/tasks/<task-id>
```

After syncing the pipe, select the `ChatLobby Claude Task` model in Open WebUI and send a JSON message like this:

```json
{
  "prompt": "Reply with exactly ok.",
  "workingDirectory": "/Users/you/path/to/repo"
}
```

The pipe creates a Claude task through the local adapter and returns the task result to chat.

## Codex Adapter

The Codex adapter mirrors the Claude adapter pattern and wraps `codex exec --json`.

```bash
# Start the adapter for Open WebUI integration
CODEX_ADAPTER_HOST=0.0.0.0 node services/codex-adapter/src/server.ts

# Opt in to unattended execution only when you explicitly want it
CODEX_ADAPTER_HOST=0.0.0.0 \
CODEX_BYPASS_APPROVALS_AND_SANDBOX=true \
node services/codex-adapter/src/server.ts

# Create a Codex task
curl -X POST http://127.0.0.1:8788/tasks \
  -H "Authorization: Bearer ${CHATLOBBY_INTERNAL_API_TOKEN}" \
  -H 'Content-Type: application/json' \
  -d '{"prompt":"Reply with exactly ok.","workingDirectory":"'"$(pwd)"'"}'

# Poll task status
curl http://127.0.0.1:8788/tasks/<task-id>
```

After syncing the pipe, select the `ChatLobby Codex Task` model in Open WebUI and send:

```json
{
  "prompt": "Reply with exactly ok.",
  "workingDirectory": "/Users/you/path/to/repo"
}
```

By default the adapter uses `workspace-write` sandboxing and does not bypass approvals. Set
`CODEX_BYPASS_APPROVALS_AND_SANDBOX=true` only when you explicitly want unattended execution.

## Knowledge Adapter

The knowledge adapter exposes canonical repository search and read endpoints.

```bash
# Start the adapter for Open WebUI integration
KNOWLEDGE_ADAPTER_HOST=0.0.0.0 node services/knowledge-adapter/src/server.ts

# Search canonical knowledge
curl -X POST http://127.0.0.1:8789/search \
  -H "Authorization: Bearer ${CHATLOBBY_INTERNAL_API_TOKEN}" \
  -H 'Content-Type: application/json' \
  -d '{"query":"ChatLobby"}'
```

After syncing the pipe, select the `ChatLobby Knowledge Query` model in Open WebUI and send:

```json
{
  "query": "ChatLobby"
}
```

## Dispatcher

The dispatcher applies rule-based routing from `services/dispatcher/rules.json` and chooses Claude, Codex,
or knowledge automatically.

```bash
# Start the dispatcher for Open WebUI integration
DISPATCHER_HOST=0.0.0.0 node services/dispatcher/src/server.ts

# Test automatic routing directly
curl -X POST http://127.0.0.1:8790/dispatch \
  -H "Authorization: Bearer ${CHATLOBBY_INTERNAL_API_TOKEN}" \
  -H 'Content-Type: application/json' \
  -d '{"prompt":"Implement a prototype and reply with exactly ok.","workingDirectory":"'"$(pwd)"'"}'
```

After syncing the pipe, select the `ChatLobby Dispatch Task` model in Open WebUI and send plain text like:

```text
Implement the feature and reply with exactly ok.
```

Send JSON only when you need override fields such as `workerHint`, `repoPath`, or `workingDirectory`.
If a synced pipe does not pick up the token automatically, set `api_bearer_token` in that function's valves and sync it again.

## Manual Verification

1. Sign in with the admin account from `.env`.
2. Confirm that a new public sign-up is rejected.
3. Open Open Terminal from Open WebUI and confirm `/workspace` is visible.
4. Use the terminal file tools or File Browser to list `/workspace` and verify `repos/` and `templates/` appear.
5. For phone testing, open `http://<your-lan-ip>:<OPEN_WEBUI_PORT>` from a device on the same network.
6. Sync `chatlobby_publish`, select the `ChatLobby Publish` model, and confirm a chat request writes a file under `/workspace/templates/chatlobby-canonical/`.
7. Start the Claude adapter with `CLAUDE_ADAPTER_HOST=0.0.0.0`, sync `chatlobby_claude_task`, and confirm the `ChatLobby Claude Task` model returns a completed task result in chat.
8. Start the Codex adapter with `CODEX_ADAPTER_HOST=0.0.0.0`, sync `chatlobby_codex_task`, and confirm the `ChatLobby Codex Task` model returns a completed task result in chat.
9. Start the knowledge adapter with `KNOWLEDGE_ADAPTER_HOST=0.0.0.0`, sync `chatlobby_knowledge_query`, and confirm the `ChatLobby Knowledge Query` model returns search results from the canonical repo.
10. Start the dispatcher with `DISPATCHER_HOST=0.0.0.0`, sync `chatlobby_dispatch_task`, and confirm plain-text requests such as `Implement ...`, `この不具合を直して`, and `README.ja.md を検索して` are routed to Codex, Claude, and knowledge respectively.

## Architecture

```text
[Mobile / PC]
    |
[Open WebUI]  ← frontdoor
    |-- conversations
    |-- Folders & Projects
    |-- Notes / Knowledge
    |-- custom tools / pipelines
    |-- status panel
            |
    [dispatcher]
      |-- Codex adapter
      |-- Claude adapter
      |-- Git/MCP knowledge adapter
            |
    [Git repositories]  ← canonical source of truth
```

## Development Docs

- `development-docs/rules/AI_RUNTIME_RULES.md`: AI runtime safety rules
- `development-docs/AI_KNOWLEDGE.md`: AI knowledge entry point
- `development-docs/INDEX.md`: development documentation index
- `development-docs/roadmap/01-initial-roadmap.md`: current roadmap and phase status
