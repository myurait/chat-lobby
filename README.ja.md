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
もしローカルで `3000` 番ポートが既に使われている場合は、起動前に `.env` の
`OPEN_WEBUI_PORT` と `WEBUI_URL` を `3001` などへ変更する。

Open Terminal は Docker 内ネットワークで事前接続するため、端末 API をホストへ直接公開せずに
Open WebUI からターミナルと File Browser を利用できる。
また、ホスト側の [`workspace/`](/Users/fox4foofighter/dev/chat-lobby/workspace/README.md) を
コンテナ内 `/workspace` に専用作業領域として mount する。

## 開発

```bash
# Compose 定義の検証
WEBUI_SECRET_KEY=test-secret \
WEBUI_ADMIN_EMAIL=admin@example.com \
WEBUI_ADMIN_PASSWORD=test-password \
OPEN_TERMINAL_API_KEY=test-terminal-key \
docker compose config

# 共有正本レイアウトへ spec を publish
python3 tools/publish_to_repo.py \
  --repo workspace/templates/chatlobby-canonical \
  --kind spec \
  --title "Example feature spec" \
  --body "Initial summary"

# Open WebUI に publish pipe を登録
python3 tools/sync_openwebui_publish_pipe.py \
  --webui-url http://localhost:3000 \
  --email admin@example.com \
  --password chatlobby-admin-password

# ローカル Claude adapter を起動
node services/claude-adapter/src/server.ts

# Open WebUI に Claude task pipe を登録
python3 tools/sync_openwebui_claude_pipe.py \
  --webui-url http://localhost:3000 \
  --email admin@example.com \
  --password chatlobby-admin-password

# Open WebUI に Codex task pipe を登録
python3 tools/sync_openwebui_codex_pipe.py \
  --webui-url http://localhost:3000 \
  --email admin@example.com \
  --password chatlobby-admin-password

# Open WebUI に knowledge query pipe を登録
python3 tools/sync_openwebui_knowledge_pipe.py \
  --webui-url http://localhost:3000 \
  --email admin@example.com \
  --password chatlobby-admin-password

# Open WebUI に dispatch pipe を登録
python3 tools/sync_openwebui_dispatch_pipe.py \
  --webui-url http://localhost:3000 \
  --email admin@example.com \
  --password chatlobby-admin-password
```

`OPEN_WEBUI_PORT` を変更した場合は、この URL も合わせて置き換える。

## 共有 Git リポジトリテンプレート

- `workspace/templates/chatlobby-canonical/` に、共有正本 Git リポジトリの初期ディレクトリ構成を置く。
- `workspace/repos/` は Open Terminal から clone した実運用リポジトリや一時作業置き場として使う。
- 専用 workspace mount により、端末が参照するホスト側作業領域を意図した範囲に限定する。
- `tools/publish_to_repo.py` は、共有正本レイアウトへテンプレート付き Markdown を保存する CLI である。
- `tools/openwebui/chatlobby_publish_pipe.py` は、会話から publish を呼び出す Open WebUI 用 pipe である。
- `tools/sync_openwebui_publish_pipe.py` は、その pipe を Open WebUI 管理 API 経由で登録・更新するための補助 CLI である。

## 会話から publish

pipe を同期した後、Open WebUI で `ChatLobby Publish` モデルを選び、次のような JSON を送る。

```json
{
  "kind": "spec",
  "title": "Example feature spec",
  "body": "Summarize the feature here.",
  "slug": "example-feature-spec"
}
```

pipe は canonical repo へ文書を書き込み、保存先パスを返す。

## Claude Adapter

Phase C の最初の adapter は、`claude -p --output-format json` を包むローカル HTTP サービスである。

```bash
# Open WebUI から使う場合は host から到達できる bind で起動
CLAUDE_ADAPTER_HOST=0.0.0.0 node services/claude-adapter/src/server.ts

# Claude task を作成
curl -X POST http://127.0.0.1:8787/tasks \
  -H 'Content-Type: application/json' \
  -d '{"prompt":"Reply with exactly ok.","workingDirectory":"'"$(pwd)"'"}'

# task 状態を確認
curl http://127.0.0.1:8787/tasks/<task-id>
```

pipe を同期した後、Open WebUI で `ChatLobby Claude Task` モデルを選び、次のような JSON を送る。

```json
{
  "prompt": "Reply with exactly ok.",
  "workingDirectory": "/Users/you/path/to/repo"
}
```

pipe はローカル Claude adapter に task を作成し、完了結果を会話へ返す。

## Codex Adapter

