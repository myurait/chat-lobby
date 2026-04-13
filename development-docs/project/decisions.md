# Architecture Decision Log

Record all non-trivial architecture, policy, and operational decisions.

---

## ADR-001: frontdoor として Open WebUI を採用

- Date: 2026-04-05
- Status: Accepted
- Context: 統合チャット基盤の frontdoor として、既存 OSS から選定する必要があった。Folders & Projects、Notes、Channels、Open Terminal、Tools/Pipelines/MCP 対応を持ち、self-host 前提で導入しやすい Open WebUI が最適と判断。
- Decision: Open WebUI を frontdoor として採用し、本体改変は最小化する。Open WebUI は upstream を利用し、fork / vendoring はしない前提で開発する。拡張は plugin / tool / sidecar / adapter として行う。fork / vendoring がどうしても必要になった場合は、実施前にユーザーの意思決定を仰ぐ。
- Consequences: Open WebUI のバージョンアップへの追従が必要。本体改変を最小化することで、保守性とライセンス整理が容易になる。統合は Compose 設定、環境変数、PersistentConfig、外部 tool / pipeline / adapter の範囲で組み立てる前提になる。

---

## ADR-002: 文書の正本を Git に固定

- Date: 2026-04-05
- Status: Accepted
- Context: 仕様書・設計書・作業ログ・決定記録の正本をどこに置くかの決定が必要だった。Open WebUI 内蔵の Notes / Knowledge は草案・補助用としては使えるが、Claude Code / Codex が同一の正本を参照するには Git が適切。
- Decision: 正本は Git リポジトリに固定する。Open WebUI 内の Notes / Knowledge は草案用途とする。
- Consequences: publish フロー（会話 → Git）の構築が必須となる。Claude Code / Codex が同一の正本を参照可能になる。

---

## ADR-003: ワーカー接続順序として Claude Code を優先

- Date: 2026-04-05
- Status: Accepted
- Context: Codex / Claude Code の両方を接続する必要があるが、同時開発は負荷が高い。スマホからの状態確認価値が高く、Remote Control と組み合わせた体験を早期に検証できる Claude Code を先行させる。
- Decision: Phase C で Claude Code 接続を先行し、Phase D で Codex を追加する。
- Consequences: Claude Code の API / SDK に対する深い理解が先に必要になる。Codex 接続は後続フェーズに持ち越し。

---

## ADR-004: 開発言語の主従と文書言語・コミットメッセージ言語の決定

- Date: 2026-04-05
- Status: Accepted
- Context: 個人プロジェクトとして、開発効率と可読性のバランスを取る必要がある。
- Decision: 開発言語は TypeScript を主とする。dispatcher、各 adapter、status store、status panel、knowledge adapter、正本化フローの恒常的な統合ロジックなど、ChatLobby の中核実装は TypeScript で行う。Python は Open WebUI の custom tool / function / pipeline、起動補助、検証用 CLI、小規模な運用補助スクリプトなど、Open WebUI 連携や補助用途に限定する。文書言語は日本語、コミットメッセージ言語は日本語とする。
- Consequences: コード中のコメント・識別子・テスト名は英語（coding-conventions に従う）。中核ロジックを Python に広げる場合は、TypeScript 主体の原則から外れるため、別途判断理由を明示する必要がある。プロジェクト文書と開発ログは日本語で記述する。

---

## ADR-005: Phase A の初期スタックは Compose 内部接続で Open Terminal を事前配線する

- Date: 2026-04-05
- Status: Accepted
- Context: Phase A では、認証付き Open WebUI と Docker 隔離された Open Terminal と File Browser を最短で成立させる必要がある。端末 API をホストに直接露出すると、初期構成として不要な攻撃面が増える。
- Decision: `docker-compose.yml` では Open WebUI、Open Terminal、Ollama を同一 Compose ネットワークに載せ、Open WebUI 側から `TERMINAL_SERVER_CONNECTIONS` で `http://open-terminal:8000` を事前設定する。Open Terminal の API キーは `.env` から注入し、ホストへのポート公開は行わない。
- Consequences: 初回起動後すぐに Open WebUI からターミナルと File Browser を利用できる。Terminal 接続設定は Open WebUI の PersistentConfig に保存されるため、再設定時は Admin UI またはデータボリューム初期化の理解が必要になる。

---

## ADR-006: Open Terminal は専用 workspace mount と共有正本テンプレートを使う

