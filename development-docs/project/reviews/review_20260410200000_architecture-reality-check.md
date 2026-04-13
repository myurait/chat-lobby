# Review

- Date: 2026-04-10T20:00:00+09:00
- Reviewer: Claude Opus 4.6 (1M context) -- Devil's Advocate
- Base Commit: 7354107
- Scope: 全コードベース vs 全設計文書の対照監査
- Review Type: tech lead review
- Trigger: Codex agent の品質懸念による全面監査要請
- Criteria:
  - 実装はアーキテクチャ文書と一致しているか
  - ADR に記載された判断は実コードに反映されているか
  - tech debt registry は現実を正確に記録しているか
  - README に虚偽記載はないか
  - 理想体験と現実の乖離はどの程度か
  - 放棄されたコードや dead end はないか

---

## Findings

### Critical

- **C-01: README が存在しない roadmap を正規参照先としている**
  - ファイル: `README.md` 334行目
  - README の Development Docs セクションに `development-docs/roadmap/01-initial-roadmap.md` が記載されているが、このファイルは存在しない。実際の active roadmap は `development-docs/roadmap/roadmap_20260410153140_conversation-continuity-first.md` であり、archived roadmap は `development-docs/roadmap/archives/roadmap_20260405174901_initial-roadmap.md` にある。README を読んで参照した利用者は必ず 404 に遭遇する。これはプロジェクトの入口文書として致命的。

- **C-02: review evidence ファイルが 5 件上限を 1 件超過している**
  - ルール: `development-process.md` Section 1 "Keep only the newest 5 review evidence files in `reviews/`; older files belong under `reviews/archives/`."
  - 現状: `reviews/` に evidence ファイルが 6 件（本レビューを含めると 7 件）存在している。最古の `review_20260409164528_roadmap-active-archive-structure.md` が archive されていない。開発プロセスルール違反。

### High

- **H-01: アーキテクチャ文書の Target Repository Layout が現実と大幅に乖離**
  - ファイル: `development-docs/design/02-architecture.md` 97-121行目
  - 文書では `plugins/openwebui-status-panel/`、`plugins/openwebui-actions/`、`docs/architecture/`、`docs/operations/`、`docs/templates/`、`examples/sample-project/` を含む構成を目標として記述。しかし `plugins/` ディレクトリ自体が存在しない。Pipe ファイルは `tools/openwebui/` にあり、これは目標構成と全く異なるパス。TD-008 に「整理方針が未確定」と記載されているが、乖離が大きすぎる。文書を読んだ人間が実際のコードを探すときに混乱する。

- **H-02: Data Flow Step 6 の「結果返却」フローは dispatcher 側で同期 polling として実装されているが、architecture doc はそれを示していない**
  - ファイル: `development-docs/design/02-architecture.md` Data Flow セクション
  - ファイル: `services/dispatcher/src/server.ts` 96-123行目
  - architecture doc は `ワーカー → 前面エージェント → ユーザー` と抽象的に記述。実際には dispatcher が adapter を同期 polling（1秒間隔、180秒タイムアウト）し、Open WebUI の HTTP 応答を blocking する設計。この重要な設計特性がアーキテクチャ文書に一切記載されていない。frontdoor の応答性に直接影響する設計判断が文書化されていない。

- **H-03: 全 pipe で `_extract_payload_text` と `_request_json` が完全コピペ**
  - ファイル: `tools/openwebui/chatlobby_claude_task_pipe.py` 56-95行目
  - ファイル: `tools/openwebui/chatlobby_codex_task_pipe.py` 56-95行目
  - ファイル: `tools/openwebui/chatlobby_knowledge_query_pipe.py` 56-95行目
  - ファイル: `tools/openwebui/chatlobby_dispatch_task_pipe.py` 55-99行目
  - ファイル: `tools/openwebui/chatlobby_status_panel_pipe.py` 57-99行目
  - TD-002 に「helper 抽出が未着手」と記録されているが、現在 6 つの pipe すべてで `_extract_payload_text`（JSON 抽出ロジック）と `_request_json`（HTTP 呼び出し）が完全に重複している。一箇所を修正すると他の 5 箇所の修正漏れが確実に起きる。tech debt registry には記録されているが、severity の実態は High。