Codex adapter も Claude adapter と同じパターンで、`codex exec --json` を包むローカル HTTP サービスである。

```bash
# Open WebUI から使う場合は host から到達できる bind で起動
CODEX_ADAPTER_HOST=0.0.0.0 node services/codex-adapter/src/server.ts

# 明示的に無人実行を許可したい場合だけ opt-in する
CODEX_ADAPTER_HOST=0.0.0.0 \
CODEX_BYPASS_APPROVALS_AND_SANDBOX=true \
node services/codex-adapter/src/server.ts

# Codex task を作成
curl -X POST http://127.0.0.1:8788/tasks \
  -H 'Content-Type: application/json' \
  -d '{"prompt":"Reply with exactly ok.","workingDirectory":"'"$(pwd)"'"}'

# task 状態を確認
curl http://127.0.0.1:8788/tasks/<task-id>
```

pipe を同期した後、Open WebUI で `ChatLobby Codex Task` モデルを選び、次のような JSON を送る。

```json
{
  "prompt": "Reply with exactly ok.",
  "workingDirectory": "/Users/you/path/to/repo"
}
```

adapter の default は `workspace-write` sandbox で、approval bypass は無効である。無人実行が必要な場合だけ
`CODEX_BYPASS_APPROVALS_AND_SANDBOX=true` を明示指定する。

## Knowledge Adapter

knowledge adapter は canonical repo に対する検索・読取 API を提供するローカル HTTP サービスである。

```bash
# Open WebUI から使う場合は host から到達できる bind で起動
KNOWLEDGE_ADAPTER_HOST=0.0.0.0 node services/knowledge-adapter/src/server.ts

# canonical knowledge を検索
curl -X POST http://127.0.0.1:8789/search \
  -H 'Content-Type: application/json' \
  -d '{"query":"ChatLobby"}'
```

pipe を同期した後、Open WebUI で `ChatLobby Knowledge Query` モデルを選び、次のような JSON を送る。

```json
{
  "query": "ChatLobby"
}
```

## Dispatcher

dispatcher は `services/dispatcher/rules.json` のルールベース判定で Claude / Codex / knowledge を自動選択する。

```bash
# Open WebUI から使う場合は host から到達できる bind で起動
DISPATCHER_HOST=0.0.0.0 node services/dispatcher/src/server.ts

# 自動振り分けを直接確認
curl -X POST http://127.0.0.1:8790/dispatch \
  -H 'Content-Type: application/json' \
  -d '{"prompt":"実装して。Reply with exactly ok.","workingDirectory":"'"$(pwd)"'"}'
```

pipe を同期した後、Open WebUI で `ChatLobby Dispatch Task` モデルを選び、まずは次のような plain text を送ればよい。

```text
実装して
```

`workerHint`、`repoPath`、`workingDirectory` のような override が必要な場合だけ JSON を送る。

## 手動確認

1. `.env` の管理者アカウントでログインする。
2. 公開サインアップが拒否されることを確認する。
3. Open WebUI から Open Terminal を開き、`/workspace` が見えることを確認する。
4. terminal の file tools または File Browser で `/workspace` を列挙し、`repos/` と `templates/` が見えることを確認する。
5. スマホ確認では、同一ネットワーク上の端末から `http://<LAN内IP>:<OPEN_WEBUI_PORT>` を開く。
6. `chatlobby_publish` を同期し、`ChatLobby Publish` モデルで送った会話が `/workspace/templates/chatlobby-canonical/` に保存されることを確認する。
7. Claude adapter を `CLAUDE_ADAPTER_HOST=0.0.0.0` で起動し、`chatlobby_claude_task` を同期したうえで、`ChatLobby Claude Task` モデルが完了結果を会話へ返すことを確認する。
8. Codex adapter を `CODEX_ADAPTER_HOST=0.0.0.0` で起動し、`chatlobby_codex_task` を同期したうえで、`ChatLobby Codex Task` モデルが完了結果を会話へ返すことを確認する。
9. knowledge adapter を `KNOWLEDGE_ADAPTER_HOST=0.0.0.0` で起動し、`chatlobby_knowledge_query` を同期したうえで、`ChatLobby Knowledge Query` モデルが canonical repo の検索結果を返すことを確認する。
10. dispatcher を `DISPATCHER_HOST=0.0.0.0` で起動し、`chatlobby_dispatch_task` を同期したうえで、`実装して`、`この不具合を直して`、`README.ja.md を検索して` のような plain text がそれぞれ Codex / Claude / knowledge に自動振り分けされることを確認する。

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
