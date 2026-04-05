[English](README.md) | 日本語

# ChatLobby

Open WebUI を frontdoor とし、複数の AI エージェント（Claude Code, Codex 等）を背後に接続する
self-hosted 統合チャット基盤。

スマホから自然言語で話しかけるだけで、調査・仕様化・実装依頼・修正依頼・状況確認までを
一貫して行える会話中心の開発基盤を目指す。

## セットアップ

```bash
# 1. ローカル設定を作成
cp .env.example .env

# 2. ローカルスタックを起動
docker compose up -d

# 3. Open WebUI で使うローカルモデルを 1 つ追加
docker compose exec ollama ollama pull qwen3:8b
```

`http://localhost:3000` を開き、`.env` に設定した管理者アカウントでログインする。
初回起動時に管理者ユーザーを自動作成し、公開サインアップは無効のままにする。

Open Terminal は Docker 内ネットワークで事前接続するため、端末 API をホストへ直接公開せずに
Open WebUI からターミナルと File Browser を利用できる。

## 開発

```bash
# Compose 定義の検証
WEBUI_SECRET_KEY=test-secret \
WEBUI_ADMIN_EMAIL=admin@example.com \
WEBUI_ADMIN_PASSWORD=test-password \
OPEN_TERMINAL_API_KEY=test-terminal-key \
docker compose config
```

## アーキテクチャ

```text
[スマホ/PC]
    |
[Open WebUI]  ← frontdoor
    |-- 会話
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
    [Git repositories]  ← 正本
```

## 開発文書

- `development-docs/rules/AI_RUNTIME_RULES.md`: AI の実行時安全ルール
- `development-docs/AI_KNOWLEDGE.md`: AI ナレッジの入口
- `development-docs/INDEX.md`: 開発文書の入口
- `development-docs/roadmap/01-initial-roadmap.md`: 現在のロードマップとフェーズ状況
