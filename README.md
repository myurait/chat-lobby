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

Open Terminal is pre-configured through the internal Docker network, so the terminal and file browser are
available from Open WebUI without exposing the terminal API to the host.

## Development

```bash
# Validate the compose definition
WEBUI_SECRET_KEY=test-secret \
WEBUI_ADMIN_EMAIL=admin@example.com \
WEBUI_ADMIN_PASSWORD=test-password \
OPEN_TERMINAL_API_KEY=test-terminal-key \
docker compose config
```

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

- `development-docs/AI_RUNTIME_RULES.md`: AI runtime safety rules
- `development-docs/AI_KNOWLEDGE.md`: AI knowledge entry point
- `development-docs/INDEX.md`: development documentation index
- `development-docs/roadmap/01-initial-roadmap.md`: current roadmap and phase status
