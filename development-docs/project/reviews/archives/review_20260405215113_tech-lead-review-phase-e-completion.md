# Review 018: Tech Lead Review — Phase E 完了時点のコードベース全体

- Date: 2026-04-05T22:01:01+09:00
- Reviewer: AI reviewer (tech lead review lens; model unspecified in source evidence)
- Base Commit: root `0aa311a` / development-docs `9ab1908`
- Scope: Phase A–E の全実装コード、設計文書、初期構想との整合性
- Review Type: tech lead review
- Trigger: 明示的なテックリードレビュー依頼
- Criteria:
  - Phase A–E の実装が declared design と初期構想に照らして破綻していないこと
  - Phase F 着手前に止めるべき High risk があるかを判断すること
  - 即時修正と deferred debt の切り分けが可能な粒度で finding を残すこと

---

## Evidence Normalization Note

- この thread は新ルール導入前に `review_018` 本体と follow-up file に分割されていた。
- 正規化にあたり、初回 review、実装方針、follow-up review を本ファイルへ統合した。
- 元証跡の初回 entry は日付のみで時刻未記録だったため、`Date` には preserved evidence file timestamp を採用した。

---

## 1. Debt Prevention（将来の負債予防）

### F-001: adapter 間のユーティリティコード重複 — Severity: Medium

`services/claude-adapter/src/server.ts`, `services/codex-adapter/src/server.ts`, `services/knowledge-adapter/src/server.ts`, `services/dispatcher/src/server.ts` の 4 ファイルで以下の関数が実質同一のコピーペーストで存在する。

- `sendJson()`
- `notFound()`
- `readJsonBody()`
- `trimTasks()` (claude-adapter, codex-adapter)

claude-adapter と codex-adapter は構造がほぼ同一（HTTP server + in-memory Map + spawn + poll）で、差分は CLI コマンド構築と出力パース部分のみ。

adapter が 4 つに増えた現時点で、共通ユーティリティの抽出が妥当。Phase F で status store を追加するとさらに 1 つ増える。

- Action: `services/shared/` に共通 HTTP ユーティリティと task lifecycle の基盤を抽出する。Phase F 着手前が適切なタイミング。

### F-002: Python pipe 間のユーティリティコード重複 — Severity: Medium

`tools/openwebui/` の 5 つの pipe ファイルで `_extract_payload_text()`, `_parse_payload()`, `_request_json()` が完全に重複。

- Action: 共通基底クラスまたはユーティリティモジュールへ抽出する。

### F-003: in-memory task store の揮発性 — Severity: Medium

claude-adapter と codex-adapter の `tasks` Map はプロセス再起動で消失する。Phase F の status store が別コンポーネントとして設計される前提があるため、現時点では adapter 内に永続化を入れる必要はないが、status store 設計時に adapter 側の task 状態とどう連携するか（push か pull か）を先に決める必要がある。

- Action: Phase F 設計開始時に、task 状態の伝搬方式を ADR として記録する。

### F-004: テストインフラが未整備 — Severity: High

`rules/testing.md` が canonical testing policy として参照されているが、テストランナー、テスト設定ファイル、テストコードが一切存在しない。`package.json` にも test script がない。

`development-process.md` Step 2 が毎フェーズ必須とされているにもかかわらず、Phase A–E のいずれでもテストが書かれていない。手動検証（Manual Verification セクション）は存在するが、自動テストによる回帰検出がゼロの状態。

- Action: Phase F 着手前にテストインフラ（vitest or node:test）を導入し、最低限 adapter の parseTaskRequest / buildCommand / routing logic の単体テストを整備する。

### F-005: TypeScript 設定ファイルが存在しない — Severity: High

`tsconfig.json` が存在せず、`tsc --noEmit` による型チェックが CI にも手動にも組み込まれていない。`coding-conventions.md` §12 で strict mode を求めているが、enforcement がない。

`package.json` の scripts は `node services/*/src/server.ts` を直接実行しており、Node 22+ の `--experimental-strip-types` に暗黙依存している。この前提条件が README にも documented されていない。

- Action: `tsconfig.json` を追加し strict mode を有効化する。README に Node バージョン要件を明記する。

---

## 2. Decomposition and Boundaries（分解と境界）

### F-006: dispatcher が routing + HTTP proxy + polling を単一ファイルに集約 — Severity: Low

