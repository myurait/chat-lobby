# Review

- Date: 2026-04-10T07:58:25Z (UTC) / 2026-04-10T16:58:25+09:00 (JST)
- Reviewer: Claude Opus 4.6 (1M context)
- Base Commit: 9e0b79edbb7a9189956cc4ff49be36d4bc38d3e8
- Scope: Python tools, OpenWebUI pipes, docker-compose.yml, .env.example, 全体コードベースの敵対的監査
- Review Type: security review + code review + tech lead review
- Trigger: ユーザーからの明示的依頼。元実装者（Codex）が品質懸念で解雇されたことを前提に、全ファイルを疑いの目で精査する。
- Criteria:
  - セキュリティ: インジェクション、パストラバーサル、SSRF、資格情報管理、認証トークン管理
  - コード品質: エラーハンドリング、入力バリデーション、コーディング規約遵守
  - アーキテクチャ準拠: ADR-005〜ADR-008、design/02-architecture.md との整合性
  - テスト: rules/testing.md に基づくカバレッジ
  - Docker/デプロイ: ポート露出、ネットワーク分離、シークレット管理

---

## Findings

### Critical

- **C-01: publish pipe が subprocess を呼ぶ際に `repo` パラメータのパストラバーサルを検証していない**
  - File: `tools/openwebui/chatlobby_publish_pipe.py` 行 106, 111-116
  - ユーザーが JSON 内で `"repo": "/etc"` や `"repo": "../../"` を渡すと、publish_to_repo.py の `--repo` 引数にそのまま渡る。publish_to_repo.py 側は `validate_repo_layout()` で `docs/specs/decisions/worklog` の存在を確認するが、攻撃者がそれらのディレクトリを持つ場所を指定すれば任意ディレクトリにファイルを書き込める。Open WebUI コンテナ内で実行されるため、コンテナ内の任意パスへの書き込みとなる。
  - 影響: コンテナ内任意ファイル書き込み

- **C-02: publish pipe の subprocess 呼び出しで `--body` にユーザー入力がそのまま CLI 引数として渡される**
  - File: `tools/openwebui/chatlobby_publish_pipe.py` 行 111-124
  - `content.strip()` がそのまま `--body` の引数値として渡される。`subprocess.run` は `shell=False` なのでシェルインジェクションは発生しないが、OS の引数長制限（通常 ARG_MAX）を超える body が渡されると `subprocess.run` が `OSError` で失敗する。この例外は `try/except` で捕捉されていない。
  - 影響: 長い body でクラッシュ。これは TD-005 に既知登録があるが、pipe 側にも例外ハンドリングが不在。

- **C-03: knowledge query pipe がユーザー指定の `repoPath` を制限なく knowledge adapter に転送する**
  - File: `tools/openwebui/chatlobby_knowledge_query_pipe.py` 行 107-108, 118-119
  - ユーザーが `{"path": "/etc/passwd"}` を送ると、knowledge adapter の `/read` エンドポイントに転送される。adapter 側の `ensurePathInsideRepo` は `repoPath` パラメータで repoRoot を変更できるため、`{"path": "/etc/passwd", "repoPath": "/"}` を送れば repoRoot が `/` になり、`ensurePathInsideRepo` のチェックを通過する。
  - File: `services/knowledge-adapter/src/server.ts` 行 35-46
  - `ensureRepoRoot` は任意の文字列を `resolve()` するだけで、許可リストも prefix チェックもない。`repoPath` がユーザー制御可能な時点で、パストラバーサル防御が無効化される。
  - 影響: knowledge adapter 経由でホスト上の任意ファイル読み取り（adapter がホスト側で動作するため）

### High

