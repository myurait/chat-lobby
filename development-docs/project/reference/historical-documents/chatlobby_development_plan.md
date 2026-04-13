# ChatLobby 開発計画書

## 1. 計画の目的

本計画は、Open WebUI を前面の統合チャットとして採用し、その背後に Claude Code と Codex をワーカーとして接続する、会話中心の統合開発基盤「ChatLobby」を段階的に構築するための実行計画を定義するものである。

本計画で実現する到達目標は次のとおりである。

- スマホから前面エージェントに話しかける
- 会話を project / workspace 相当のまとまりに編成する
- 会話からドキュメントを生成し、Git リポジトリへ昇格させる
- Codex / Claude Code のどちらを使うかは基盤側が判断する
- 両者は同じ Git 上の文書とコードを参照する
- 実行中タスク、進行状況、差分、承認待ちを前面チャットから確認する
- 必要に応じて仕様へ差し戻し、更新した仕様を再び共通知識として使う

---

## 2. 採用方針

### 2.1 frontdoor

frontdoor は Open WebUI で固定する。

採用理由は以下のとおりである。

- Folders & Projects、Notes、Channels を持ち、会話単位のまとまりを作りやすい
- Open Terminal により、実際のコードベース・ファイル操作と会話を近接させられる
- Tools、Pipelines、MCP を前提としており、外部ワーカーや共通知識層を接続しやすい
- self-host 前提で導入しやすい

### 2.2 正本

仕様書、設計書、作業ログ、決定記録の正本は Git に固定する。

Open WebUI 内蔵の Notes や Knowledge は草案・補助用とし、最終版は Git リポジトリへ昇格させる。
これにより、Claude Code と Codex が同一の正本を参照できる。

### 2.3 ワーカー

ワーカーの役割は次のように定義する。

- Codex: background 実装ワーカー
- Claude Code: ローカル密着ワーカー
- 前面エージェント: Open WebUI 上の統合オペレータ

### 2.4 状態可視化

前面チャットから確認したいものは、配下ワーカーの「思考文」そのものではなく、実行状態と作業ログである。
したがって、表示対象は以下を基本とする。

- task title
- worker 種別
- current step
- branch
- changed files
- approval required
- last tool / last action
- stopped reason

---

## 3. 最終構成

```text
[スマホ/PC]
    ↓
[Open WebUI]
    ├─ 会話
    ├─ Folders & Projects
    ├─ Notes
    ├─ Channels
    ├─ Open Terminal
    ├─ custom tools / pipelines
    └─ status panel（自作）
            ↓
    [dispatcher]
      ├─ Codex adapter
      ├─ Claude adapter
      └─ Git/MCP knowledge adapter
            ↓
    [Git repositories]
      ├─ docs/
      ├─ specs/
      ├─ decisions/
      ├─ worklog/
      └─ source code
```

この構成では、Open WebUI を単なる LLM UI としてではなく、会話・文書・実行・状態確認のハブとして用いる。

---

## 4. 実装方針

### 4.1 fork 方針

Open WebUI 本体への改変は最小化し、可能な限り plugin / tool / sidecar / adapter として拡張する。
公開時の保守性とライセンス整理を容易にするためである。

### 4.2 公開方針

公開対象は Open WebUI の fork そのものではなく、「Open WebUI を frontdoor として利用する統合レイヤー」とする。

### 4.3 無料セルフホストの意味

無料でセルフホストする対象は、統合基盤そのものである。

具体的には以下を self-host 対象とする。

- Open WebUI
- dispatcher
- adapters
- status store
- status panel
- knowledge adapter

Claude Code や Codex 自体の利用条件や料金体系は別管理とする。

---

## 5. フェーズ別実行計画

以下は実施順である。

### Phase 0. 土台の確立

#### 目的

無料で self-host できる frontdoor と、Git 正本の基本形を成立させる。

#### 実施内容

- Open WebUI を Docker で起動
- 認証を有効化
- Open Terminal を Docker 隔離で有効化
- File Browser が使える状態にする
- 共有 Git リポジトリを1つ用意
- `docs/`, `specs/`, `decisions/`, `worklog/` の初期構成を固定

#### 成果物

- `infra/docker-compose.yml`
- `docs/project-template/`
- 初期運用 README

#### 完了条件

- スマホブラウザから Open WebUI に入り、会話、Notes、ファイル閲覧ができる
- Open Terminal 経由でテスト用 repo を clone し、ファイルを見られる

### Phase 1. 会話から Git 正本への昇格

#### 目的

会話内容や Notes を、仕様書・決定記録として Git 正本へ昇格させる流れを固定する。

#### 実施内容