`services/dispatcher/src/server.ts`（309 行）は、routing 判定ロジック（`routeRequest`, `normalizeKnowledgeQuery`）、HTTP client（`requestJson`, `executeTaskAdapter`）、dispatch 統合（`dispatch`）、HTTP server を 1 ファイルに持つ。

現時点では 300 行で管理可能だが、Phase F で status 収集が加わると肥大化する。routing ロジックを分離しておくとテスタビリティも向上する。

- Action: Phase F 着手時に `routeRequest` と `normalizeKnowledgeQuery` を別モジュールへ切り出す。

### F-007: rules.json の起動時一括読み込み — Severity: Low

`loadRoutingRules()` は `readFileSync` で起動時に 1 回だけ読む。ルール変更にプロセス再起動が必要。Phase E の段階ではルール変更頻度が低いため許容可能だが、将来 hot reload が欲しくなる構造。

- Action: 現時点では記録のみ。ルール更新頻度が上がった段階で file watch または再読み込み API を検討する。

### F-008: 目標リポジトリ構成と実際の構成の乖離 — Severity: Low

<ユーザー追記 (本件はエージェントを介さないユーザーからの直接追記である)>本件は修正対象から外してよい。ただし、プラグイン周辺のディレクトリ構成は肥大化/煩雑化について特に警戒が必要のため、後続フェーズにプラグイン構成の見直しを含む、長期的な計画の策定およびADR記載が必要となる。後続にタスクの追加のみ実施せよ</ユーザー追記>

`design/02-architecture.md` と `chatlobby_development_plan.md` の目標構成:
```
plugins/
  openwebui-status-panel/
  openwebui-actions/
```

実際の構成:
```
tools/openwebui/    ← pipes が配置されている
```

`plugins/` ディレクトリは存在しない。pipes を `plugins/` に移すか、目標構成を現状に合わせて更新する必要がある。

- Action: 目標構成の文書を現状に合わせて更新する。実際の `tools/openwebui/` 配置は Open WebUI の mount 境界と一致しており合理的。

---

## 3. Alignment With Declared Design（設計文書との整合性）

### F-009: ADR-004 の言語方針は正しく守られている — Decision only

TypeScript を中核実装に、Python を Open WebUI 連携に限定する方針は厳密に守られている。問題なし。

### F-010: コミット規約の遵守 — Decision only

`coding-conventions.md` §10 で `<type>: <summary>` 形式、日本語、72 文字以内、Co-authored-by なしを規定。git log を確認すると概ね遵守されている。

### F-011: tech debt registry が空のまま — Severity: Medium

`design/03-tech-debt-registry.md` にはテンプレート行のみで、実際の負債が一切記録されていない。F-003（揮発性 task store）、F-004（テスト未整備）、F-005（tsconfig 未整備）は明確な技術負債であり、記録されるべきもの。

- Action: 本レビューの High/Medium finding を tech debt registry に転記する。

---

## 4. Senior-Engineer Smell Detection（嗅覚検知）

### F-012: adapter API に認証・認可がない — Severity: High

全 adapter は `CLAUDE_ADAPTER_HOST=0.0.0.0` で起動した時点で、同一ネットワーク上の任意のクライアントから無制限にタスク作成が可能。`workingDirectory` もリクエスト経由で任意指定できる。

claude-adapter は `claude -p` を `workingDirectory` 上で実行するため、悪意のあるリクエストが任意ディレクトリで Claude Code を実行できる。codex-adapter も同様。

個人利用の LAN 環境では許容範囲だが、`0.0.0.0` バインドを推奨する README の手順との組み合わせでリスクが顕在化する。

- Action: 最低限、Bearer token による API key 認証を adapter に追加する。`.env` で管理し、Open WebUI pipe の Valves にも対応する。Phase F までに対応が望ましい。

### F-013: リクエストボディのサイズ制限なし — Severity: Medium

全 TypeScript サーバーの `readJsonBody()` がリクエスト全体を無制限にバッファする。大きなリクエストでメモリ枯渇の可能性がある。

- Action: `readJsonBody()` に上限（例: 1MB）を追加する。<ユーザー追記 (本件はエージェントを介さないユーザーからの直接追記である)>サイズ決め打ちは危険。また、リクエスト実態が平文だけとは限らないため、長大なリクエストはオフロードする仕組みが必要。ただし、実際の設計/実装は後続フェーズに任せる。これも踏まえ負債または後続タスクにもれなく追記すること</ユーザー追記>