- **H-01: 全 pipe の `_request_json` / `urllib.request.urlopen` にタイムアウトが設定されていない**
  - Files:
    - `tools/openwebui/chatlobby_claude_task_pipe.py` 行 89
    - `tools/openwebui/chatlobby_codex_task_pipe.py` 行 89
    - `tools/openwebui/chatlobby_knowledge_query_pipe.py` 行 89
    - `tools/openwebui/chatlobby_dispatch_task_pipe.py` 行 96
    - `tools/openwebui/chatlobby_status_panel_pipe.py` 行 93
    - `tools/openwebui_sync.py` 行 22
  - `urllib.request.urlopen` のデフォルトタイムアウトは無制限。adapter が応答しない場合、Open WebUI のワーカースレッドが永久にブロックされる。
  - 影響: adapter 不達時に Open WebUI のワーカースレッドがハング、サービス品質低下

- **H-02: claude/codex pipe の同期 polling が Open WebUI ワーカースレッドをデフォルト 180 秒間ブロックする**
  - Files:
    - `tools/openwebui/chatlobby_claude_task_pipe.py` 行 125-152
    - `tools/openwebui/chatlobby_codex_task_pipe.py` 行 125-152
  - `time.sleep()` を `while` ループ内で呼んでおり、最大 180 秒間 Open WebUI のワーカーを占有する。これは TD-006 に既知登録があるが、severity が「open」のまま対策なし。
  - 影響: 同時リクエストの処理能力低下、DoS ベクトル

- **H-03: `TERMINAL_SERVER_CONNECTIONS` 内の `${OPEN_TERMINAL_API_KEY}` が Compose の変数補間で展開されない**
  - File: `docker-compose.yml` 行 52-53
  - `TERMINAL_SERVER_CONNECTIONS` は YAML の `>-` (folded block scalar) で定義されている。その中に `${OPEN_TERMINAL_API_KEY}` があるが、これは Docker Compose の変数展開対象内にあるので展開される。しかし JSON 文字列内に `${}` が含まれる構造は、値に `$` を含む API キーを使うと JSON が壊れる。
  - 修正後の精査: Docker Compose は `>-` 内でも変数展開する。ただし API キーに `"` や `\` が含まれると JSON 構文が壊れるリスクがある。
  - 影響: 特殊文字を含む API キーで Open Terminal 接続が壊れる

- **H-04: OpenWebUI pipe のテストが一切存在しない**
  - 全6つの pipe ファイル (`chatlobby_publish_pipe.py`, `chatlobby_claude_task_pipe.py`, `chatlobby_codex_task_pipe.py`, `chatlobby_knowledge_query_pipe.py`, `chatlobby_dispatch_task_pipe.py`, `chatlobby_status_panel_pipe.py`) に対するテストが存在しない。
  - `tools/openwebui_sync.py` のテストも存在しない。
  - `tests/` ディレクトリには TypeScript service のテスト（`test_dispatcher.py`, `test_codex_adapter.py`, `test_status_store.py`, `test_knowledge_adapter.py`）と `test_publish_to_repo.py` はあるが、pipe のユニットテストはゼロ。
  - `development-docs/rules/testing.md` Section 5: "New code must have tests." に対する違反。
  - 影響: pipe ロジックの回帰検知不能

- **H-05: `_extract_payload_text` の markdown fence 解析が脆弱**
  - Files: 全 pipe（6ファイル全てに同一実装が重複）
  - ` ```json ` の後に ` ``` ` を探すが、ネストされたコードブロックやメッセージ内に複数の fence がある場合に誤解析する。例えば ` ```json\n{"a":"```"}\n``` ` は `{"a":"` だけを抽出する。
  - 影響: 正常に見えるがエッジケースで JSON パースエラーになり、ユーザーに不親切なエラーメッセージが返る

- **H-06: sync スクリプト群のコード重複が rules 違反**
  - Files: `tools/sync_openwebui_publish_pipe.py`, `tools/sync_openwebui_claude_pipe.py`, `tools/sync_openwebui_codex_pipe.py`, `tools/sync_openwebui_knowledge_pipe.py`, `tools/sync_openwebui_dispatch_pipe.py`, `tools/sync_openwebui_status_pipe.py`
  - 6つの sync スクリプトが事実上同一の `build_parser()` / `main()` 構造を持ち、差分は `function_id`, `name`, `description`, `DEFAULT_PIPE_FILE` の4値のみ。これは `coding-conventions.md` Section 3 "Keep functions and modules focused on one responsibility" および Section 5 "One primary export per file" の精神に反する。
  - TD-002 で既知登録されているが、sync 側のコード重複は登録なし。
  - 影響: 修正漏れリスク、保守コスト

### Medium

- **M-01: publish pipe の `publish_tool_path` valve がユーザー（管理者）から任意の実行パスを設定可能**
  - File: `tools/openwebui/chatlobby_publish_pipe.py` 行 47-49
  - `publish_tool_path` valve でコンテナ内の任意 Python スクリプトを指定して `subprocess.run` で実行できる。これは管理者のみが設定可能だが、valve の意図に比してリスクが大きい。
  - 影響: 管理者が意図せず危険なパスを設定するとコンテナ内の任意コード実行

- **M-02: `openwebui_sync.py` の `sign_in` 関数がパスワードをメモリに保持し続ける**
  - File: `tools/openwebui_sync.py` 行 31-39
  - パスワードが `argparse.Namespace` オブジェクトとプロセスメモリに残存する。短命 CLI なので実質的リスクは低いが、セキュリティベストプラクティスからは逸脱。
  - 影響: 低。メモリダンプ時のパスワード漏洩リスク

- **M-03: pipe の `_request_json` メソッドが非 HTTP エラー（ネットワーク到達不能、DNS 解決失敗）を捕捉していない**
  - Files: 全 pipe の `_request_json` メソッド
  - `urllib.error.HTTPError` のみ `except` で捕捉しているが、`urllib.error.URLError`（接続拒否、DNS 失敗）や `socket.timeout` は捕捉されない。adapter が起動していない場合、`URLError` が pipe の `pipe()` メソッドから未処理で伝播し、Open WebUI がユーザーに内部スタックトレースを返す可能性がある。
  - 影響: adapter 不達時のユーザー体験悪化

- **M-04: `.env.example` に `CHATLOBBY_STATUS_STORE_URL` が記載されているが `docker-compose.yml` は status store をコンテナとして起動しない**
  - File: `.env.example` 行 9, `docker-compose.yml`
  - `.env.example` には `CHATLOBBY_STATUS_STORE_URL=http://127.0.0.1:8791` があるが、status store はホスト側で手動起動する設計。README にも手動起動の手順が記載されている。ただし `.env.example` にこの URL がある理由や、ホスト側起動が前提である旨の説明がない。
  - 影響: セットアップ時の混乱