- Open WebUI の Folders & Projects を project 単位で利用
- Notes を草案置き場として使う
- custom tool を追加し、会話や Notes から Markdown を生成して repo に保存
- 生成先を `docs/specs/`, `docs/decisions/` などに固定
- commit message のテンプレートを定める

#### 成果物

- `tools/publish_to_repo`
- `docs/templates/spec.md`
- `docs/templates/adr.md`

#### 完了条件

- 会話中に「これを元に仕様書を作成して」で Markdown が repo に保存される
- Open WebUI の File Browser からそのファイルが見える

### Phase 2. Codex / Claude Code 接続

#### 目的

前面エージェントから配下ワーカーを起動し、同じ repo を見て作業できるようにする。

#### 実施内容

- Codex adapter を作成
  - app-server 接続
  - task 作成
  - approvals 受信
  - streamed events 取得
- Claude adapter を作成
  - Agent SDK または CLI 制御
  - Hooks 受信
  - Remote Control 用 session 情報の保持
- Git/MCP adapter を作成
  - repo パス
  - current branch
  - specs/worklog 参照
- Open WebUI 側に action を追加
  - 「Codex に依頼」
  - 「Claude に依頼」
  - 「自動振り分け」

#### 成果物

- `services/codex-adapter/`
- `services/claude-adapter/`
- `services/knowledge-adapter/`

#### 完了条件

- Open WebUI 上の会話から Codex / Claude の起動ができる
- 両者が同じ repo を見て作業できる

### Phase 3. 自動振り分け

#### 目的

Claude / Codex のどちらを使うかを、ユーザーが都度判断しなくてよい状態にする。

#### 実施内容

- dispatcher の routing rule を作成
- 初期はルールベースで開始する
- 例:
  - 新規プロトタイプ、広い差分、並列化向き → Codex
  - ローカル依存、不具合調査、限定修正、網羅的操作 → Claude
  - 仕様差し戻し、要件整理 → 前面エージェント
- ルーティング結果を会話に明示表示
- 手動 override も残す

#### 成果物

- `services/dispatcher/rules.yaml`
- `docs/operations/routing-policy.md`

#### 完了条件

- ユーザーが「実装して」「この不具合を直して」と言うだけで、基盤側が候補を決める

### Phase 4. 状態可視化

#### 目的

何のタスクを実行中で、どこまで進んでいるかを前面チャットから把握できるようにする。

#### 実施内容

- Codex app-server の streamed agent events を収集
- Claude Hooks / Agent SDK のイベントを収集
- status store を作成
- Open WebUI に status panel を追加
- 表示項目:
  - worker
  - task title
  - status
  - current step
  - last tool/action
  - branch
  - changed files
  - approval required
- think の生表示は主目的にしない
- 代わりに「実行状態」と「作業ログ」を見せる

#### 成果物

- `services/status-store/`
- `plugins/openwebui-status-panel/`
- `docs/operations/status-model.md`

#### 完了条件

- スマホから現在進行中のタスクと停止理由が見える
- approval 待ちが分かる

### Phase 5. 仕様差し戻しループ

#### 目的

実装結果から仕様書を更新し、次回以降の共通知識として再利用できるようにする。

#### 実施内容

- worklog 自動生成
- changed files の要約
- 実装結果を前面エージェントへ返却
- action を追加
  - 「この実装をもとに仕様更新」
  - 「この変更を decisions に反映」
- 差分から spec / ADR / worklog を再生成

#### 成果物

- `tools/update_spec_from_changes`
- `tools/update_adr_from_changes`
- `docs/operations/spec-feedback-loop.md`

#### 完了条件

- 実装後に仕様更新が会話から行える
- 更新版仕様が次回以降の主要ナレッジになる

---

## 6. リポジトリ構成案

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

この構成では、公開物の主役を ChatLobby の統合レイヤーとし、Open WebUI 本体との差分を最小化する。

---

## 7. マイルストーン

### Milestone 1

Open WebUI + Git 正本 + Notes/Projects 運用

### Milestone 2

会話から Markdown を repo に publish

### Milestone 3

Codex / Claude の片方だけ先につなぐ

優先順位は、スマホからの live 状態確認を重視するなら Claude 側を先行とする。

### Milestone 4

自動振り分け

### Milestone 5

状態パネル

### Milestone 6

仕様差し戻しループ

---

## 8. この計画の要約

「Open WebUI を frontdoor に採用し、Git を正本とし、Codex と Claude Code を背後ワーカーとして接続し、会話から仕様・実装・差し戻しまでを一貫して扱える self-hosted 統合チャット基盤 ChatLobby を段階的に構築する」