- **H-04: dispatcher の synchronous poll が Open WebUI worker thread を 180 秒間占有しうる**
  - ファイル: `services/dispatcher/src/server.ts` 106-123行目
  - ファイル: `tools/openwebui/chatlobby_dispatch_task_pipe.py` 104-116行目
  - TD-006 に「同期 polling で Open WebUI worker を占有しうる」と記録されているが、dispatch pipe も同様に Open WebUI 側で `urllib.request.urlopen` を blocking で呼び、その先の dispatcher が最大 180 秒 poll する。事実上、dispatch pipe 経由の 1 リクエストが Open WebUI の worker thread を 3 分間占有する設計。Claude/Codex pipe も個別に同じ問題を抱えている。

- **H-05: アーキテクチャ文書の Key Interfaces に `statusId` の URL encoding 問題が隠れている**
  - ファイル: `services/status-store/src/server.ts` 169-176行目
  - status-store の GET `/tasks/:id` は `url.pathname.slice("/tasks/".length)` で statusId を取得する。statusId のフォーマットは `{worker}:{taskId}` で `:` を含む。HTTP のパス部分ではこれが正しくパースされるが、status panel pipe 側では `urllib.parse.quote(status_id.strip(), safe='')` でエンコードしている。一方 status-store 側ではデコードしていない。`:` は `%3A` にエンコードされるため、pipe 経由の statusId lookup は `claude%3A<uuid>` で検索され、store 上の `claude:<uuid>` とマッチしない可能性が高い。

- **H-06: Codex adapter の `DEFAULT_SKIP_GIT_REPO_CHECK` デフォルト値が危険**
  - ファイル: `services/codex-adapter/src/server.ts` 36行目
  - `process.env.CODEX_SKIP_GIT_REPO_CHECK !== "false"` の結果、環境変数が未設定の場合 `undefined !== "false"` は `true` になる。つまりデフォルトで git repo check がスキップされる。意図された安全ガードが逆転している。

### Medium

- **M-01: アーキテクチャ文書の Worker Roles に記載の「knowledge adapter: Git 正本と関連知識を共通参照可能にする補助層」は実態として rg (ripgrep) の薄いラッパー**
  - ファイル: `services/knowledge-adapter/src/server.ts` 82-191行目
  - architecture doc は「共通参照可能にする補助層」と表現し、ADR-012 は「将来的に MCP や vector retrieval を組み込む場合も、この adapter 境界の内側で差し替えやすい」と述べている。実態は ripgrep の string match のみ。semantic search も embedding も存在しない。これ自体は tech debt として許容範囲だが、ドキュメント上の印象が実態より大幅に高い。

- **M-02: dispatcher の routing rules が起動時に 1 回だけロードされ、ランタイム更新できない**
  - ファイル: `services/dispatcher/src/server.ts` 70行目
  - ADR-013 は「ルール更新は `rules.json` と `docs/operations/routing-policy.md` の同期で運用する」と述べている。しかし `loadRoutingRules` は起動時に `readFileSync` で 1 回だけ呼ばれる。ルール変更はサービス再起動が必須。運用文書にその記載がない。

- **M-03: `design/02-architecture.md` の Open Questions に記載の内容と実装状態の乖離**
  - ファイル: `development-docs/design/02-architecture.md` 126-130行目
  - "Open WebUI の Pipelines でどこまで dispatcher ロジックを実装可能か" -- 結論として Pipelines ではなく host-side dispatcher を実装した。この question は resolved として記録されるべき。
  - "Claude Code の Remote Control と Agent SDK のどちらを主に使うか" -- 実装は `claude -p` CLI を使っており、Remote Control も Agent SDK も使っていない。この question も resolved として記録されるべき。
  - "Codex app-server の安定性と利用可能なイベント粒度" -- 実装は `codex exec --json` CLI を使っている。question が open のまま放置されている。
  - Open Questions が outdated のまま放置されている結果、architecture doc を読んだ人間に「これらがまだ未決定」という誤った印象を与える。