### F-014: prompt を CLI 引数として直接渡している — Severity: Medium

`buildClaudeCommand()` と `buildCodexCommand()` が prompt 文字列を CLI 引数に直接渡している。OS の引数長制限（Linux: 通常 2MB、macOS: 256KB）に当たる可能性がある。stdin 経由での受け渡しが安全。

- Action: prompt が一定長を超える場合は stdin pipe に切り替える。

### F-015: Python pipe の同期 polling が Open WebUI worker を占有 — Severity: Low

`chatlobby_claude_task_pipe.py` と `chatlobby_codex_task_pipe.py` は `time.sleep()` ループで最大 180 秒ブロックする。Open WebUI の pipe 実行モデル次第だが、worker pool を長時間占有する可能性がある。<ユーザー追記 (本件はエージェントを介さないユーザーからの直接追記である)>これは議論の余地あり。sleepであるべきであるかは議論の余地があり、実行モデル次第なところもあるが、技術負債として明確に捉えるべき</ユーザー追記>

dispatch pipe は dispatcher 側でポーリングするため pipe 自体はブロックしないが、claude/codex pipe は直接ブロックする。

- Action: 現時点では記録のみ。dispatch pipe 経由の利用を主とすることで影響は限定的。

### F-016: graceful shutdown が未実装 — Severity: Low

全 TypeScript サーバーが SIGTERM/SIGINT ハンドリングをしていない。実行中タスクがある状態でプロセスを kill すると、task record が `running` のまま放棄される。

- Action: Phase F の status store 実装時にあわせて対応する。

---

## 5. 初期構想との整合性 (ユーザーから個別指示)

### 全体的な方向性

初期構想（`chatlobby_requirements.md`, `chatlobby_roadmap.md`, `chatlobby_development_plan.md`）が描くビジョンと、Phase E 時点の実装を照合する。

#### ロードマップの忠実な実行: 良好

Phase A → B → C → D → E の順序は初期ロードマップに完全に準拠している。各フェーズの成功判定も満たされている。段階的構築の方針が守られており、過剰な先行実装もない。

#### 初期構想が求める「前面エージェント」の不在: 注意

初期構想 §4.1, §7.1.1 が求めるのは「前面には応対する開発リーダー相当のエージェントが存在し、ユーザーは基本的に前面の会話相手とだけ話せばよい」体験。

現状は「ユーザーが Open WebUI の model 一覧から ChatLobby Dispatch Task を選んでテキストを送る」形式。dispatcher は routing を行うが、会話文脈の保持、結果の統合表示、対話的なフォローアップといった「前面エージェント」の役割は果たしていない。

これは Phase E のスコープ外であり、現時点で問題ではない。ただし、Phase F 以降で「前面エージェント」をどう実現するか（LLM ベースの front agent を置くか、Open WebUI 側の会話フローに寄せるか）が重要な設計判断になる。

- Action: Phase F または Phase G の設計開始時に、front agent の実現方式を ADR として明確化する。

#### 自然言語からの作業移行: 部分的に達成

初期構想 §7.1.2「雑談、調査相談、仕様相談、実装依頼、修正依頼が、同じ会話圏で連続して行える」。

dispatch pipe は plain text を受け付け、keyword matching で振り分ける。「実装して」「検索して」のような短い指示は動作する。しかし、同じ会話内で「まず調査して → その結果を踏まえて実装して」のような連続的なフローは未対応。各リクエストは独立した単発。

これはロードマップの Phase F–G で段階的に改善される想定であり、現時点では適切。

#### 並列ワーカー起動: 未実装（想定通り）

初期構想 §5.3, §7.4.1 が求める「複数実装担当による並列修正」は dispatcher にまだない。dispatcher は単一ワーカーへの routing のみ。

これは Phase E のスコープ外であり、将来の multi-dispatch として設計予定。現時点では問題ない。

#### knowledge 共有: 基本形は成立

初期構想 §7.3 が求める「各エージェントが共通で参照する共有正本」は、knowledge adapter + canonical repo で成立している。publish pipe で Git へ書き込み、knowledge pipe で Git から読み出す。

