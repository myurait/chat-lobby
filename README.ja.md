[English](README.md) | 日本語

# ChatLobby

Open WebUI を frontdoor とし、複数の AI エージェント（Claude Code, Codex 等）を背後に接続する
self-hosted 統合チャット基盤。

スマホから自然言語で話しかけるだけで、調査・仕様化・実装依頼・修正依頼・状況確認までを
一貫して行える会話中心の開発基盤を目指す。

## セットアップ

```bash
# 準備中 — Phase A（基盤起動）が進行中
docker compose up -d
```

## 開発

```bash
# 準備中
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

- `development-docs/AI_RUNTIME_RULES.md`: AI の実行時安全ルール
- `development-docs/AI_KNOWLEDGE.md`: AI ナレッジの入口
- `development-docs/INDEX.md`: 開発文書の入口