- **M-05: codex pipe が `bypassApprovalsAndSandbox` フィールドをユーザー入力からそのまま adapter に転送する**
  - File: `tools/openwebui/chatlobby_codex_task_pipe.py` 行 113
  - `bypassApprovalsAndSandbox` は安全機構の無効化フラグである。pipe がこれをフィルタなしで転送するのは危険。adapter 側で `CODEX_BYPASS_APPROVALS_AND_SANDBOX` 環境変数によるガードがある可能性があるが、pipe レベルでの防御がない。
  - 影響: ユーザーが意図せず安全機構を無効化するリスク

- **M-06: `docker-compose.yml` で `open-terminal` コンテナが `OPEN_TERMINAL_EXECUTE_TIMEOUT: 5` と極端に短いタイムアウトを設定**
  - File: `docker-compose.yml` 行 17
  - 5秒のタイムアウトでは、ファイルブラウザ操作や `git clone` 等の時間がかかる操作が失敗する可能性がある。
  - 影響: ターミナル操作のユーザー体験悪化

- **M-07: `_extract_payload_text` が全6 pipe に完全重複**
  - Files: 全 pipe ファイル
  - TD-002 で「Python pipe は Open WebUI function が単一ファイル前提のため helper 抽出が未着手」と記録済みだが、同一メソッドが6ファイルに重複している状態は `coding-conventions.md` Section 2.2 "Check whether copy-paste patterns should be extracted into shared code" に反する。
  - 影響: 一箇所の修正が5箇所に波及しない回帰リスク