ただし、worker（Claude Code / Codex）が knowledge adapter を直接参照する仕組みはまだない。worker は `workingDirectory` 内のファイルしか見えない。canonical repo と作業 repo の同期は手動前提。

#### Phase G の再検討メモ: 妥当

ロードマップに「この辺りは現在のdevelopment-docsループに依存していれば不要に見える」と注記がある。development-docs の CLAUDE.md ループ（調査 → 設計 → 実装 → レビュー → knowledge.md 更新）が spec feedback loop の一部を代替しているのは事実。ただし、初期構想が求める「実装結果を受けて仕様書を自動更新し、次回の共通知識にする」自動化の部分は development-docs ループでは手動に留まる。Phase G の要否は実装時にディスカッションするという判断は適切。

---

## 6. Finding Summary

- `F-001` / Medium / Debt: adapter 間のユーティリティコード重複
- `F-002` / Medium / Debt: Python pipe 間のユーティリティコード重複
- `F-003` / Medium / Debt: in-memory task store の揮発性（Phase F 設計時に要検討）
- `F-004` / High / Debt: テストインフラ未整備
- `F-005` / High / Debt: `tsconfig.json` 未整備、Node バージョン要件未文書化
- `F-006` / Low / Boundary: dispatcher が routing + proxy + polling を集約
- `F-007` / Low / Boundary: `rules.json` の起動時一括読み込み
- `F-008` / Low / Alignment: 目標リポジトリ構成と実構成の乖離
- `F-009` / Alignment: ADR-004 言語方針は遵守（問題なし）
- `F-010` / Alignment: コミット規約は遵守（問題なし）
- `F-011` / Medium / Alignment: tech debt registry が空
- `F-012` / High / Smell: adapter API に認証なし
- `F-013` / Medium / Smell: リクエストボディのサイズ制限なし
- `F-014` / Medium / Smell: prompt を CLI 引数で渡すため長さ制限あり
- `F-015` / Low / Smell: Python pipe の同期 polling が worker を占有
- `F-016` / Low / Smell: graceful shutdown 未実装

---

## 7. Recommended Action Priority

### Phase F 着手前に必須

1. **F-004**: テストインフラを導入し、routing logic と adapter の request parsing に単体テストを追加
2. **F-005**: `tsconfig.json` を作成し strict mode を有効化。README に Node 22+ 要件を明記
3. **F-012**: adapter API に最低限の Bearer token 認証を追加
4. **F-011**: 本レビューの finding を tech debt registry に転記

### Phase F と並行で対応可能

5. **F-001**: 共通ユーティリティの抽出（status store 追加前が好タイミング）
6. **F-013**: リクエストボディのサイズ制限追加
7. **F-014**: 長い prompt の stdin 渡しへの切り替え

### 記録して将来対応

8. **F-002**, **F-003**, **F-006**, **F-007**, **F-008**, **F-015**, **F-016**

## Implementation Response Plan

- Date: 2026-04-05T21:51:13+09:00
- Reviewer: Codex agent (model unspecified in source evidence)
- Base Commit: root `0aa311a` / development-docs `9ab1908`
- Plan Summary:
  - High finding を Phase F 着手前の最低限 hardening として解消し、Medium / Low のうち即時実装しない項目は tech debt registry と roadmap に送る。
- Planned Fixes:
  - `services/shared/` を追加し、HTTP utility と task trimming の重複を削減する。
  - adapter / dispatcher に bearer token 認証を追加し、non-loopback bind 時は token 必須にする。
  - `tsconfig.json`、README の Node 要件、test / typecheck script を追加する。
  - review 018 の High / Medium finding とユーザー追記の論点を tech debt registry と roadmap に転記する。
- Deferred Items:
  - Python pipe 共通化、task 状態永続化、dispatcher 分割、rules hot reload、large payload offload、stdin 経由 prompt、direct pipe async 化、graceful shutdown は後続フェーズへ送る。
  - plugin 配置戦略と front agent 方式は ADR 化タスクとして後続フェーズに追加する。

## Follow-Up Review History

### Entry 1

- Date: 2026-04-05T22:01:09+09:00
- Reviewer: Codex agent (model unspecified in source evidence)
- Base Commit: root `d8bfcce` / development-docs `807f114`
- Review Type: tech lead review
- References:
  - review 018 の response plan
  - `services/shared/`, adapter auth, debt registry, README / `.env` / pipe valve 更新