- **M-04: README に記載のないサービスが存在する**
  - ファイル: `README.md`
  - README の Architecture 図に `status store` が含まれているが、Development セクションには `status-store` の起動コマンドと使い方が独立セクションとして記載されている一方、Codex adapter や Knowledge adapter の起動コマンドは Development セクションに分散して記載されているだけで、Claude adapter のような独立セクションがない。一貫性が欠ける。
  - 更に、services/ 配下に 5 つのサービスがあるが、README の Architecture 図には dispatcher と status store の関係が曖昧（status store が dispatcher の配下に見える配置）。

- **M-05: `tools/publish_to_repo.py` が参照する templates ディレクトリパスとコンテナ内パスの不整合**
  - ファイル: `tools/publish_to_repo.py` 13行目 `ROOT_DIR = Path(__file__).resolve().parents[1]`
  - ファイル: `tools/openwebui/chatlobby_publish_pipe.py` 49行目
  - publish_to_repo.py は `ROOT_DIR / "docs" / "templates"` を参照する（ホスト上の `chat-lobby/docs/templates/`）。pipe 側は `/workspace/chatlobby/tools/publish_to_repo.py` を呼ぶが、このとき `ROOT_DIR` は `/workspace/chatlobby/` になり、templates は `/workspace/chatlobby/docs/templates/` を参照する。docker-compose.yml で `./docs:/workspace/chatlobby/docs:ro` がマウントされているためこれは解決する。ただし、この微妙な依存関係がどこにも文書化されていない。

- **M-06: conversation continuity の pilot 実装が design doc に記載されているが、コードが存在しない**
  - ファイル: `development-docs/design/04-conversation-continuity-foundation.md`
  - design doc の Section 10 は「candidate extraction は knowledge adapter と status store の read path を中心に設計する」「front agent pipe / dispatcher 前段で candidate proposal payload を返す最小 pilot を定義する」と記述。しかし、dispatcher にも pipe にも conversation continuity のロジックは一切存在しない。roadmap の Active Cycle Candidate は「planning package と最小 pilot 定義を作る」であり、これは design doc の作成自体を指している可能性があるが、「pilot 定義を作る」と「pilot を実装する」の境界が曖昧。

- **M-07: services/shared/ の共通化が途中状態**
  - ファイル: `services/shared/http.ts`, `services/shared/status.ts`, `services/shared/tasks.ts`
  - TD-001 に「adapter 間で task lifecycle と HTTP utility の共通化が途中段階」と記録されている。実態として http.ts と status.ts は適切に共通化されているが、task の spawn/poll パターン（`runTask` 関数）は claude-adapter と codex-adapter で個別実装されたまま。tech debt の記載内容は正確。

- **M-08: status store の `/tasks/:id` で URL エンコーディング前提が欠落**
  - ファイル: `services/status-store/src/server.ts` 169-176行目
  - `statusId` は `{worker}:{taskId}` の形式でコロンを含むが、HTTP パス上でコロンは特殊文字。status-store 側で `decodeURIComponent` を呼んでいない。H-05 と関連するが、store 側の実装不備としても指摘。

### Low

- **L-01: pipe ファイルのバージョンが全て `0.1` のまま**
  - 全 pipe ファイルの docstring で `version: 0.1` が固定。Phase A から Phase F まで実装が進んでいるのに version が更新されていない。

- **L-02: README に `typecheck` スクリプトへの言及があるが、実行方法が記載されていない**
  - ファイル: `README.md` 108行目 "The `typecheck` script expects `tsc` to be available in your shell."
  - `typecheck` スクリプトの具体的な呼び出し方（npm script なのか、直接実行なのか）が不明。

- **L-03: `.env.example` に `STATUS_STORE_URL` が含まれているが命名が `CHATLOBBY_STATUS_STORE_URL`**
  - ファイル: `.env.example` -- `CHATLOBBY_STATUS_STORE_URL=http://127.0.0.1:8791`
  - adapter コードでは `process.env.STATUS_STORE_URL ?? process.env.CHATLOBBY_STATUS_STORE_URL` の順で参照。`.env.example` には `CHATLOBBY_STATUS_STORE_URL` しか記載がないが、コードは `STATUS_STORE_URL` も受け付ける。環境変数名の選好が不明確。

- **L-04: docker-compose.yml に HEALTHCHECK が未設定**
  - ファイル: `docker-compose.yml`
  - 全サービス（ollama, open-terminal, open-webui）に healthcheck が設定されていない。`depends_on` は使っているが health 条件なし。

---

## Review Dimensions