- Date: 2026-04-05
- Status: Accepted
- Context: Phase A の残課題として、Open Terminal の Docker 隔離をより明確にしつつ、背後ワーカーと frontdoor が参照する共有 Git リポジトリ構成を固定する必要があった。ホスト全体を terminal へ見せる構成は不要に広い。
- Decision: `open-terminal` にはホストの `./workspace` のみを `/workspace` として bind mount し、ここを専用作業領域とする。さらに `workspace/templates/chatlobby-canonical/` に、`docs/`, `specs/`, `decisions/`, `worklog/`, `src/` を持つ共有正本テンプレートを配置する。
- Consequences: Terminal と File Browser が扱うホスト領域を限定できる。Phase B 以降の publish tool や文書配置規約は、このテンプレート構成を前提に設計しやすくなる。実運用 clone は `workspace/repos/` に分離して root リポジトリから除外する必要がある。

---

## ADR-007: Phase B の正本化はローカル CLI publish tool から始める

- Date: 2026-04-05
- Status: Accepted
- Context: Phase B の最初の到達点は、会話や Notes から確定した内容を Git 正本へ昇格させる流れの固定である。いきなり Open WebUI plugin や pipeline に埋め込むより、まずは deterministic な CLI を作って文書配置規約とテンプレートを固める方が安全だった。
- Decision: 最初の publish 実装は `tools/publish_to_repo.py` とし、`docs/templates/` と `docs/operations/document-placement.md` を正本化フローの基準にする。Open WebUI からの直接実行は後続タスクとする。
- Consequences: まず CLI 経由で spec / ADR / worklog の保存先とテンプレートを固定できる。次フェーズでは、この CLI を tool / pipeline / adapter から呼び出す統合作業が必要になる。

---

## ADR-008: Phase B の Open WebUI 統合は upstream function pipe から外部 CLI を呼ぶ

- Date: 2026-04-05
- Status: Accepted
- Context: Phase B を完了するには、Open WebUI の会話から spec / ADR / worklog を Git 正本へ保存できる必要がある。一方で、ADR-001 により Open WebUI は fork / vendoring しない前提であり、upstream 互換を崩さずに統合する必要があった。
- Decision: Open WebUI との publish 統合は、custom `Pipe` function として `chatlobby_publish` を登録し、その中から bind mount 済みの `tools/publish_to_repo.py` を呼び出す方式にする。Open WebUI 本体コードは変更せず、Compose mount、管理 API、function registry の範囲で統合する。
- Consequences: 会話から正本へ保存する最短経路を upstream 互換のまま成立できる。現在の publish 入力形式は構造化 JSON を前提にするため、自然言語や Notes からの昇格 UX は後続フェーズで改善余地が残る。

---

## ADR-009: Phase C の最初の Claude 接続はローカル CLI を包む HTTP adapter とする

- Date: 2026-04-05
- Status: Accepted
- Context: Phase C の最初の目標は、前面チャットから 1 種類の実装ワーカーを起動できる状態を作ることである。Claude Code にはローカル CLI が既に存在し、これを最小の adapter で包めば、Open WebUI や dispatcher から呼ぶ前段の実行面を早く固定できる。
- Decision: 最初の Claude adapter は `services/claude-adapter/src/server.ts` とし、Node 組み込み HTTP サーバーから `claude -p --output-format json` を起動するローカル sidecar とする。通信面は `POST /tasks`, `GET /tasks`, `GET /tasks/:id`, `GET /health` の最小 API に絞る。
- Consequences: 依存追加なしで Claude Code の task 実行面を先に検証できる。現段階では Open WebUI の task 実行 UI や chat 返却との直結は未実装であり、Phase C の残タスクとして後続に残る。

---

## ADR-010: Phase C の frontdoor 統合は Open WebUI pipe から Claude adapter を呼ぶ

- Date: 2026-04-05
- Status: Accepted
- Context: Phase C を完了するには、Claude adapter 単体だけでなく、Open WebUI の前面チャットから task を起動し、その結果を会話に返す必要がある。ここでも Open WebUI を fork / vendoring せず、upstream extension point の範囲で統合する必要があった。
- Decision: `chatlobby_claude_task` custom `Pipe` function を Open WebUI に登録し、その中から `http://host.docker.internal:8787` の Claude adapter API を呼ぶ。adapter は Open WebUI コンテナから到達できるように host 側で `CLAUDE_ADAPTER_HOST=0.0.0.0` で起動する。
- Consequences: 最低限の task 実行 UI は「Open WebUI で model を選んで JSON を送る」形で成立し、結果も会話へ返せる。現段階では task 状態の継続表示や richer UI はなく、後続の dispatcher / status panel フェーズで補う必要がある。

