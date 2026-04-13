# Review

- Date: 2026-04-10T20:00:00+09:00
- Reviewer: Claude Opus 4.6 (1M context)
- Base Commit: 9e0b79e
- Scope: development-docs/ 配下の全ファイル -- ルール、設計、機能、ロードマップ、要件、レビュー、ログ、ナレッジ、インデックス
- Review Type: document review
- Trigger: 品質懸念で解雇された Codex エージェントが作成した文書群の全量敵対監査
- Criteria:
  - ルール間の内部矛盾はないか
  - 設計文書がアーキテクチャと矛盾していないか
  - 機能文書がロードマップと矛盾していないか
  - クロスリファレンス（ファイルパス、セクション参照、ADR 番号）は正確か
  - 参照先のファイルは実在するか
  - 言語ポリシーへの準拠は完全か
  - 文書階層は必要かつ適切か、過剰設計はないか
  - 重複コンテンツはないか
  - プロセスの重さはプロジェクト規模に見合っているか

---

## Findings

### Critical

- C-1: `development-docs/project/features/00-feature-index.md` にハードコードされた絶対パス
  - ファイル: `/Users/fox4foofighter/dev/chat-lobby/development-docs/features/00-feature-index.md`
  - 9箇所に `/Users/fox4foofighter/dev/chat-lobby/development-docs/` で始まる絶対パスが使われている。OSS 公開を目標に掲げながら、ローカルマシンの絶対パスが文書に焼き込まれている。他者が clone しても全リンクが壊れる。相対パスに修正すべき。

- C-2: `reference/historical-documents/INDEX.md` に存在しないファイルへの参照
  - ファイル: `/Users/fox4foofighter/dev/chat-lobby/development-docs/reference/historical-documents/INDEX.md`
  - `chatlobby_development_plan.md` と `chatlobby_roadmap.md` の canonical successor に `development-docs/project/roadmap/archives/roadmap_20260405174901_initial-roadmap.md` が記載されているが、このファイルは存在しない。実際のアーカイブ済みロードマップは `development-docs/project/roadmap/archives/roadmap_20260405174901_initial-roadmap.md` にある。壊れた参照がトレーサビリティチェーンを断っている。

### High

- H-1: レビュー証跡ファイルが上限 5 件を超えている（6 件）
  - ファイル: `/Users/fox4foofighter/dev/chat-lobby/development-docs/reviews/`
  - `development-process.md` Section 1 および `development-docs/project/reviews/README.md` は「最新 5 件のみ reviews/ に保持、古いファイルは archives/ へ移す」と定める。現在 6 件のレビュー証跡ファイルが reviews/ 直下に存在する。特に `review_20260409164528_roadmap-active-archive-structure.md` は development log Entry 8 で「archives/ へ移した」と記録されているにもかかわらず、reviews/ 直下に残り archives/ に存在しない。ログの記録が虚偽になっている。

- H-2: 開発ログ Entry 8 で言及されたレビューファイルが存在しない
  - ファイル: `/Users/fox4foofighter/dev/chat-lobby/development-docs/development-logs/log_20260409165428.md` Entry 8
  - `development-docs/project/reviews/review_20260410155928_conversation-continuity-foundation.md` を追加したと記録されているが、このファイルはリポジトリに存在しない。ログで記録された作業成果物が実際には存在しないため、トレーサビリティが壊れている。

- H-3: `development-docs/project/design/03-tech-debt-registry.md` が Markdown テーブルで書かれている
  - ファイル: `/Users/fox4foofighter/dev/chat-lobby/development-docs/design/03-tech-debt-registry.md`
  - `knowledge.md` Section 3 および `development-docs/project/reviews/README.md` は「レビュー証跡に Markdown テーブルを使わない」としている。tech debt registry は設計文書だがレビュー系文書ではないため厳密にはルール外だが、`coding-conventions.md` のユーザー向けグローバル CLAUDE.md にも「外部出力ではテーブルを使わずリストで代替する」とある。このテーブルはセルの横幅が極端に長く、可読性が壊れている。

- H-4: `knowledge.md` の言語分類が曖昧
  - ファイル: `/Users/fox4foofighter/dev/chat-lobby/development-docs/knowledge.md`
  - `language-policy.md` によれば、knowledge.md は「project-progress document」に該当し、Documentation Language（日本語）で記述すべき。しかし実際にはセクション 1--5 が全て英語で、セクション 6 のみ日本語。ファイルの大部分が言語ポリシーに違反している。「reusable lessons」が「stable rule」なのか「project-progress」なのかの分類判断を要求する。