### Tech Lead Review

#### Debt Prevention

- tech debt registry (TD-001 through TD-009) は概ね現実を正確に反映している。
- 未登録の debt: statusId の URL encoding 問題（H-05/M-08）、dispatcher の同期 poll による worker thread 占有の具体的影響範囲、Codex の skip-git-repo-check デフォルト反転（H-06）。
- TD-009（front agent 実現方式未決定）は依然として根本的問題。全ての理想体験 pillar が「前面 AI が判断する」を前提としているが、前面 AI は存在しない。現在あるのは pipe 経由の手動ワーカー選択か、keyword-based dispatcher である。

#### Complexity Versus Value

- 5 つの TypeScript service + 6 つの Python pipe + 1 つの Python CLI という構成は、個人プロジェクトとしてはかなり多い。
- ただし各コンポーネントは小さく（server.ts は最大 317 行）、責務は明確。この粒度自体は妥当。
- 問題は pipe 側の重複コード。6 つの pipe に同一ロジックが copy-paste されており、保守コストが既に高い。

#### Decomposition and Boundaries

- adapter 境界は ADR 通りに実装されている: claude-adapter(:8787), codex-adapter(:8788), knowledge-adapter(:8789), dispatcher(:8790), status-store(:8791)。
- shared/ への HTTP/status utility の抽出は適切。
- pipe 側の重複が唯一の構造的問題点だが、Open WebUI の single-file function 制約に起因するため、回避方法は限られる。

#### Alignment With Declared Design

- architecture doc の Target Repository Layout と現実は大幅に乖離（H-01）。
- Data Flow の重要な設計特性（同期 polling）が未記載（H-02）。
- Open Questions が 3 件とも resolved だが更新されていない（M-03）。
- ADR-001 through ADR-017 の判断自体は概ね実装と一致しているが、ADR-009 が「`claude -p --output-format json` を起動する」と記載している点は正確に実装されている。ADR-011 が「`codex exec --json` を包む」と記載している点も正確。ADR-012 の knowledge adapter も正確。ADR-013 の dispatcher も正確。ADR-014 の bearer token も正確。ADR-015 の status store も正確。

#### Senior-Engineer Smell Detection

- dispatcher が同期 polling で結果を待つ設計は、初期 pilot としては理解できるが、production では致命的。1 タスク = 1 Open WebUI worker thread の占有。
- Codex adapter の `DEFAULT_SKIP_GIT_REPO_CHECK` のデフォルト反転（H-06）は典型的な「テスト環境では動くが production で想定外の動作をする」パターン。
- statusId の URL encoding 問題（H-05）は、テスト時には curl で直接叩くため発見されないが、pipe 経由（Python の urllib.parse.quote）では壊れる典型的な環境差異。

#### Explanation Responsibility

- 理想体験文書は非常に高品質。問題定義、体験 pillar、representative scenario、acceptance signal が明確。
- しかし、現在の実装は理想体験の 10-15% 程度しか実現していない。理想体験の 5 つの pillar のうち、実質的に動作しているのは Pillar 4（Orchestration Visibility -- status panel 経由の状態確認）の一部のみ。
- Pillar 1（Front Agent As Single Entry Point）: 前面 AI は存在しない。keyword dispatcher があるだけ。
- Pillar 2（Context Memory and Conversation Continuity）: design doc のみ。実装ゼロ。
- Pillar 3（Frictionless Project Elevation）: 実装ゼロ。
- Pillar 4（Orchestration Visibility and Control）: status store と panel が動作。ただし in-memory かつ best-effort。
- Pillar 5（Knowledge Elevation and Reuse）: publish tool と knowledge adapter が動作。ただし ripgrep ベースの string match のみ。

---

## 大項目別サマリー

### 1. 実装はアーキテクチャ文書と一致しているか

**部分的に一致。重大な乖離あり。**

一致している点:
- 5 つのサービス（claude-adapter, codex-adapter, knowledge-adapter, dispatcher, status-store）が architecture doc の記載通りに存在し、記載通りの API を提供している。
- Open WebUI を frontdoor とし、fork/vendoring なしで pipe 経由で拡張する方針は遵守されている。
- bearer token 認証は ADR-014 通りに実装されている。
- status model は architecture doc の記載通りの field を持っている。