---

## ADR-011: Phase D の Codex 接続は Claude と同型の adapter / pipe 境界で実装する

- Date: 2026-04-05
- Status: Accepted
- Context: Phase D では、Claude Code に加えて Codex も同一 frontdoor 配下へ置く必要がある。運用と保守の一貫性を保つには、Claude 側と同型の adapter / pipe 境界で揃えるのが妥当だった。
- Decision: `services/codex-adapter/src/server.ts` を追加し、`codex exec --json` を包むローカル HTTP adapter とする。Open WebUI 側は `chatlobby_codex_task` custom `Pipe` function から `http://host.docker.internal:8788` の adapter API を呼ぶ。
- Consequences: Claude / Codex の task API 形状を揃えやすくなり、後続の dispatcher や status 正規化に接続しやすい。現時点では Codex も JSON 入力前提の簡素な task UI であり、操作性の洗練は後続タスクに残る。

---

## ADR-012: Phase D の knowledge adapter は canonical repo の検索・読取 sidecar とする

- Date: 2026-04-05
- Status: Accepted
- Context: Phase D では、文書正本を worker と frontdoor の双方から共通参照できる knowledge adapter が必要である。まずは canonical repo の検索・読取を薄い sidecar に切り出す方が、MCP や retrieval を直接抱え込むより安全だった。
- Decision: `services/knowledge-adapter/src/server.ts` を追加し、canonical repo に対する `search` / `read` API を提供するローカル HTTP adapter とする。Open WebUI 側は `chatlobby_knowledge_query` custom `Pipe` function から `http://host.docker.internal:8789` を呼ぶ。
- Consequences: Open WebUI frontdoor から canonical repo の検索・読取を直接使える。将来的に MCP や vector retrieval を組み込む場合も、この adapter 境界の内側で差し替えやすい。

---

## ADR-013: Phase E の自動振り分けは rule-based dispatcher と plain-text frontdoor から始める

- Date: 2026-04-05
- Status: Accepted
- Context: Phase E では、ユーザーが Claude / Codex を都度選ばずに `実装して` や `この不具合を直して` のような自然言語依頼だけで基盤側が候補を決める必要がある。初期段階でモデル判定に寄せすぎると、debug 性と説明可能性が落ちる。
- Decision: `services/dispatcher/src/server.ts` を追加し、`services/dispatcher/rules.json` に定義した rule-based routing で `claude` / `codex` / `knowledge` を自動選択する。Open WebUI 側は `chatlobby_dispatch_task` custom `Pipe` function を追加し、plain text はそのまま `prompt` として受け付け、override が必要な場合のみ JSON を使う。routing 結果と理由は会話へ明示表示する。
- Consequences: `実装`, `不具合`, `検索` などの類型で deterministic に振り分けでき、routing policy も文書化しやすい。現段階では semantic classification や multi-worker orchestration はなく、ルール更新は `rules.json` と `docs/operations/routing-policy.md` の同期で運用する。

---

## ADR-014: host 側 adapter / dispatcher は bearer token で保護する

- Date: 2026-04-05
- Status: Accepted
- Context: `CLAUDE_ADAPTER_HOST=0.0.0.0` などの bind を README で案内しているため、同一ネットワーク上から task 作成 API へ到達できる状態が発生していた。review 018 で、adapter API に認証がない点が High risk として指摘された。
- Decision: `claude-adapter`、`codex-adapter`、`knowledge-adapter`、`dispatcher` は `CHATLOBBY_INTERNAL_API_TOKEN` を共通 bearer token として受け付ける。非 loopback bind の場合は token 未設定で起動しない。Open WebUI 側の各 pipe も `api_bearer_token` valve で同 token を送る。
- Consequences: host 側 service を `0.0.0.0` で bind しても、token を知らないクライアントは task / search / dispatch API を使えない。今後、より細かい認可や rotate 方針が必要になった場合は、この token 境界の内側で拡張する。

---

## ADR-015: Phase F の状態可視化は adapter push 型の central status store で正規化する

