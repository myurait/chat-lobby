English | [日本語](README.ja.md)

# ChatLobby

A self-hosted integrated chat platform that connects multiple AI agents (Claude Code, Codex, etc.)
behind a single conversational interface powered by Open WebUI.

ChatLobby enables you to manage the full development lifecycle — from investigation and spec authoring
to implementation requests, status monitoring, and spec revisions — all from a single chat, including mobile.

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

## Development

```bash
# Validate the compose definition
WEBUI_SECRET_KEY=test-secret \
WEBUI_ADMIN_EMAIL=admin@example.com \
WEBUI_ADMIN_PASSWORD=test-password \
OPEN_TERMINAL_API_KEY=test-terminal-key \
docker compose config
```

## Shared Repo Template

- `workspace/templates/chatlobby-canonical/` provides the initial directory layout for the shared canonical Git repository.
- `workspace/repos/` is reserved for runtime clones and scratch repositories opened from Open Terminal.
- The dedicated workspace mount narrows terminal access to the intended project work area instead of the full host filesystem.

## Manual Verification

1. Sign in with the admin account from `.env`.
2. Confirm that a new public sign-up is rejected.
3. Open Open Terminal from Open WebUI and confirm `/workspace` is visible.
4. Use the terminal file tools or File Browser to list `/workspace` and verify `repos/` and `templates/` appear.
5. For phone testing, open `http://<your-lan-ip>:<OPEN_WEBUI_PORT>` from a device on the same network.

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