- **M-08: publish_to_repo.py の `TEMPLATES_DIR` が `ROOT_DIR / "docs" / "templates"` を指すが、コンテナ内マウントパスと一致しない可能性**
  - File: `tools/publish_to_repo.py` 行 14-15
  - `ROOT_DIR` は `Path(__file__).resolve().parents[1]` で解決される。コンテナ内では `/workspace/chatlobby/tools/publish_to_repo.py` にマウントされるため `ROOT_DIR` は `/workspace/chatlobby` となり、`TEMPLATES_DIR` は `/workspace/chatlobby/docs/templates` となる。`docs` ディレクトリは `./docs:/workspace/chatlobby/docs:ro` でマウントされているので到達可能だが、テンプレートファイルの存在確認がコンテナ内で行われない場合は `FileNotFoundError` になる。
  - 影響: テンプレート不在時のエラーメッセージがユーザーに不親切

### Low

- **L-01: pipe ファイルのドキュメント文字列がファイル先頭の `""" title: ... """` のみで、クラスやメソッドの docstring がない**
  - Files: 全 pipe ファイル
  - `coding-conventions.md` Section 9 "Document public APIs and complex functions" に対して不足。
  - 影響: 保守性低下

- **L-02: `.env.example` のプレースホルダー値が `change-this-*` パターンで統一されていない**
  - File: `.env.example`
  - `WEBUI_ADMIN_EMAIL=admin@example.com` は「変更してください」パターンではなく具体的な値。一貫性がない。
  - 影響: 軽微。ユーザーが変更を忘れるリスク

- **L-03: `openwebui_sync.py` の `ensure_function` 内で not-found 判定がハードコードされた文字列比較**
  - File: `tools/openwebui_sync.py` 行 9, 69-70
  - `NOT_FOUND_DETAIL = "We could not find what you're looking for :/"` という Open WebUI 内部のエラーメッセージ文字列に依存している。Open WebUI のバージョンアップでこの文字列が変わると動作しなくなる。
  - 影響: Open WebUI アップデート時の脆弱性

- **L-04: codex pipe の HELP_TEXT にデフォルトモデル `gpt-5.4` が記載されているが実在性が不明**
  - File: `tools/openwebui/chatlobby_codex_task_pipe.py` 行 28
  - ユーザーに誤解を与える可能性。
  - 影響: 軽微

- **L-05: `publish_to_repo.py` の `slugify` 関数が ASCII のみ対応で、日本語タイトルに対してスラグ全体が空になり `ValueError` になる**
  - File: `tools/publish_to_repo.py` 行 36-41
  - `re.sub(r"[^a-zA-Z0-9]+", "-", ...)` が日本語文字を全て `-` に置換し、`strip("-")` で空文字列になる。pipe 側で `slug` を明示しない場合、`title` から `slugify` される。日本語タイトルで `ValueError("Slug cannot be empty")` が発生する。
  - Product Language が English / Japanese と定義されている以上、日本語タイトルへの対応不足。
  - 影響: 日本語タイトルで publish が失敗

---

## Review Dimensions

### Tech Lead Review

#### Debt Prevention

- TD-002 (pipe helper 抽出未着手) がそのまま放置されており、6つの pipe で `_extract_payload_text`, `_parse_payload`, `_request_json` が完全重複。修正時の回帰リスクが高い。
- TD-005 (CLI 引数長制限) の影響が publish pipe にも波及しているが、pipe 側の catch がなく、tech debt が連鎖している。
- sync スクリプト群の重複は tech debt に未登録。

#### Complexity Versus Value