- Date: 2026-04-05
- Status: Accepted
- Context: Phase F では、Claude / Codex / knowledge の進捗を frontdoor から一貫した形式で見えるようにする必要がある。worker ごとのイベント粒度は異なり、dispatcher や Open WebUI pipe が個別 polling で吸収すると重複実装が増える。
- Decision: 各 adapter は task 開始・完了・失敗の節目で、正規化済み `StatusEvent` を `status-store` の `/events` へ best-effort で push する。`status-store` は `statusId = {worker}:{taskId}` を key に `running` / `succeeded` / `failed`、`approvalState`、`currentStep`、`lastAction`、`resultSummary` を保持し、Open WebUI 側の `chatlobby_status_panel` は `/tasks` と `/tasks/:id` を読むだけにする。
- Consequences: frontdoor 側は worker 差分ではなく共通の status model のみを扱えばよくなり、approval 可視化も `approvalState` で揃えられる。status 伝搬は best-effort なので task 完了を status publication failure で失敗させない。一方で現時点の `status-store` は in-memory のため、再起動を跨ぐ履歴保持は後続課題として残る。

---

## ADR-016: エージェントロール定義の格納先として development-docs/rules/roles/ を新設する

- Date: 2026-04-10
- Status: Accepted
- Context: AI エージェントに特定の役割（Devil's Advocate レビュアーなど）を割り当てる必要が生じた。ロール定義はツール非依存であるべきだが、格納先が無かった。`.claude/agents/` は Claude Code 固有であり、正本とは別の位置づけが必要だった。
- Decision: `development-docs/rules/roles/` を新設し、エージェントロール定義の正本格納先とする。ロールファイルは stable rule document として英語で記述する。ツール固有のラッパー（`.claude/agents/` 等）は正本を参照するだけの local convenience とする。`.claude/agents/*.md` は Git で管理されており（`.claude/settings.local.json` のみが gitignore 対象）、ローカルで利用可能な状態を維持する。
- Consequences: ロール定義がプロジェクト文書として一元管理される。Claude Code 以外のランタイム（Codex 等）も同一の定義を参照可能になる。ツール固有ラッパーはユーザーが自分でプロビジョニングする必要がある。

---

## ADR-017: Milestone 1 の会話継続基盤は文書ベースの軽量 pilot で開始する

- Date: 2026-04-10
- Status: Accepted
- Context: Milestone 1「前の続きが自然につながる」の出発点として、2つの構造選択肢を検討した。Option A は Git 正本と status store を継続情報源とする文書ベースの軽量 pilot。Option B は conversation continuity 専用の persistent store を今の段階で追加する方式。Autonomous Proceed Conditions に基づき、Option A を自律的に選択した（推奨が1つで理由記載済み、ユーザー好みで覆す余地が低い、後からの方針転換が容易）。
- Decision: Milestone 1 は Option A（文書ベースの軽量 pilot）で進める。Option B（dedicated persistence layer）は `development-docs/project/features/01-feature-backlog.md` Feature 012 に deferred item として保持し、pilot の検証結果で昇格判断する。これは暫定的な出発点であり、最終形ではない。
- Consequences: 新しい永続層を追加せずに「自然な再開」と「短い訂正で戻れること」を先に検証できる。ただし publish されていない純粋な会話文脈は pilot の情報源に含まれず、この不足が深刻と判明した場合は Feature 012 の昇格を検討する必要がある。

---

## ADR-018: ledger-flow フレームワークを ChatLobby に導入（init-and-done モデル）

- Date: 2026-04-13
- Status: Accepted
- Context: 旧来の独自 governance 構造（`/development-docs/` を別 git repo として管理、独自ロール定義、独自ルール）が存在した。Devil's Advocate による全量監査で多数の指摘（設計と実装の乖離、ルール重複、コンテキスト圧力）が出たため、汎用フレームワーク `ledger-flow` を myurait/ledger-flow として独立開発し、その init-and-done モデルで ChatLobby に導入することとした。
- Decision: ledger-flow のフレームワーク全体（rules/, roles/, templates/, scripts/）を `development-docs/rules/` に転写し、既存の進行ファイルを `development-docs/project/` に移行した。サブモジュール依存なし。ChatLobby は ledger-flow 起点から独立して運用する（フレームワーク改定への追従方針はプロジェクト側の判断）。
- Consequences: CLAUDE.md はリダイレクタ（3行）となり、実体のロールルーターは `development-docs/entry-point.md`。AGENTS.md はハイブリッド方式で Codex/Copilot をサポート。ロール定義はフレームワーク提供の5ロール（Worker, Compliance Auditor, Code Quality Auditor, Devil's Advocate, Planning Lead）。開発フローは6必須ステップ + トリガー制。ledger-flow の変更は ChatLobby に自動伝達されないため、必要に応じて手動で取り込む必要がある。