- H-5: 読み順が 4 箇所で矛盾している
  - 影響ファイル:
    - `/Users/fox4foofighter/dev/chat-lobby/CLAUDE.md`
    - `/Users/fox4foofighter/dev/chat-lobby/development-docs/AI_KNOWLEDGE.md`
    - `/Users/fox4foofighter/dev/chat-lobby/development-docs/INDEX.md`
    - `/Users/fox4foofighter/dev/chat-lobby/development-docs/README.md`
  - CLAUDE.md は `AI_RUNTIME_RULES.md` -> `AI_KNOWLEDGE.md` -> `README.md` と指示。AI_KNOWLEDGE.md は `AI_RUNTIME_RULES.md` -> `language-policy.md` -> `INDEX.md` -> `coding-conventions.md` -> `development-process.md` と指示。INDEX.md は `AI_KNOWLEDGE.md` -> `AI_RUNTIME_RULES.md` -> `language-policy.md` -> `coding-conventions.md` -> `development-process.md` と指示。README.md は `AI_RUNTIME_RULES.md` -> `language-policy.md` -> `AI_KNOWLEDGE.md` -> `INDEX.md` と指示。4 つのエントリポイントが全て異なる順序を指示しており、どれが正しいのか判断できない。AI エージェントがどこから入っても混乱する構造になっている。

- H-6: `coding-conventions.md` Section 7 で Markdown テーブルを使用
  - ファイル: `/Users/fox4foofighter/dev/chat-lobby/development-docs/rules/coding-conventions.md` 64--72 行目
  - ルール文書自体が Error Handling Patterns で Markdown テーブルを使用している。ユーザーの CLAUDE.md グローバル指示は「外部出力ではテーブルを使わず箇条書きやコードブロックで代替する」と定める。ルール文書は外部出力として最も広く参照されるものであり、自身が定めたい規範に反している。

### Medium

- M-1: `AI_RUNTIME_RULES.md` Section 4 と `coding-conventions.md` Section 20 の内容重複
  - `AI_RUNTIME_RULES.md` の「File Operation Rule: Always read a file before writing or editing it.」と `coding-conventions.md` の「File Operation Rule: Always read a file before writing or editing it.」が完全に重複している。single source of truth の原則に反する。どちらかが変更されたとき同期が漏れるリスクがある。

- M-2: `knowledge.md` と `development-process.md` の広範な内容重複
  - `knowledge.md` Section 2 "Documentation Discipline" の内容の大部分が `development-process.md` Section 4 "Documentation Rules" と重複している。レビュー証跡の命名規則、アーカイブルール、ロードマップファイルのルール、理想体験文書の正本ルールなど、少なくとも 15 項目が両方に存在する。片方が更新されたとき必ず不整合が発生する構造になっている。

- M-3: `knowledge.md` と `AI_KNOWLEDGE.md` の役割境界が不明
  - `AI_KNOWLEDGE.md` は「Start Here」として 14 項目の読み順を示し、「Working Rules」としてファイル管理ルールを列挙する。`knowledge.md` は「reusable lessons」として開発運用の知恵を記録する。しかし `AI_KNOWLEDGE.md` の Working Rules には `knowledge.md` Section 2 と重複するルールが多数含まれている。2 つの文書の責務境界が不明確。

- M-4: epics の feature_template.md と実際の epic 文書の構造不一致
  - `features/feature_template.md` には `Roadmap Readiness` と `Validation Scenarios` セクションがあるが、epics（01--06）にはこれらが無い。代わりに epics は `Promotion Condition` のみを持つ。テンプレートが epics に適用されるのか supporting features にのみ適用されるのかが不明。epic 用テンプレートが存在しないのに、epics が一貫した構造で書かれている。暗黙のテンプレートが存在しているが文書化されていない。

- M-5: `development-docs/project/design/01-project-charter.md` が完全に日本語で書かれている
  - ファイル: `/Users/fox4foofighter/dev/chat-lobby/development-docs/design/01-project-charter.md`
  - `language-policy.md` の Document Language Rules で、設計文書は「Documents that evolve with project progress should be written in Documentation Language」に該当するため日本語で正しいと解釈できる。しかし project charter は通常、変更頻度が低く principle-stable に近い。rule documents と project-progress documents の境界にある文書の分類が曖昧。