- 6つの個別 sync スクリプトは、1つの汎用 sync スクリプトに `--function-id`, `--name`, `--description`, `--pipe-file` を渡す形で置き換え可能。現在の構成は不要な複雑さ。

#### Decomposition and Boundaries

- pipe と adapter の境界は ADR-008, ADR-010, ADR-011, ADR-012, ADR-013 に準拠。
- ただし pipe 内の `_request_json` がエラー分類を adapter に委ねすぎており、ネットワークエラーとアプリケーションエラーの区別が pipe 側でできない。

#### Alignment With Declared Design

- ADR-005: Open Terminal は Compose 内部接続でホスト露出なし -- 準拠。ポート公開はない。
- ADR-006: workspace mount は `./workspace:/workspace` -- 準拠。
- ADR-007: publish_to_repo.py CLI が存在 -- 準拠。
- ADR-008: pipe から publish CLI を呼ぶ構成 -- 準拠。ただし C-01 の repo パス制限不在が安全性を損なう。
- ADR-014: bearer token による保護 -- pipe 側は valve で token を保持し adapter に送信。準拠。ただし token が空でも request は送信される（adapter 側で弾く前提）。
- `development-docs/project/design/02-architecture.md` の Operating Model: "Open WebUI 本体への改変は最小化" -- pipe は function registry 経由の登録で準拠。

#### Senior-Engineer Smell Detection

- knowledge adapter の `repoPath` パラメータがユーザー制御可能な状態で、サーバーサイドの path validation に頼る設計は、pipe 側での防御がなく脆弱。
- publish pipe の subprocess 呼び出しは、長期的には in-process 呼び出しに置き換えるべき（TD-005 とも連動）。
- `os.environ.get("CHATLOBBY_INTERNAL_API_TOKEN", "")` が pipe クラス定義時（import 時）に評価される。valve 設定で上書きしない限り、Open WebUI 再起動なしでは token 変更が反映されない。

#### Explanation Responsibility

- pipe の HELP_TEXT はユーザーに JSON フォーマットを説明しており、最低限の説明責任は果たしている。
- ただしエラー時のメッセージ（特に adapter 接続失敗時）がスタックトレースになるケースがあり、ユーザーに分かりにくい。

### Security Review

- **subprocess 安全性**: `shell=False` で実行。シェルインジェクションリスクはなし。ただし引数長制限の例外処理がない。
- **SSRF リスク**: pipe の `adapter_base_url` / `dispatcher_base_url` / `status_store_base_url` は valve で管理者が設定する。ユーザー入力から URL を構築していないため、直接の SSRF はなし。ただし valve 経由で管理者が任意 URL を設定可能。
- **パストラバーサル**: C-01 (publish pipe の `repo` パラメータ) と C-03 (knowledge pipe 経由の `repoPath`) が critical。
- **認証トークン管理**: ADR-014 に準拠。adapter 側で non-loopback bind 時に token 必須を強制。pipe 側は valve で token を保持。
- **Docker 構成**: Open Terminal はホストにポート公開なし（ADR-005 準拠）。Open WebUI のみホスト公開。

### Code Review

- `coding-conventions.md` Section 4 "File names: kebab-case for multi-word names": pipe ファイルは `chatlobby_publish_pipe.py`（snake_case）。kebab-case ルールとの不一致。ただし Python モジュールで kebab-case は import 不能なので、Python 固有の制約として許容される可能性がある。
- Section 6 "Import Order": 全 pipe ファイルで import 順序は stdlib -> pydantic -> open_webui で適切。
- Section 7 "Error Handling: Never swallow errors silently": pipe の `_request_json` で `urllib.error.URLError` を捕捉していない点が違反。
- Section 14 "Validate and sanitize all external input": C-01, C-03 が違反。

---

## Implementation Response Plan

- Date: (TBD -- 修正着手時に記入)
- Reviewer: (TBD)
- Base Commit: (TBD)
- Plan Summary: (TBD)
- Planned Fixes: (TBD)
- Deferred Items: (TBD)
