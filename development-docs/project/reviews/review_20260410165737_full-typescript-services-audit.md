# Review

- Date: 2026-04-10T16:57:37+09:00
- Reviewer: Claude Opus 4.6 (Devil's Advocate)
- Base Commit: 9e0b79edbb7a9189956cc4ff49be36d4bc38d3e8
- Scope: 全 TypeScript サービスの完全な敵対的監査 (`services/claude-adapter/`, `services/codex-adapter/`, `services/knowledge-adapter/`, `services/dispatcher/`, `services/status-store/`, `services/shared/`)
- Review Type: tech lead review | security review | code review
- Trigger: Codex エージェントが品質問題で解雇された後の全リポジトリ監査要請
- Criteria:
  - エラーハンドリング: エラーが適切にキャッチ、ログ、伝播されているか
  - 入力バリデーション: システム境界で外部入力が検証されているか
  - セキュリティ: インジェクション、パストラバーサル、認証バイパス
  - リソース管理: プロセスのクリーンアップ、タイムアウト、メモリリーク
  - 競合状態: 並行タスク処理、共有状態
  - エッジケース: 空入力、巨大入力、不正入力
  - アーキテクチャ準拠: ADR-009 から ADR-015 の遵守
  - コーディング規約準拠: `rules/coding-conventions.md`
  - テストポリシー準拠: `rules/testing.md`
  - Tech Debt Registry の正確性

---

## Findings

### Critical

- **C-01: コマンドインジェクション — prompt が CLI 引数として直接渡されている**
  - 影響ファイル:
    - `/services/claude-adapter/src/task-request.ts` 行 60 (`command.push(task.prompt)`)
    - `/services/codex-adapter/src/task-request.ts` 行 65 (`command.push(task.prompt)`)
  - 説明: ユーザー提供の `prompt` 文字列が `spawn()` の引数配列に直接挿入される。`spawn` はシェルを介さないため古典的なシェルインジェクションは発生しないが、prompt に CLI フラグ構文（例: `--dangerously-bypass-approvals-and-sandbox`）を含めることで、意図しないフラグが CLI に渡される。Claude Code / Codex CLI がフラグと positional 引数を `--` で分離しない限り、攻撃者は prompt を通じて `--permission-mode` や `--dangerously-bypass-approvals-and-sandbox` を上書きできる可能性がある。
  - 根拠: `coding-conventions.md` Section 14「Validate and sanitize all external input」、Section 7「Make failure modes explicit」に違反。
  - 対策: prompt の前に `--` を挿入して positional 引数の開始を明示する。または prompt にハイフン先頭文字列が含まれる場合に拒否する。

- **C-02: `workingDirectory` にパストラバーサル防御がない（claude-adapter / codex-adapter）**
  - 影響ファイル:
    - `/services/claude-adapter/src/task-request.ts` 行 27-29
    - `/services/codex-adapter/src/task-request.ts` 行 35-36
    - `/services/claude-adapter/src/server.ts` 行 45 (`cwd: request.workingDirectory`)
    - `/services/codex-adapter/src/server.ts` 行 75 (`cwd: request.workingDirectory`)
  - 説明: ユーザー提供の `workingDirectory` が無検証で `spawn()` の `cwd` に渡される。攻撃者は `/etc`, `/root`, `/` などシステム上の任意ディレクトリを指定できる。knowledge-adapter では `ensurePathInsideRepo()` でこの防御を行っているが、claude-adapter と codex-adapter にはこの検証が完全に欠落している。
  - 根拠: `coding-conventions.md` Section 14「Validate and sanitize all external input」に違反。ADR-014 で bearer token 保護を追加したが、認証されたクライアントでも任意パス指定が可能。
  - 対策: 許可されたベースディレクトリ配下かどうかの検証を追加する。

- **C-03: `readJsonBody` にリクエストボディサイズ制限がない**
  - 影響ファイル: `/services/shared/http.ts` 行 22-37
  - 説明: `readJsonBody` はリクエストストリーム全体をメモリに蓄積する。Content-Length チェックもストリーム上限もない。攻撃者は巨大な HTTP ボディを送信し、プロセスの OOM を引き起こせる。全 5 サービスがこの関数を使用しているため、全サービスが DoS に対して脆弱。
  - 根拠: `coding-conventions.md` Section 15「Watch memory usage in long-running processes」、Section 14「Validate and sanitize all external input」に違反。tech debt registry TD-004 に「大きい payload のオフロード方式が未設計」と記録されているが、最低限のサイズ上限すらないのは重大な欠落。

### High

- **H-01: Graceful shutdown が全サービスに欠落**
  - 影響ファイル:
    - `/services/claude-adapter/src/server.ts` 行 231-233
    - `/services/codex-adapter/src/server.ts` 行 263-265
    - `/services/knowledge-adapter/src/server.ts` 行 314-316
    - `/services/dispatcher/src/server.ts` 行 201-205
    - `/services/status-store/src/server.ts` 行 183-186
  - 説明: SIGTERM / SIGINT ハンドラが存在しない。サーバーが停止されると、実行中のリクエストは途中で切断され、claude-adapter / codex-adapter で spawn 済みの子プロセスは orphan として残り、ステータスは永久に `running` のまま。
  - 根拠: tech debt registry TD-007 に記録済みだが、ステータスが「open」のまま放置されており対処が進んでいない。`coding-conventions.md` Section 7「Always handle errors explicitly」および Section 13「Log all significant state changes」に違反。

- **H-02: 子プロセスのタイムアウトがない（claude-adapter / codex-adapter）**
  - 影響ファイル:
    - `/services/claude-adapter/src/server.ts` 行 44-132 (`runTask`)
    - `/services/codex-adapter/src/server.ts` 行 74-159 (`runTask`)
  - 説明: `spawn()` で起動した子プロセスにタイムアウトが設定されていない。Claude Code や Codex が無限にハングした場合、タスクは永久に `running` 状態に留まり、プロセスリソースを消費し続ける。`MAX_TASKS` の制限はあるが、`trimTasks` は running タスクを優先的に保持するため、ハングしたタスクが集積する。
  - 根拠: `coding-conventions.md` Section 15「Watch memory usage in long-running processes」に違反。

- **H-03: stdout / stderr のバッファに上限がない**
  - 影響ファイル:
    - `/services/claude-adapter/src/server.ts` 行 54-59
    - `/services/codex-adapter/src/server.ts` 行 84-89
  - 説明: 子プロセスの stdout / stderr を文字列連結で蓄積しているが、上限チェックがない。大量の出力を返す Claude Code / Codex タスクはアダプタプロセスの OOM を引き起こす。
  - 根拠: `coding-conventions.md` Section 15 に違反。TD-004 関連。

- **H-04: `requireBearerToken` のタイミング攻撃脆弱性**
  - 影響ファイル: `/services/shared/http.ts` 行 49
  - 説明: `providedToken !== expectedToken` は通常の文字列比較（`!==`）を使用しており、タイミングサイドチャネルに対して脆弱。攻撃者はレスポンス時間の差異からトークンを 1 文字ずつ推測できる可能性がある。
  - 根拠: `coding-conventions.md` Section 14「Security Practices」に違反。`crypto.timingSafeEqual` を使用すべき。

- **H-05: `parseCodexJsonl` 内の無検証 `JSON.parse`**
  - 影響ファイル: `/services/codex-adapter/src/server.ts` 行 58
  - 説明: `parseCodexJsonl` は `filter((line) => line.startsWith("{"))` で行をフィルタした後に `JSON.parse(line)` を呼ぶが、try-catch がない。`{` で始まるが不正な JSON 行があるとプロセス全体がクラッシュする。
  - 根拠: `coding-conventions.md` Section 7「Always handle errors explicitly」に違反。

- **H-06: `readJsonBody` で空ボディに対してデフォルト空オブジェクトを返す**
  - 影響ファイル: `/services/shared/http.ts` 行 28-30
  - 説明: `chunks.length === 0` のとき `{}` を返す。これにより Content-Type なしの GET リクエストや空 POST でもバリデーションを通過してしまうケースがある。特に dispatcher の `/dispatch` ではボディなしで到達した場合、`parseDispatchRequest({})` が呼ばれ `HttpError(400)` を返すが、他のサービスでは想定外の動作になりうる。
  - 根拠: `coding-conventions.md` Section 7 に違反。空ボディはエラーとして扱うべき。

- **H-07: dispatcher のポーリングループがサービスを長時間ブロックする**
  - 影響ファイル: `/services/dispatcher/src/server.ts` 行 107-123 (`executeTaskAdapter`)
  - 説明: `POLL_TIMEOUT_MS` のデフォルトは 180000ms（3 分）。この間、HTTP レスポンスは返されず、クライアント接続を占有する。Node.js のデフォルト HTTP サーバータイムアウト（120 秒）よりも長いため、クライアント側でタイムアウトが先に発生する可能性がある。また、dispatcher が単一スレッドであるため、長時間実行タスクが増えるとすべてのリクエスト処理が詰まる。
  - 根拠: TD-006 関連だが、dispatcher 自体のブロッキング問題は tech debt registry に記録されていない。`coding-conventions.md` Section 15 に違反。

- **H-08: knowledge-adapter の `repoPath` パラメータにパストラバーサル防御がない**
  - 影響ファイル: `/services/knowledge-adapter/src/server.ts` 行 35-37 (`ensureRepoRoot`)
  - 説明: `ensureRepoRoot` は `repoPath` をそのまま `resolve()` するだけで、任意のディレクトリパスを受け入れる。`ensurePathInsideRepo` は `repoRoot` からの相対パスを検証するが、`repoRoot` 自体が攻撃者に制御可能。つまり `repoPath: "/etc"` を指定すれば `/etc` 内の任意ファイルを検索・読取できる。
  - 根拠: `coding-conventions.md` Section 14 に違反。

- **H-09: テストカバレッジが著しく不足**
  - 影響ファイル: テスト対象は 3 ファイルのみ (`tests/http.test.ts`, `tests/task-request.test.ts`, `tests/routing.test.ts`)
  - 説明: サービスコードは 11 ファイルあるが、テストが存在するのは `shared/http.ts`（部分的）、`claude-adapter/src/task-request.ts`、`codex-adapter/src/task-request.ts`、`dispatcher/src/routing.ts` のみ。以下のコードにはテストが存在しない:
    - `services/shared/tasks.ts` — `trimTasks` ロジック
    - `services/shared/status.ts` — `publishStatusEvent`, `buildStatusId`
    - `services/status-store/src/server.ts` — `mergeStatusEvent`, `parseStatusEvent`, `trimStatusRecords`, `listTasks`
    - `services/knowledge-adapter/src/server.ts` — `handleSearch`, `handleRead`, `ensurePathInsideRepo`, パストラバーサル防御
    - 全サーバーファイル — HTTP エンドポイントの統合テスト
    - `services/dispatcher/src/server.ts` — `dispatch` ロジック、`executeTaskAdapter` のポーリング
  - 根拠: `rules/testing.md` Section 5「New code must have tests」に明確に違反。knowledge-adapter のパストラバーサル防御のような重要なセキュリティロジックにテストがないのは特に危険。

### Medium

- **M-01: `WorkerName` 型が `shared/status.ts` と `dispatcher/src/routing.ts` で重複定義**
  - 影響ファイル:
    - `/services/shared/status.ts` 行 1
    - `/services/dispatcher/src/routing.ts` 行 3
  - 説明: 同じ `WorkerName = "claude" | "codex" | "knowledge"` が 2 箇所で独立に定義されている。一方を変更しても他方が更新されないリスクがある。
  - 根拠: `coding-conventions.md` Section 3「Do not accept hidden coupling as normal」、`development-process.md` Section 2.2「Detect duplicated knowledge that should be centralized」に違反。

- **M-02: `TaskState` 型が `shared/status.ts` の `StatusState` と重複定義**
  - 影響ファイル:
    - `/services/claude-adapter/src/server.ts` 行 9
    - `/services/codex-adapter/src/server.ts` 行 13
    - `/services/shared/status.ts` 行 2
  - 説明: `TaskState = "running" | "succeeded" | "failed"` が `StatusState` と同一内容で 3 箇所に独立定義されている。
  - 根拠: M-01 と同一の根拠。

- **M-03: claude-adapter と codex-adapter の `server.ts` が大量のコード重複**
  - 影響ファイル:
    - `/services/claude-adapter/src/server.ts` (233 行)
    - `/services/codex-adapter/src/server.ts` (265 行)
  - 説明: サーバー起動、ルーティング、タスク管理、status publish のパターンがほぼ同一。差分は `spawn` するコマンドと `parseJsonl` の有無だけ。TD-001 に「adapter 間で task lifecycle と HTTP utility の共通化が途中段階」と記録されているが、現状は共通化がほぼ進んでいない。`runTask` 関数内の status publish コードだけで各ファイル 40 行以上が実質コピーペースト。
  - 根拠: TD-001 の通り。`coding-conventions.md` Section 3 および `development-process.md` Section 2.2 に違反。

- **M-04: `trimTasks` が running タスクを誤って削除する可能性**
  - 影響ファイル: `/services/shared/tasks.ts` 行 1-19
  - 説明: `trimTasks` は `maxTasks` に到達すると非 running タスクを削除し、それでも不足なら `tasks.keys().next().value`（Map の挿入順で最も古いもの）を削除する。この最も古いタスクが running 状態である可能性がある。running タスクが削除されると、子プロセスは動き続けるが結果を記録する場所がなくなる。
  - 根拠: `coding-conventions.md` Section 7「Make failure modes explicit」に違反。

- **M-05: `publishStatusEvent` のエラーが全て `.catch(() => {})` で握りつぶされている**
  - 影響ファイル:
    - `/services/claude-adapter/src/server.ts` 行 90, 109, 130, 211
    - `/services/codex-adapter/src/server.ts` 行 117, 136, 157, 243
    - `/services/knowledge-adapter/src/server.ts` 行 247, 261, 287, 301
  - 説明: ADR-015 は「status 伝搬は best-effort なので task 完了を status publication failure で失敗させない」と述べているが、エラーを完全に握りつぶしてログすら残さないのは `coding-conventions.md` Section 7「Never swallow errors silently」に違反。best-effort であっても、障害の可視化は必要。
  - 根拠: `coding-conventions.md` Section 7 および Section 13「Log all significant state changes」に違反。

- **M-06: dispatcher の `requestJson` 内で `response.text()` を `JSON.parse` しているが不正 JSON で握りつぶされる**
  - 影響ファイル: `/services/dispatcher/src/server.ts` 行 86-88
  - 説明: `JSON.parse(text)` が失敗した場合、例外は外側の `catch` で `HttpError(502)` に変換されるが、元のレスポンスボディ情報が失われ、デバッグが困難になる。
  - 根拠: `coding-conventions.md` Section 7「Log errors with sufficient context」に違反。

- **M-07: `normalizeKnowledgeQuery` のハードコードされた日本語パターン**
  - 影響ファイル: `/services/dispatcher/src/routing.ts` 行 79-89
  - 説明: 関数内に日本語助詞・動詞パターンがハードコードされている。ADR-004 で「Supported Product Languages: English / Japanese」と定義されているが、将来的な言語追加時にこの関数が適応できない。また、これらのパターンは `rules.json` の keyword リストと重複・不整合の可能性がある。
  - 根拠: `coding-conventions.md` Section 3「Keep functions and modules focused on one responsibility」に違反。設定ファイルに外出しすべき。

- **M-08: `/tasks/:id` のルーティングがプレフィックスマッチで意図しないパスを受け入れる**
  - 影響ファイル:
    - `/services/claude-adapter/src/server.ts` 行 171
    - `/services/codex-adapter/src/server.ts` 行 198
    - `/services/status-store/src/server.ts` 行 169
  - 説明: `url.pathname.startsWith("/tasks/")` は `/tasks/abc/def/ghi` のようなネストパスもマッチする。taskId に `/` が含まれることはない（UUID 形式）が、予期しない URL がマッチしてしまう。
  - 根拠: `coding-conventions.md` Section 6「Follow the principle of least surprise」に違反。

- **M-09: status-store の `trimStatusRecords` が全レコードをソートしてから削除する非効率な実装**
  - 影響ファイル: `/services/status-store/src/server.ts` 行 69-81
  - 説明: イベント受信のたびに `Array.from(tasks.values()).sort(...)` を実行する。MAX_TASKS=200 では問題にならないが、設計として O(n log n) のコストが毎回発生する。
  - 根拠: `coding-conventions.md` Section 15「Choose appropriate data structures」に違反。

- **M-10: health エンドポイントが認証なしで内部情報を漏洩**
  - 影響ファイル:
    - `/services/knowledge-adapter/src/server.ts` 行 217-219（`repoRoot` を返す）
    - `/services/status-store/src/server.ts` 行 134（`tasks.size` を返す）
  - 説明: knowledge-adapter の `/health` がファイルシステム上の `repoRoot` パスを返し、status-store が現在のタスク数を返す。認証なしで到達可能なため、攻撃者にシステム構成情報を与える。
  - 根拠: `coding-conventions.md` Section 14「Follow the principle of least privilege」に違反。

- **M-11: `loadRoutingRules` が同期 `readFileSync` を使用**
  - 影響ファイル: `/services/dispatcher/src/server.ts` 行 27-68
  - 説明: 起動時の 1 回だけとはいえ、`coding-conventions.md` Section 12「Prefer async/await over raw Promises」の精神に反する。また、ファイルが存在しない場合やパースに失敗した場合のエラーメッセージが不十分。
  - 根拠: `coding-conventions.md` Section 12 に違反（軽度）。

### Low

- **L-01: `HttpError` が `name` プロパティを設定しない**
  - 影響ファイル: `/services/shared/http.ts` 行 3-9
  - 説明: `Error` を継承するが `this.name = "HttpError"` を設定していないため、`error.name` は `"Error"` のまま。ログやデバッグ時に区別しにくい。
  - 根拠: `coding-conventions.md` Section 7「Provide meaningful error messages」に違反（軽度）。

- **L-02: 複数の env 変数名エイリアスが未文書化**
  - 影響ファイル: 全サーバーファイル
  - 説明: `CLAUDE_ADAPTER_API_TOKEN ?? CHATLOBBY_INTERNAL_API_TOKEN`, `STATUS_STORE_URL ?? CHATLOBBY_STATUS_STORE_URL` など、複数の env 変数名が使用されているが、どちらが推奨でどちらが後方互換かの文書がない。
  - 根拠: `coding-conventions.md` Section 13「Make decision points explicit」に違反。

- **L-03: `server.ts` ファイルのコード行数が convention の上限に近い**
  - 影響ファイル:
    - `/services/codex-adapter/src/server.ts` (265 行)
    - `/services/claude-adapter/src/server.ts` (233 行)
  - 説明: `coding-conventions.md` Section 5「Keep files under 300 lines when practical」に対し、サーバー起動・ルーティング・タスク管理・status publish がすべて 1 ファイルに収まっている。関心の分離が不十分。
  - 根拠: `coding-conventions.md` Section 5 に違反（軽度、300 行以内ではある）。

- **L-04: import 順序の規約不遵守**
  - 影響ファイル: `/services/knowledge-adapter/src/server.ts` 行 1-8
  - 説明: `coding-conventions.md` Section 6 では「Standard library → Third-party → Internal absolute → Internal relative」の順で空行区切りとされているが、knowledge-adapter は standard library と internal import の間に空行がない。他のサービスも同様。
  - 根拠: `coding-conventions.md` Section 6 に違反。

- **L-05: `process.env` をそのまま子プロセスに渡している**
  - 影響ファイル:
    - `/services/claude-adapter/src/server.ts` 行 47
    - `/services/codex-adapter/src/server.ts` 行 77
  - 説明: `env: process.env` は `CHATLOBBY_INTERNAL_API_TOKEN` を含むすべての環境変数を子プロセスに継承させる。最小権限の原則に反する。
  - 根拠: `coding-conventions.md` Section 14「Follow the principle of least privilege」に違反（軽度）。

---

## Review Dimensions

### Tech Lead Review

#### Debt Prevention

- TD-001（adapter 間のコード重複）は M-03 で確認。open のまま改善が進んでいない。
- TD-003（in-memory status store）は現状通り。
- TD-004（リクエストボディサイズ制限）は C-03 で確認。TD 記録はあるが「最低限のサイズ上限」すら未実装であり、重大度の評価が甘い。
- TD-005（CLI 引数長制限）は C-01 のインジェクション問題と重複。TD には記録されているが、セキュリティ面の記述がない。
- TD-007（graceful shutdown 欠如）は H-01 で確認。open のまま。
- 未登録の Tech Debt:
  - dispatcher のブロッキングポーリング（H-07）が tech debt registry に未登録。
  - `repoPath` によるパストラバーサル（H-08）が tech debt registry に未登録。
  - `WorkerName` / `TaskState` の型重複（M-01, M-02）が tech debt registry に未登録。
  - status publish のエラー握りつぶし（M-05）が tech debt registry に未登録。

#### Complexity Versus Value

- 各サービスの構造自体はシンプルで、ADR-009 から ADR-015 で決定された最小 HTTP adapter + CLI ラッパーの設計方針に合致している。
- ただし、同一パターンの重複（M-03）は「シンプルさ」ではなく「手抜き」であり、保守コストを増大させる。

#### Decomposition and Boundaries

- `shared/` ディレクトリに `http.ts`, `tasks.ts`, `status.ts` が配置されており、共通機能の分離は適切な方向性。
- しかし、各 `server.ts` がサーバー起動・ルーティング・ビジネスロジック・子プロセス管理をすべて担っており、関心の分離が不十分。
- ADR-009 で「最小の adapter」とされた設計を理由に分離を怠っている可能性がある。

#### Alignment With Declared Design

- ADR-009: `POST /tasks`, `GET /tasks`, `GET /tasks/:id`, `GET /health` の最小 API — 準拠。
- ADR-011: Claude と同型の adapter 境界 — 準拠（ただし M-03 のコード重複が問題）。
- ADR-012: knowledge adapter の search / read API — 準拠。
- ADR-013: dispatcher の rule-based routing — 準拠。routing 結果と理由が返却される。
- ADR-014: bearer token 保護 — 準拠。ただし H-04 のタイミング攻撃脆弱性あり。
- ADR-015: adapter push 型 status store — 準拠。ただし M-05 のエラー握りつぶしが best-effort の度合いを超えている。
- アーキテクチャ文書の Status Model: `statusId`, `worker`, `state`, `approvalState`, `currentStep`, `lastAction`, `resultSummary`, `updatedAt` — すべて `StatusRecord` 型に含まれ、準拠。

#### Senior-Engineer Smell Detection

- 全 `server.ts` で `createServer` の async コールバック内の例外処理が不完全。`readJsonBody` が reject した場合、トップレベルの try-catch に到達するが、`requireBearerToken` 以外の `HttpError` は一部のパスでのみ捕捉され、予期しない例外はレスポンスなしでコネクションを放置する可能性がある。
- `void publishStatusEvent(...).catch(() => {})` パターンが 12 箇所以上あり、機械的なコピーペーストの痕跡。
- `trimTasks` が呼ばれるタイミング（新タスク追加前）に対して、`MAX_TASKS` 到達時に running タスクが削除される設計は、本番環境での予測不能な挙動につながる。

#### Explanation Responsibility

- 各サービスは ADR で設計意図が明確に記述されている。
- しかし、コード内のコメントがほぼ皆無であり、`coding-conventions.md` Section 8「Explain 'why', not 'what'」に対するコンプライアンスが低い。特に `deriveApprovalState`, `normalizeKnowledgeQuery`, `parseCodexJsonl` のようなドメインロジック関数にコメントがない。

### Security Review

- C-01: CLI フラグインジェクション — Critical
- C-02: workingDirectory パストラバーサル — Critical
- C-03: リクエストボディ無制限 — Critical（DoS）
- H-04: タイミング攻撃 — High
- H-08: repoPath パストラバーサル — High
- M-10: health エンドポイントの情報漏洩 — Medium
- L-05: 環境変数の子プロセス漏洩 — Low

### Code Review

- H-05: `parseCodexJsonl` の未処理例外 — High
- H-06: 空ボディのデフォルト値 — High
- M-01 から M-11: 上記の通り
- L-01 から L-04: 上記の通り
- 全体的なコードスタイルは一貫しており、`coding-conventions.md` Section 4 の命名規約（camelCase, PascalCase）には概ね準拠。
- `const` の使用、async/await の活用、テンプレートリテラルの使用は適切。

---

## Implementation Response Plan

- Date: (未記入 — 修正着手時に記入)
- Reviewer: (修正者が記入)
- Base Commit: (修正時の最新コミットを記入)
- Plan Summary: (修正計画を記入)
- Planned Fixes: (修正対象を記入)
- Deferred Items: (延期項目を記入)

---

## Follow-Up Review History

### Entry 1

- Date: (修正完了後に記入)
- Reviewer: (再レビュー担当者が記入)
- Base Commit: (再レビュー時のコミットを記入)
- Review Type: (同一のレビューレンズを適用)
- References: (対応する Plan items を参照)
- Result: (修正結果を記入)
- Notes: (補足を記入)
- Remaining Risks: (残存リスクを記入)
- Risk Handling:
  - accepted residual risk with monitoring or next-review trigger
  - deferred planned work with tracked destination document or phase
  - explicit user decision required
  - unresolved finding requiring another fix-and-review cycle