乖離している点:
- Target Repository Layout（H-01）: `plugins/` が存在せず、`tools/openwebui/` に置かれている。
- Data Flow の同期 polling 特性（H-02）が文書化されていない。
- Open Questions が全て resolved なのに更新されていない（M-03）。

### 2. ADR は現実と一致しているか

**概ね一致。ただし決定の「結果」部分が更新されていない。**

- ADR-001 through ADR-015: 実装は各 ADR の Decision に記載の通り。
- ADR-016: roles/ ディレクトリが存在し、devil's-advocate.md が格納されている。一致。
- ADR-017: design/04 が文書ベースの pilot として存在。ただし実装は未着手。
- 問題: ADR-009 は「Claude Code の Remote Control と Agent SDK」に言及しているが、実際には CLI (`claude -p`) を使用。Context 部分で「ローカル CLI が既に存在し」とあるため矛盾ではないが、Open Questions の「Agent SDK のどちらを主に使うか」と合わせると混乱を招く。

### 3. tech debt registry は正確か

**概ね正確。ただし未登録の debt が複数存在。**

- TD-001 through TD-009: 全て open として記録されており、実態と一致。
- 未登録:
  - statusId の URL encoding 問題
  - Codex adapter の skip-git-repo-check デフォルト反転
  - dispatcher の routing rules がランタイム更新できない件
  - review evidence ファイルの 5 件上限超過の運用問題

### 4. README は正確か

**虚偽記載あり。**

- `development-docs/roadmap/01-initial-roadmap.md` への参照が壊れている（C-01）。
- `typecheck` スクリプトの呼び出し方が不明（L-02）。
- 各セクションの setup/使い方は概ね正確で、記載されたコマンドは実際に動作する構造になっている。
- Architecture 図は実態と概ね一致しているが、status store の位置付けが曖昧。

### 5. 理想体験は現実に根拠があるか

**理想体験文書は高品質だが、現在の実装との乖離は非常に大きい。**

- 理想体験が描く「前面 AI とだけ会話すればよい」世界は、現時点では実現されていない。
- 現在のユーザー体験: Open WebUI で特定の pipe（ChatLobby Claude Task, ChatLobby Codex Task, ChatLobby Dispatch Task 等）を手動で選択し、JSON または特定フォーマットのメッセージを送信する。これは「ユーザーが毎回どの AI を使うか選ばされる」（Pillar 1 の failure case）そのもの。
- dispatch pipe は plain text 入力を受け付けるため、最もユーザーフレンドリーだが、keyword matching による routing は「前面 AI が判断する」とは言えない。
- 会話継続は design doc のみで実装ゼロ。
- project 化は構想段階。

乖離の推定:
- Pillar 1 (Front Agent): 5-10% 実現（dispatcher の keyword routing のみ）
- Pillar 2 (Context Memory): 0% 実現（design doc のみ）
- Pillar 3 (Project Elevation): 0% 実現
- Pillar 4 (Orchestration Visibility): 30-40% 実現（status store + panel が動作、ただし in-memory で restart 非対応）
- Pillar 5 (Knowledge Elevation): 20-30% 実現（publish tool + knowledge adapter が動作、ただし string match のみ）

### 6. dead end や abandoned path はあるか

**明確な dead end は少ないが、以下が該当候補。**

- `docs/operations/routing-policy.md` -- ADR-013 が「ルール更新は `rules.json` と `docs/operations/routing-policy.md` の同期で運用する」と述べている。このファイルは存在するが、rules.json との同期が実際に行われているかは未検証。
- `workspace/templates/chatlobby-canonical/` -- ADR-006 で定義されたテンプレート構成。docs/, specs/, decisions/, worklog/, src/ が存在する。publish tool はこれを前提に動作する。ただし実際の運用でこのテンプレートが使われている証跡は限定的。
- conversation continuity pilot の design doc（`design/04-conversation-continuity-foundation.md`）-- 設計文書は完成しているが、実装は未着手。roadmap の Active Cycle Candidate に「planning package と最小 pilot 定義を作る」とあり、design doc がその成果物と解釈できるため、dead end ではなく work in progress。ただし design doc の Section 10 が「実装境界」を定義しているのに実装がないのは、文書が実態より先走っている状態。
