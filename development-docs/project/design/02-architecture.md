# Architecture

## System Overview

ChatLobby は、Open WebUI を frontdoor とし、その背後に dispatcher、各種 adapter、
Git 正本を配置する統合チャット基盤である。

```text
[スマホ/PC]
    |
[Open WebUI]
    |-- 会話 / Folders & Projects / Notes
    |-- custom tools / pipelines
    |-- status panel（自作）
            |
    [dispatcher]
      |-- Codex adapter
      |-- Claude adapter
      |-- Git/MCP knowledge adapter
            |
[Git repositories]
      |-- docs/ specs/ decisions/ worklog/
      |-- source code
```

## Operating Model

- frontdoor は Open WebUI で固定する。
- 仕様書、設計書、決定記録、作業ログの正本は Git に固定する。
- Open WebUI 本体への改変は最小化し、拡張は plugin / tool / sidecar / adapter として実施する。
- Open WebUI は upstream をそのまま利用し、fork / vendoring はしない前提で開発する。
- Open WebUI への統合は、Compose 設定、環境変数、PersistentConfig、外部 tool / pipeline / adapter の範囲で行う。
- fork / vendoring が必要だと判断した場合は、その時点でユーザーの意思決定を仰ぐ。
- 公開対象は Open WebUI の fork ではなく、Open WebUI を frontdoor として利用する統合レイヤーとする。
- 無料で self-host する対象は Open WebUI、dispatcher、adapters、status store、status panel、knowledge adapter であり、Claude Code や Codex 自体の利用条件は別管理とする。
- 状態可視化は、adapter から status store への push と、Open WebUI status panel からの read に分離する。

## Boundaries

- Domain logic: dispatcher の routing rule、status model、publish フロー
- Infrastructure and I/O: Open WebUI、Docker、Git リポジトリ
- External dependencies: Claude Code (Agent SDK / CLI)、Codex (app-server API)、Open WebUI

## Worker Roles

- 前面エージェント: Open WebUI 上の統合オペレータ。ユーザーとの会話、仕様整理、ワーカー結果の統合を担当する。
- Claude adapter / Claude Code: ローカル密着ワーカー。ローカル依存の調査、限定修正、網羅的操作を優先的に扱う。
- Codex adapter / Codex: background 実装ワーカー。広い差分、新規プロトタイプ、並列化しやすい作業を優先的に扱う。
- knowledge adapter: Git 正本と関連知識を共通参照可能にする補助層である。

## Data Flow

1. ユーザー → Open WebUI → 前面エージェント（会話）
2. 前面エージェント → dispatcher → 適切なワーカー adapter
3. ワーカー adapter → Claude Code / Codex（実装作業）
4. ワーカー → Git リポジトリ（コード・文書の変更）
5. ワーカー → status store → status panel（状態可視化）
6. ワーカー → 前面エージェント → ユーザー（結果返却）

## Key Interfaces

- dispatcher ↔ adapter: タスク起動・状態取得の共通インターフェース
- adapter ↔ ワーカー: Claude Agent SDK / Codex app-server API
- Open WebUI ↔ plugin: Tools / Pipelines / MCP
- publish tool: 会話 → Git 正本への昇格 API
- adapter ↔ status store: `POST /events` による best-effort status push
- status panel ↔ status store: `GET /tasks`, `GET /tasks/:id` による read-only status query

## Status Model

- `statusId`: `{worker}:{taskId}` で生成する一意識別子
- `worker`: `claude` | `codex` | `knowledge`
- `state`: `running` | `succeeded` | `failed`
- `approvalState`: `not_required` | `may_require_approval` | `bypassed` | `unknown`
- `currentStep`: frontdoor に見せる現在の工程
- `lastAction`: 直近の adapter / worker action
- `resultSummary`: 完了時の要約
- `updatedAt`: status store 上の最終更新時刻

## Status Visibility Principles

前面チャットから見せるべきものは、ワーカーの思考文そのものではなく、実行状態と作業ログである。

- 優先表示項目:
  - task title
  - worker 種別
  - current step
  - branch
  - changed files
  - approval required
  - last tool / last action
  - stopped reason
- think の生表示は主目的にしない。
- Codex / Claude Code 間でイベント粒度が異なっても、status model で正規化して前面へ返す。

## Target Repository Layout

将来の公開可能版では、ChatLobby の統合レイヤーを主役として以下の構成を目標にする。

```text
chatlobby/
  README.md
  docker-compose.yml
  openwebui/
    configs/
  services/
    dispatcher/
    codex-adapter/
    claude-adapter/
    knowledge-adapter/
    status-store/
  plugins/
    openwebui-status-panel/
    openwebui-actions/
  docs/
    architecture/
    operations/
    templates/
  examples/
    sample-project/
```

現時点では全ディレクトリを先行作成せず、Phase の進行に応じて段階的に具体化する。

## Open Questions

- Open WebUI の Pipelines でどこまで dispatcher ロジックを実装可能か
- Claude Code の Remote Control と Agent SDK のどちらを主に使うか
- Codex app-server の安定性と利用可能なイベント粒度
- 会話継続の基盤: 現在は文書ベースの軽量 pilot（`development-docs/project/design/04-conversation-continuity-foundation.md`）で進めている。publish 前の会話文脈の取り扱いが不足と判明した場合、dedicated persistence layer（Feature 012）への移行判断が必要