- M-6: 14 ステップ開発フローは個人プロジェクトとして過剰
  - ファイル: `/Users/fox4foofighter/dev/chat-lobby/development-docs/rules/development-process.md` Section 8
  - ステップ 0--14 の全 15 ステップ（ステップ 0 含む）が「Every step is mandatory」とされている。個人開発プロジェクトで、理想体験入力の確認、要件発見、計画入力の導出、ロードマップ選定、サイクル受入定義、実装、テスト、文書更新、開発ログ、レビュー、修正、再チェック、フォローアップレビュー、コミット、ロードマップ更新を全て義務化するのは、作業速度を著しく落とす。特に Stage A（ステップ 0--4）は多くの小規模変更で形骸化する。

- M-7: バックログの 8 つの必須メタデータフィールドは個人プロジェクトとして過剰
  - ファイル: `/Users/fox4foofighter/dev/chat-lobby/development-docs/features/01-feature-backlog.md`
  - 各バックログ項目に Source, Status, Priority Assumption, Expected Order, Blockers, Experience Tie, Thickness, Design Impact, Current Design Constraint, Supporting Feature, Why Not In Roadmap Yet の 11 フィールドを要求している。12 項目の deferred request に対してこの粒度は、バックログの維持自体が主作業になるリスクがある。

- M-8: 要件発見プロセスの費用対効果
  - ファイル: `/Users/fox4foofighter/dev/chat-lobby/development-docs/requirements/`
  - 要件発見ルール、理想体験インタビューテンプレート、理想体験スペックテンプレートの 3 文書が存在する。プライマリユーザーが自分自身である個人プロジェクトで、構造化インタビューテンプレートを使って自分自身にインタビューするプロセスを義務化しているのは過剰。ただし、AI エージェントが開発者の意図を引き出すためのツールとして使うなら妥当性がある。この使い方が文書で明確にされていない。

- M-9: `roadmap_consultation_template.md` と `roadmap_share_template.md` の重複
  - 両テンプレートは構造がほぼ同じ（理想体験に対する現在地、今回進む範囲、残る範囲、閉め質問）。差分は「decision request」か「sharing」かの目的のみ。2 つのテンプレートに分ける必要性が薄い。

- M-10: `CLAUDE.md` が Codex のフォールバック動作を定義しているが、Codex は解雇済み
  - ファイル: `/Users/fox4foofighter/dev/chat-lobby/CLAUDE.md` 19 行目
  - 「Runtimes that cannot spawn subagents (e.g., Codex) must still apply the review criteria...」と記載されているが、Codex エージェントは品質懸念で解雇されている。死んだランタイムへのフォールバック指示が残っている。

- M-11: `decisions.md` の ADR 言語が一貫して日本語だが、ADR の分類が不明
  - ファイル: `/Users/fox4foofighter/dev/chat-lobby/development-docs/decisions.md`
  - `language-policy.md` は「ADRs and project decisions unless the project explicitly chooses otherwise」を project-progress documents に分類しているため日本語は正しい。ただし、ADR-001 から ADR-017 の全てが技術決定であり、一部は stable rule に近い性質を持つ。language policy の例外ルールで「long-lived exception は本文書か ADR に反映する」とあるが、ADR 自体の言語例外は未定義。

- M-12: tech debt registry に Date フィールドが全て同じ（2026-04-05）
  - ファイル: `/Users/fox4foofighter/dev/chat-lobby/development-docs/design/03-tech-debt-registry.md`
  - TD-001 から TD-009 の全 9 項目が 2026-04-05 の同じ日付。Phase A--F を跨ぐ技術的負債が全て同一日に登録されたことは不自然。一括登録された疑いがあり、個別の発生時点が正確に記録されていない可能性がある。

### Low

- L-1: `INDEX.md` の Directory Map が不完全
  - `requirements/` がディレクトリマップのツリーに含まれていない。

- L-2: `README.md` と `README.ja.md` の読み順が微妙に異なる
  - `README.md` は 9 項目のリスト。`README.ja.md` も 9 項目だが、パス表記が微妙に異なる（`roadmap/` 直下 vs. "the single active roadmap file"）。

- L-3: `reference/reference_template.md` が一度も使用されていない
  - `reference/` ディレクトリには `historical-documents/` と `README.md` のみが実用されており、`reference_template.md` を使った Reference Note ファイルが一つも存在しない。未使用のテンプレートが残っている。