- Result: Pass
- Notes:
  - review 018 の High 指摘は最低限の範囲で処理され、deferred 論点も registry と roadmap に転記された。
  - `services/shared/` 抽出により adapter 追加時の重複を抑えやすくなった。
  - Open WebUI 非 fork、TypeScript 主体、host sidecar 分離という設計方針を崩さず hardening できている。
- Remaining Risks:
  - `typescript` compiler 自体の導入は未完了で、strict config の enforcement はまだ弱い。
  - long payload / stdin / async polling は debt 化済みだが、実装は未着手。

### Entry 2

- Date: 2026-04-05T22:01:09+09:00
- Reviewer: AI reviewer (tech lead review lens; model unspecified in source evidence)
- Base Commit: root `d8bfcce` / development-docs `807f114`
- Review Type: tech lead review
- References:
  - review 018 の response plan
  - review 018 の全 finding に対する post-fix re-review
- Result: Pass with follow-up findings
- Notes:
  - review 018 の High finding 3 件（F-004, F-005, F-012）は修正済みと判定された。
  - High / Medium finding は修正済み、または tech debt registry で追跡可能な状態に整理された。
  - ユーザー追記で deferred 指示された F-008, F-013, F-015 も registry / roadmap に正しく反映された。

#### Entry 2 Finding Status

- `F-001` / Medium / 許容: shared utility 抽出は完了、spawn/poll 重複は TD-001 で追跡
- `F-002` / Medium / 許容: Open WebUI packaging 制約を踏まえ TD-002 で追跡
- `F-003` / Medium / 許容: status store 設計時に ADR 化する前提で TD-003 へ送付
- `F-004` / High / 対応済み: Python unittest ベースの test infrastructure を追加
- `F-005` / High / 対応済み: `tsconfig.json` と Node 22 要件を追加。ただし R-001 が残存
- `F-006` / Low / 許容: Phase F での分割対象として記録済み
- `F-007` / Low / 許容: ルール再読込は将来課題として記録済み
- `F-008` / Low / 許容: ユーザー指示どおり修正対象外、TD-008 で追跡
- `F-009` / 問題なし: ADR-004 言語方針は遵守
- `F-010` / 問題なし: コミット規約は遵守
- `F-011` / Medium / 対応済み: TD-001〜TD-009 を追加
- `F-012` / High / 対応済み: Bearer token 認証を全 adapter + pipe に実装
- `F-013` / Medium / 許容: ユーザー指示どおり offload 設計を TD-004 で追跡
- `F-014` / Medium / 許容: stdin 経由 prompt は TD-005 で追跡
- `F-015` / Low / 許容: direct pipe polling は TD-006 で追跡
- `F-016` / Low / 許容: graceful shutdown は TD-007 で追跡

#### Entry 2 New Findings

- `R-001` / Medium: `typescript` パッケージが `devDependencies` にないため `npm run typecheck` が環境依存。
  Action: `typescript` を devDependencies に追加する。
- `R-002` / Low: TypeScript の純粋関数に対する unit test がない。
  Action: Phase F で `node:test` か `vitest` の導入を検討する。
- `R-003` / Low: knowledge-adapter の認証チェック配置が他 adapter と不一致。
  Action: 次回 adapter 修正時に auth check pattern を統一する。

- Remaining Risks:
  - R-001 が未解消のため、strict mode の enforcement はまだ不完全。
  - R-002, R-003 は低優先度だが、Phase F 以降の service 追加時に再燃しうる。

### Entry 3

- Date: 2026-04-05T22:41:54+09:00
- Reviewer: Codex agent (GPT-5)
- Base Commit: root `d8bfcce` / development-docs `f5f6cb8`
- Review Type: tech lead review
- References:
  - Entry 2 の new findings `R-001`, `R-002`, `R-003`
  - `services/*/src/*`, `tests/*.test.ts`, `package.json`, `tsconfig.json`
- Result: Pass
- Notes:
  - `R-001` は `package.json` に `typescript` を `devDependencies` として追加することで解消した。
  - `R-002` は pure function を `task-request.ts` / `routing.ts` へ切り出し、`node:test` による TypeScript unit test 12 件を追加して解消した。
  - `R-003` は knowledge adapter の bearer token check を他 adapter と同じ request entry point へ移し、auth check pattern を統一して解消した。
  - 既存の Python integration test 16 件と新しい `node:test`、`npm test`、`node --check` は通過した。
