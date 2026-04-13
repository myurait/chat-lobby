# Initial Roadmap

## Current Phase

- Phase: Complete
- Focus: Initial roadmap scope is complete through Phase F. Further work belongs in `features/`.

## Phase Policy

- まず「会話 → 文書化 → Git 昇格 → ワーカー依頼」の最短ループを成立させる。
- Open WebUI 本体改変は最小化し、plugin / tool / sidecar / adapter を基本とする。
- 各フェーズは、前フェーズの完了条件を満たしてから次へ進む。

## Phases

### Phase A: 基盤起動
- 目的: ChatLobby の最小 self-host 環境を成立させる。
- 成功判定:
  - Open WebUI が Docker で起動する
  - スマホからログインして会話できる
  - Notes / Folders & Projects / File Browser が使える
  - Open Terminal からテスト用 repo を扱える
- [x] プロジェクトチャーター策定
- [x] docker-compose.yml 作成（Open WebUI 起動）
- [x] 認証の有効化
- [x] Open Terminal の Docker 隔離有効化
- [x] File Browser が使える状態にする
- [x] 共有 Git リポジトリの初期構成を固定
- [x] スマホからの接続確認

### Phase B: 正本化フロー
- 目的: 会話内容や Notes を Markdown 文書として Git に昇格させる。
- [x] publish tool の作成
- [x] Markdown テンプレート整備
- [x] 文書配置規約の策定
- [x] 会話から spec / ADR / worklog を Git に保存可能にする

### Phase C: 単一ワーカー接続（Claude Code 優先）
- 目的: 前面チャットから、まずは 1 種類の実装ワーカーを起動できるようにする。
- [x] Claude adapter の作成
- [x] 最低限の task 実行 UI
- [x] 作業結果のチャット返却

### Phase D: 両ワーカー接続
- 目的: Codex / Claude Code の双方を ChatLobby 配下に置く。
- [x] Codex adapter の作成
- [x] knowledge adapter の作成
- [x] 手動ワーカー選択の実装

### Phase E: 自動振り分け
- 目的: ユーザーが Claude / Codex を選ばなくてよい状態を作る。
- [x] dispatcher の作成
- [x] routing rules の定義
- [x] routing policy ドキュメント

### Phase F: 状態可視化
- 目的: 配下ワーカーの作業状態を前面チャットから確認できるようにする。
- [x] status store の作成
- [x] status panel の作成
- [x] approval 可視化
- [x] adapter と status store の状態伝搬方式を ADR で固定

## Moved To Feature Backlog

- 仕様差し戻しループの tool 化は、現段階の initial roadmap から外し、`features/01-feature-backlog.md` で管理する。
- 他者が試せる状態へ整える公開準備も、次フェーズの目的とはせず、`features/01-feature-backlog.md` で管理する。

## Deferred Cross-Cutting Tasks

- [ ] plugin / tools directory strategy を見直し、長期構成と ADR を定義する。
- [ ] front agent の実現方式を ADR として固定する。
- [ ] 長大 request の offload 方式を設計し、request body / prompt length の扱いを統一する。
- [ ] direct pipe の同期 polling を将来どう縮退させるかを決め、dispatch / status 導線へ寄せる。

## Release Targets

- v0.1: Phase A + B + C（会話 → 文書 → 実装依頼の最短ループ）
- v0.2: Phase D（複数ワーカー統合）
- v0.3: Phase E + F（自動振り分け + 状態可視化）

## Initial Priority

1. Open WebUI + Git 正本の成立
2. 文書 publish フロー
3. Claude Code 接続
4. Codex 接続
5. 自動振り分け
6. 状態パネル

## Risks and Mitigations

### Open WebUI 依存の偏り

- Risk: Open WebUI への依存が強すぎると、将来的な置換が難しくなる。
- Mitigation: 本体改変は最小化し、plugin / sidecar / adapter を基本とする。

### ワーカー状態可視化の不統一

- Risk: Codex と Claude Code のイベント粒度が異なり、統一表示が難しい。
- Mitigation: status model を先に定義し、各ワーカー側で正規化する。

### 正本化の手間

- Risk: 会話から Git 正本へ昇格する作業が億劫になり、運用が途切れる。
- Mitigation: publish action を frontdoor 上のワンアクションに寄せ、文書テンプレートと保存先規約を固定する。

### ChatGPT 依存の期待値ずれ

- Risk: ChatGPT Projects 的体験を frontdoor 側で完全再現できるとは限らない。
- Mitigation: ChatLobby は ChatGPT 互換ではなく、「会話から実装チームを動かす frontdoor」として価値定義する。

## Notes

Update this file at the end of each development cycle.

### 2026-04-05

- `docker-compose.yml` と `.env.example` を追加し、Open WebUI / Ollama / Open Terminal の最小起動構成を定義。
- Open Terminal は Compose 内部ネットワーク経由で事前配線し、端末 API のホスト公開を避ける方針にした。
- 次タスクは認証の実起動確認と、初回ログイン手順を含む運用確認。

### 2026-04-05 文書正規化