- L-4: `development-logs/log_template.md` の期間フィールドが単一値
  - テンプレートの `Period:` は単一日付のみを想定しているが、実際のログは複数日にまたがる。

- L-5: `development-docs/project/features/epics/` の番号体系にギャップが予想される
  - 現在 01--06 の 6 件。これらが全て `candidate` ステータスであり、ロードマップに直接マッピングされているのは 3 件（02, 03, 04 -> Milestones 1, 2, 3 を介して間接参照）。残り 3 件（01, 05, 06）はロードマップから直接参照されていない。

---

## Review Dimensions

### Document Review

- 合計 90 以上のファイルを監査対象とした（reviews/archives/ 含む）。
- 文書間のクロスリファレンスは概ね正確だが、2 箇所で壊れた参照が見つかった（C-2, H-2）。
- 言語ポリシーの準拠は rules/ 配下と template 文書では完全。知識文書（knowledge.md）で重大な違反がある（H-4）。
- 文書構造は体系的だが、個人プロジェクトの規模に対して過剰な層が存在する（M-6, M-7, M-8）。

### Design Review

- Simpler alternative considered:
  - 15 ステップの開発フローは、Stage A（ステップ 0--4）を「既存ロードマップ項目への追加作業の場合はスキップ可能」とするだけで、日常的な作業速度が大幅に改善する。
  - 要件発見プロセスは、AI エージェントが開発者の意図を引き出すためのプロンプトテンプレートとして位置づけ直せば、形式的なプロセスから実用的なツールに変わる。
  - knowledge.md と AI_KNOWLEDGE.md の Working Rules は統合可能。
- Traceability from user problem to planning document:
  - 理想体験 -> epic -> supporting feature -> backlog のトレーサビリティチェーンは健全。ただし historical documents INDEX の壊れた参照（C-2）がチェーンの起点を損なっている。
- Intended experience change:
  - 文書構造自体は「AI エージェントが自律的に開発を進められる」という体験を支えるために設計されている。この目的に対しては構造の深さに一定の妥当性がある。ただし、agent が守れないほど多いルールは agent の信頼性を下げる。
- Validation completeness:
  - ロードマップの validation scenario は会話シナリオベースで定義されており適切。ただし Milestone 1 の Active Cycle Candidate にある verification evidence の 1 つ（`development-docs/project/reviews/review_20260410155928_conversation-continuity-foundation.md`）が存在しない（H-2）。

### Tech Lead Review

#### Debt Prevention

- 文書間の内容重複（M-1, M-2, M-3）は、将来の不整合発生が確実な技術的負債。knowledge.md の Working Rules セクションは development-process.md の劣化コピーになりつつある。

#### Complexity Versus Value

- 個人プロジェクトに対して enterprise-grade のガバナンス構造が導入されている。これは AI エージェントによる自律開発という特殊なコンテキストでは部分的に正当化されるが、プロセスの重さがエージェント自身にも遵守されていない（H-1: アーカイブルール違反、H-2: 存在しないファイルの記録）ことから、プロセスが実効性を持っていない兆候がある。

#### Decomposition and Boundaries

- `knowledge.md` / `AI_KNOWLEDGE.md` / `development-process.md` の責務境界が不明確で、同じルールが複数の場所に散在している。

#### Alignment With Declared Design

- ロードマップ、epic、支援機能、バックログの構造は理想体験文書に対して正確に整合している。ADR もアーキテクチャ文書と一致している。

#### Senior-Engineer Smell Detection

- ルールがルールを参照し、そのルールがさらに別のルールを参照する多段参照が多い。例: CLAUDE.md -> AI_KNOWLEDGE.md -> development-process.md -> testing.md。agent が全てを正確に辿れる保証がなく、参照の深さが遵守率を下げている。
- 9 項目の tech debt が全て同一日に open ステータスで登録され、1 件も closed になっていない。tech debt registry が管理ツールとして機能していない。

#### Explanation Responsibility

- 文書群全体として「なぜこの構造が必要か」の説明が不足している。特に、要件発見プロセス、15 ステップ開発フロー、バックログの 11 フィールドについて、個人プロジェクトでの必要性の根拠が無い。「AI エージェントが自律的に判断するための構造化入力として必要」という暗黙の前提があるが、明文化されていない。

---

## Findings Summary

- Critical: 2 件（C-1, C-2）
- High: 6 件（H-1 -- H-6）
- Medium: 12 件（M-1 -- M-12）
- Low: 5 件（L-1 -- L-5）
- 合計: 25 件