- Remaining Risks:
  - `typescript` dependency は manifest 上は解消したが、このターンではローカル環境への install を行っていないため、`npm run typecheck` はまだ未実行である。

### Entry 4

- Date: 2026-04-05T22:44:42+09:00
- Reviewer: Codex agent (GPT-5)
- Base Commit: root `fecb2b4` / development-docs `c9b3093`
- Review Type: tech lead review
- References:
  - Entry 3 の remaining risk
  - `package.json`, `tsconfig.json`, `package-lock.json`
- Result: Pass
- Notes:
  - project-local の `npm install` を実施し、`typescript` と `@types/node` を lockfile 付きで同期した。
  - `tsconfig.json` に `lib: ["ES2023"]` と `types: ["node"]` を追加したことで、`npm run typecheck` が通るようになった。
  - `npm test` も再実行し、Python integration test と `node:test` の両方が通ることを確認した。
- Remaining Risks:
  - None.

### Entry 5

- Date: 2026-04-06T00:15:00+09:00
- Reviewer: Claude Opus 4.6
- Base Commit: root `7907e0a` / development-docs (same tree as root)
- Review Type: tech lead review
- References:
  - Entry 3 planned fixes: R-001 (typescript devDependency), R-002 (TS unit tests), R-003 (auth check pattern)
  - Entry 4 remaining risk: npm install / typecheck 実行確認
  - Commits: `fecb2b4` (test: add TypeScript unit tests), `7907e0a` (chore: sync typecheck dependencies)
- Result: Pass
- Verification Method:
  - `npm run typecheck` を実行し、`tsc --noEmit` が exit 0 で完了することを確認した。
  - `node --test tests/*.test.ts` を実行し、12 件全件 pass を確認した。
  - 全 adapter / dispatcher / shared のソースコードを読み、以下を検証した。
- Findings per Entry 2 new finding:
  - `R-001` / 解消確認済み: `typescript@^5.9.3` と `@types/node@^22.18.6` が `devDependencies` に追加されている。`package-lock.json` も同期済み。`tsconfig.json` は `target: ES2023`, `lib: ["ES2023"]`, `types: ["node"]`, `strict: true` で適切。`npm run typecheck` が exit 0 を返すことを実行確認した。
  - `R-002` / 解消確認済み: pure function が以下のモジュールに切り出された。
    - `services/claude-adapter/src/task-request.ts`: `parseClaudeTaskRequest`, `buildClaudeCommand`
    - `services/codex-adapter/src/task-request.ts`: `parseCodexTaskRequest`, `buildCodexCommand`
    - `services/dispatcher/src/routing.ts`: `parseDispatchRequest`, `routeRequest`, `normalizeKnowledgeQuery`
    - テストは `tests/http.test.ts` (3件), `tests/routing.test.ts` (5件), `tests/task-request.test.ts` (4件) の計 12 件。routing のエッジケース（workerHint override, keyword fallback, explicit field）と task-request のフラグ生成が網羅されている。
  - `R-003` / 解消確認済み: knowledge-adapter の auth check が request handler 冒頭に移動し、claude/codex adapter と同一パターンになった。具体的には `knowledge-adapter/src/server.ts:217-225` で `/health` 以外の全リクエストに対して一括で `requireBearerToken` → `HttpError` catch を実施。4 adapter すべてが同じ try/catch 構造で統一されている。
- Code Quality Observations:
  - pure function の切り出しにより、server.ts の各ファイルは HTTP server + spawn + state 管理に集中し、parse/build/routing logic が独立テスト可能になった。decomposition は適切。
  - `routeRequest` が `routingRules` を引数で受け取る形に変更され、テスト時に任意のルールセットを注入できる。依存注入として正しい改善。
  - `loadRoutingRules` は引き続き dispatcher の server.ts に残っており、I/O を含むためテスト対象から適切に分離されている。
  - dispatcher server.ts は 206 行に縮小（Entry 1 時点の 309 行から約 33% 減）。F-006 で指摘した肥大化懸念が実質的に解消された。
- New Findings:
  - None.
- Remaining Risks:
  - None. review 018 の全 finding (F-001〜F-016) および follow-up finding (R-001〜R-003) はすべて対応済みまたは tech debt registry で追跡中。Phase F 着手に対するブロッカーはない。