- `reference/historical-documents` の内容のうち、運用境界、ワーカー役割、状態可視化方針、リポジトリ構成目標、初期優先順位、主要リスクを現行文書へ移送した。
- 以後、歴史的経緯の確認を除き、通常作業で `reference/historical-documents` を読む前提を置かない。
- `reference/my-project-template/` をローカル参照用に clone し、開発ドキュメンテーションルールの正本参照元として位置づけた。clone 自体は Git 管理から除外した。
- 文書粒度ルールを `knowledge.md` に明記し、肥大化していた `rules/coding-conventions.md` を `rules/development-process.md` へ分割した。
- 原則不変の規約文書を `rules/` 配下へ集約し、通常作業で更新しない文書群として分離した。
- `open-terminal` のホスト側作業領域を `./workspace` mount に限定し、`workspace/templates/chatlobby-canonical/` に共有正本テンプレートを追加した。
- この変更により、Phase A の「Open Terminal の Docker 隔離有効化」と「共有 Git リポジトリの初期構成を固定」を実装面で完了とした。
- `open-webui` をローカル起動し、admin sign-in 成功と public sign-up 拒否を確認した。あわせて Open WebUI 経由で terminal server verify と `/workspace` の file listing を確認し、認証と File Browser を完了扱いにした。
- 実機スマホからのログイン確認が完了し、Phase A を完了扱いとした。
- 次タスクは Phase B の `publish tool の作成` と `Markdown テンプレート整備` の着手である。
- `tools/publish_to_repo.py`、`docs/templates/`、`docs/operations/document-placement.md` を追加し、Phase B の CLI ベース正本化を開始した。
- 残る Phase B 項目は、Open WebUI の会話や Notes からこの publish flow を直接呼び出せるようにする統合作業である。
- `chatlobby_publish` function pipe を Open WebUI に登録し、会話 API から `publish_to_repo.py` を呼び出して canonical repo へ Markdown を保存できることを確認した。
- これにより Phase B を完了扱いとし、次タスクを Phase C の Claude Code 接続へ進める。
- `services/claude-adapter/src/server.ts` を追加し、`claude -p --output-format json` を包むローカル HTTP adapter を実装した。
- `POST /tasks` で task を受け付け、`GET /tasks/:id` で `succeeded` まで到達することを確認した。
- `chatlobby_claude_task` function pipe を Open WebUI に登録し、会話 API から Claude adapter を呼び、結果が前面チャットへ返ることを確認した。
- これにより Phase C を完了扱いとし、次タスクを Phase D の Codex 接続へ進める。
- `services/codex-adapter/src/server.ts` を追加し、`codex exec --json` を包むローカル HTTP adapter を実装した。
- `chatlobby_codex_task` function pipe を Open WebUI に登録し、会話 API から Codex adapter を呼び、結果が前面チャットへ返ることを確認した。
- `services/knowledge-adapter/src/server.ts` を追加し、canonical repo の検索・読取 API を提供する knowledge adapter を実装した。
- `chatlobby_knowledge_query` function pipe を Open WebUI に登録し、会話 API から canonical repo の検索結果を返せることを確認した。
- Open WebUI の model 選択により、`ChatLobby Claude Task` / `ChatLobby Codex Task` / `ChatLobby Knowledge Query` を手動で切り替えられる状態になった。
- これにより Phase D を完了扱いとし、次タスクを Phase E の dispatcher と routing rules へ進める。
- `services/dispatcher/src/server.ts` と `services/dispatcher/rules.json` を追加し、Codex / Claude / knowledge を rule-based に自動選択する dispatcher を実装した。
- `docs/operations/routing-policy.md` に routing rule と override 方針を記録した。
- `chatlobby_dispatch_task` function pipe を Open WebUI に登録し、plain text の `実装して` / `この不具合を直して` / `README.ja.md を検索して` がそれぞれ Codex / Claude / knowledge に自動振り分けされることを確認した。
- knowledge adapter には file path match fallback を追加し、自然言語からのファイル名検索にも最低限対応した。
- これにより Phase E を完了扱いとし、次タスクを Phase F の status store と status panel へ進める。
- review 018 の follow-up として、`services/shared/` へ HTTP / task trimming utility を抽出し、host 側 adapter / dispatcher に共通 bearer token 認証を追加した。
- `.env.example`、README、Open WebUI pipe valves に `CHATLOBBY_INTERNAL_API_TOKEN` と Node 22+ 前提を反映した。
- review 018 で deferred 扱いになった plugin 構成見直し、front agent ADR、長大 request offload、direct pipe polling の論点を後続タスクと tech debt registry に追加した。
- `services/status-store/src/server.ts` と `services/shared/status.ts` を追加し、Claude / Codex / knowledge の task 状態を `statusId` 単位で正規化する central status store を実装した。
- `tools/openwebui/chatlobby_status_panel_pipe.py` と `tools/sync_openwebui_status_pipe.py` を追加し、Open WebUI frontdoor から status list / detail を参照できる status panel を実装した。
- `approvalState` を `not_required` / `may_require_approval` / `bypassed` / `unknown` に正規化し、Codex / Claude / knowledge の status 表示へ載せた。
- `tests/test_status_store.py` と adapter / knowledge test 更新により、status store の merge / trim / auth と `statusId` 伝搬を自動検証した。
- Open WebUI に `chatlobby_status_panel` を同期し、`status` の chat completion が `worker` / `state` / `approval` / `step` を返すことを確認した。
- これにより Phase F をもって initial roadmap scope を完了扱いとした。
- 仕様差し戻しループの tool 化と公開準備は、次フェーズではなく feature backlog へ移して別管理にした。
