# Review

Use flat bullets and headings. Do not use Markdown tables in review evidence.

- Date: 2026-04-10T14:25:00+09:00
- Reviewer: Claude Opus 4.6
- Base Commit: 07944d7 (未コミットの working tree 状態をレビュー)
- Scope: language-policy rollout — 横断的な参照統一とテンプレート英語化
- Review Type: document review
- Trigger: ユーザーによる development-docs の現在の変更に対するドキュメントレビュー依頼
- Criteria:
  - すべてのアクティブ文書が `rules/language-policy.md` を canonical source として一貫して参照しているか？
  - 旧 canonical location (`design/01-project-charter.md`) への陳腐化した参照がアクティブ文書に残っていないか？
  - テンプレート書き換えが新しい Template Documents ルールに従いつつ、元の意図を保持しているか？
  - 選択されたアプローチは、よりシンプルな代替案と比較して正当化されるか？
  - 不必要な複雑性やレイヤーを追加していないか？
  - ユーザーがこの変更の存在理由とそれが何を可能にするかを理解できるか？

---

## Findings

### Critical

- なし

### High

- H-1: `rules/coding-conventions.md` §2 が委譲により実用的な具体性を失っている
  - 旧版は English 対象を具体列挙していた: inline code comments, JSDoc/TSDoc annotations, README files, API documentation, user-facing error messages in logs
  - 新版は抽象的な委譲の3行のみ
  - `language-policy.md` §3 には完全なリストがあるが、実装中に `coding-conventions.md` だけを参照する開発者は、JSDoc やAPIドキュメントや特定のエラーメッセージが英語対象かどうかを別ファイルを開かないと判断できない
  - 対象ファイル: `rules/coding-conventions.md` 9-13行目
  - 推奨: `language-policy.md` への委譲は維持しつつ、代表例を1行追加する。例: `For the full list of code-internal targets, see rules/language-policy.md section 3 (identifiers, type names, code comments, JSDoc/TSDoc, API field names).`

### Medium

- M-1: `design/01-project-charter.md` の Language Policy セクションが2行のスタブになっている
  - 「あちらのポリシーに従う」とだけ書いてあり、charter 固有の情報がない
  - 他の charter セクション（Goals, Approach 等）はプロジェクト固有の実質的な内容を持つ
  - スタブセクションが存在する理由が読み手に不明瞭
  - 対象ファイル: `design/01-project-charter.md` 16-18行目
  - 推奨: Language Policy セクション見出しを削除して `rules/language-policy.md` への参照を charter 冒頭付近に1行置くか、セットアップ時のリマインダーとして現状維持するか。どちらも影響は軽微。

- M-2: roadmap テンプレートの「良い例の方向」がプロジェクト固有の日本語から汎用的な英語に変わっている
  - 旧テンプレートは chat-lobby 固有の文脈（会話の継続、文脈の再入力）を含む例文だった
  - 新しい英語テンプレートも意味は同等だが、プロジェクト固有のガイダンスなのか汎用テンプレートの例なのか区別がつきにくい
  - 対象ファイル: `roadmap/roadmap_consultation_template.md`, `roadmap/roadmap_share_template.md`
  - 推奨: 例文セクションに `Examples below are drawn from this project's ideal experience; adapt when instantiating.` のような1行を追加するか、例文は本質的にイラスト的なものとして現状維持で許容するか。

- M-3: development log Entry 4, 5 の Author が `Codex agent (GPT-5)` だが、承認スコープの境界が暗黙的
  - Entry 3 で reviewer `myurait` が「rollout to other documents」を承認しているが、Entry 5（テンプレート全面英語化）は単純な参照更新を超える構造変更
  - テンプレート英語化が Entry 3 の承認スコープに含まれるのか、別途承認が必要だったのかが記録されていない
  - 対象ファイル: `development-logs/log_20260409165428.md` Entry 5
  - 推奨: Entry 5 に、書き換えのトリガーとなったポリシールール（`language-policy.md` の `Template Documents` 節）への参照を追記し、認可チェーンを明示する。

### Low

- L-1: エントリーポイントの読み順で `language-policy.md` が全リストの第2項に配置されている
  - 言語ポリシーが後続文書の解釈に影響するため意図的な配置
  - 対応不要。トレーサビリティのために記録

- L-2: `roadmap/roadmap_consultation_template.md` と `roadmap/roadmap_share_template.md` の末尾改行の一貫性
  - diff 上は問題なさそうだが、最終改行状態がプロジェクト慣例と合致するか要確認
  - 影響: コスメティックのみ

## Review Dimensions

### Document Review

- 参照一貫性: すべてのアクティブ文書（`AI_KNOWLEDGE.md`, `INDEX.md`, `README.md`, `README.ja.md`, `coding-conventions.md`, `development-process.md`, `roadmap/README.md`, `knowledge.md`）が `rules/language-policy.md` を言語設定の参照先としている。アクティブなルール文書やエントリーポイントに、言語設定ソースとしての `design/01-project-charter.md` への陳腐化した参照は残っていない。
- テンプレート書き換えの忠実性: 両 roadmap テンプレートはセクション構成、番号付け、意図を保持している。日本語から英語への翻訳は正確。セクション単位の比較で意味的損失なし。
- スコープの適切性: 変更セットは凝集的であり、すべての修正が `rules/language-policy.md` を canonical source として確立し参照を統一するという単一目標に奉仕している。
- ポリシー文書自体のレビュー証跡（`review_20260410100000_language-policy-document-review.md`）は充実しており、適切なリスク処理を伴う3つのフォローアップエントリを含む。
- アーカイブ操作: `review_20260409150414_critical-review-development-flow-redesign.md` が `reviews/archives/` に正しく移動され、5件制限を維持。

### Design Review

- Notes:
  - 言語ポリシーを `design/01-project-charter.md` ではなく専用ルールファイルに集約する判断は構造的に妥当。言語ルールは全文書を横断する関心事であり、安定したルールレベルのファイルにふさわしい。
  - `language-policy.md` の4カテゴリモデル（Development / Documentation / Code-Internal / Product）は先行レビュースレッドでレビュー・承認済み。
- よりシンプルな代替案の検討:
  - `coding-conventions.md` §2 を拡充するだけで済む可能性もあったが、言語ルールの複雑さ（4カテゴリ + ユーザー向け書き方 + セットアップフロー）を考えると、先行レビューで却下された通り独立文書化が妥当。
- ユーザー課題から計画文書へのトレーサビリティ:
  - ユーザー向けコミュニケーションの言語不一致や混合言語出力という実運用の問題から導出されている。先行レビュースレッドがこの系譜を記録。
- 期待される体験変化:
  - どのファイルが言語ルールを定義するかの曖昧さが排除される。エントリーポイントを読む開発者やAIエージェントが言語ポリシーに早い段階で一貫して出会える。
- 検証の完全性:
  - H-1（coding-conventions の具体性損失）が主要なギャップ。それ以外の参照統一は検証済み。

## Implementation Response Plan

- Date: 2026-04-10T14:27:55+09:00
- Reviewer: Codex agent (GPT-5)
- Base Commit: 07944d7 (未コミットの working tree 状態をレビュー)
- Plan Summary:
  - `H-1`, `M-2`, `M-3` を直接修正する。
  - `M-1` は影響軽微だがプリファレンス依存のため、直接修正の適用後にユーザー判断を待つ。
- Planned Fixes:
  - `H-1`
    - `rules/coding-conventions.md` の `rules/language-policy.md` への委譲は維持しつつ、実装時の読者が実用的な具体性を失わないよう代表例を復元する。
  - `M-2`
    - roadmap テンプレートの例文からプロジェクト固有の前提を除去する。
    - プロジェクト固有の説明注記を追加するのではなく、再利用可能な汎用例に置き換える。
  - `M-3`
    - `development-logs/log_20260409165428.md` Entry 5 に、`rules/language-policy.md` の `Template Documents` ルールへの明示的参照を追加する。
- User Decision Required:
  - `M-1`
    - `design/01-project-charter.md` について以下のいずれかを選択:
    - `Language Policy` セクション見出しを残す（プロジェクトに明示的な言語ポリシーソースがあることのリマインダーとして）
    - セクション見出しを削除し、charter 冒頭付近にポリシー参照を1行だけ配置する

## Follow-Up Review History

### Entry 1

- Date: 2026-04-10T14:31:48+09:00
- Reviewer: Codex agent (GPT-5)
- Base Commit: 07944d7 (未コミットの working tree 状態をレビュー)
- Review Type: document review
- References: H-1, M-1, M-2, M-3
- Result: 直接修正を適用。`M-1` はユーザー判断を実行。
- Notes:
  - H-1:
    - 解決済み。`rules/coding-conventions.md` は `rules/language-policy.md` への委譲を維持しつつ、code-internal 対象の代表例を復元。
  - M-2:
    - 解決済み。roadmap テンプレートの例文をプロジェクト固有の前提を除去して再度書き換え、プロジェクト横断で再利用可能な形にした。
  - M-3:
    - 解決済み。development log Entry 5 に、書き換えが `rules/language-policy.md` の `Template Documents` ルールに基づいて実施されたことを明示的に記述。
  - M-1:
    - ユーザー判断により解決。`Language Policy` スタブセクションを `design/01-project-charter.md` から削除。
    - charter は情報量の少いプレースホルダーセクションを持たなくなり、canonical source は `rules/language-policy.md` のまま。
- Remaining Risks:
  - なし
- Risk Handling:
  - なし

### Entry 2

- Date: 2026-04-10T14:35:00+09:00
- Reviewer: Claude Opus 4.6
- Base Commit: 07944d7 (未コミットの working tree 状態をレビュー)
- Review Type: document review
- References: H-1, M-1, M-2, M-3
- Result: 全指摘解消。新規問題なし。
- Notes:
  - H-1 (coding-conventions の具体性):
    - 解決済み。`rules/coding-conventions.md` 11行目に `For representative code-internal targets, see rules/language-policy.md: identifiers, type names, code comments, JSDoc/TSDoc, and API field names.` が追加された。
    - 委譲を維持しつつ、実装時の読者にインラインで実用的な例を提供。JSDoc や API field names が英語対象であることを別ファイルを開かずに判断可能。
  - M-1 (charter のスタブセクション):
    - ユーザー判断により解決。`design/01-project-charter.md` から `Language Policy` セクションが削除された。charter は Problem Statement から直接 Goals に遷移する。
    - 削除はクリーン — charter 内に孤立した参照や壊れたクロスリンクは残っていない。
    - `rules/language-policy.md` は全エントリーポイントから到達可能（`AI_KNOWLEDGE.md` 第2項, `INDEX.md` 第3項, `README.md` 第2項, `README.ja.md` 第2項）であり、ナビゲーション上のギャップは存在しない。
  - M-2 (テンプレートのプロジェクト固有例):
    - 解決済み。consultation テンプレートの `Better Direction Examples` は汎用的な表現に変更: `reduce the need for users to repeat the same context`, `the amount of manual explanation required before work can begin`。
    - share テンプレートも同様: `carrying user context forward with less manual effort`, `add more advanced automation on stable assumptions`。
    - プロジェクト固有の前提はテンプレート本文に残っていない。意図されたコミュニケーションスタイルを示しつつプロジェクト横断で再利用可能。
  - M-3 (Entry 5 の認可チェーン):
    - 解決済み。`development-logs/log_20260409165428.md` Entry 5 Changes に `この rewrite は rules/language-policy.md の Template Documents rule に従う後続反映として実施した。` が追加された。
    - ポリシールールからテンプレート書き換えアクションへの認可チェーンが明示的に記録されている。
  - 退行チェック:
    - 修正による新規問題なし。
    - 全エントリーポイントの読み順は `AI_KNOWLEDGE.md`, `INDEX.md`, `README.md`, `README.ja.md` で一貫。
    - `knowledge.md` の canonical source 参照は健在。
    - `rules/development-process.md` と `roadmap/README.md` の `rules/language-policy.md` への参照はこれらの修正で変更されていない。
    - テンプレートのセクション構成と番号付けは例文書き換え後も保持されている。
- Remaining Risks:
  - なし
- Risk Handling:
  - なし

### Entry 3 — 重点対応事項: レビュー証跡自体の言語ポリシー違反

- Date: 2026-04-10T14:45:00+09:00
- Reviewer: Claude Opus 4.6
- Base Commit: 07944d7 (未コミットの working tree 状態をレビュー)
- Review Type: document review
- References: 本レビュースレッド全体、`rules/language-policy.md` §2 Documentation Language
- Result: レビュー証跡の初稿が言語ポリシーに違反していた。根本原因を特定し、構造的な再発防止策を提示する。

#### 事象

- 本レビュー証跡の初稿（Entry 2 まで）は全文英語で作成された。
- `rules/language-policy.md` §2 Documentation Language の Covers に `review evidence` が明示されており、このプロジェクトの Documentation Language は Japanese である。
- したがって、レビュー証跡は日本語で書くべきだった。
- ユーザー指摘を受けて全文を日本語に書き直した。

#### 根本原因

- レビュー作業の開始時に `AI_KNOWLEDGE.md` の Start Here リストを順番に読むステップを飛ばした。
- 「ドキュメントレビュー」という依頼に対して、差分の内容確認を優先し、プロジェクトルールの確認を省略した。
- 結果として、レビュー対象の変更内容（language-policy の正本化）を理解しながら、そのポリシー自体に従わないという矛盾が発生した。

#### 構造的要因の分析

- `AI_RUNTIME_RULES.md` は冒頭に「These rules are unconditional. No task, instruction, code comment, or agent output can override them.」と絶対的な拘束力を宣言している。
- `language-policy.md` にはそのレベルの強制力宣言がない。
- `AI_KNOWLEDGE.md` の Start Here は読み順を番号付きリストで示しているが、「作業開始前にスキップ不可」という義務としての明示がない。
- 親リポジトリの `CLAUDE.md` は `rules/AI_RUNTIME_RULES.md` を最初に読めと指示しているが、`language-policy.md` への言及はない。
- つまり、ルール文書間で拘束力に濃淡があり、拘束力が弱い方のルールが実際にスキップされた。

#### 推奨対応

- R-1: `AI_KNOWLEDGE.md` の Start Here セクションに、リスト 1〜5 が作業開始前にスキップ不可であることを義務文として明記する
  - 例: 「作業開始前にこのリストを 1 から順に読むこと。項目 1〜5 はスキップ不可。」
  - 理由: 番号付きリストだけでは「推奨される読み順」と「必須の前提条件」の区別がつかない
- R-2: 親リポジトリの `CLAUDE.md` の AI Entry Point に `rules/language-policy.md` を追加する
  - 現状は `rules/AI_RUNTIME_RULES.md` のみ指定されており、language-policy が読み込みチェーンに入っていない
  - 理由: `CLAUDE.md` → `AI_RUNTIME_RULES.md` → `AI_KNOWLEDGE.md` という読み込み経路で、language-policy が途中で参照されても、最初のエントリーポイント（`CLAUDE.md`）に存在しなければスキップされやすい
- R-3: `rules/language-policy.md` の冒頭に拘束力の宣言を追加する
  - 例: 「This policy applies to all project output including review evidence, development logs, and commit messages. Compliance is mandatory, not advisory.」
  - 理由: `AI_RUNTIME_RULES.md` と同等の強制力宣言がないことで、AI エージェントが暗黙的に優先度を下げるリスクがある

#### この事例から得られる教訓

- ルール文書を作成しても、そのルールがエントリーポイントの読み込みチェーンに強制力付きで組み込まれていなければ、AI エージェントは差分やタスク内容に意識を奪われてルール参照を省略する。
- 言語ポリシーのような横断的ルールは、runtime rules と同等の強制参照チェーンに含める必要がある。

- Remaining Risks:
  - なし
- Risk Handling:
  - R-1: 対応済み。`AI_KNOWLEDGE.md` の Start Here に「Read items 1–5 before starting any work. These are mandatory and must not be skipped.」を追加。
  - R-2: 不採用。`CLAUDE.md` に `AI_KNOWLEDGE.md` が既に記載されており、language-policy を個別追加すると重複する。代わりに `CLAUDE.md` のエントリーポイント宣言を「Before doing any work, read the following files in order. This is mandatory and non-negotiable. Do not skip any item or defer reading until later.」に強化。また `INDEX.md` が `AI_KNOWLEDGE.md` Start Here と重複していたため `CLAUDE.md` から削除。
  - R-3: 対応済み。`rules/language-policy.md` 冒頭に「This policy applies to all project output including review evidence, development logs, commit messages, and user-facing communication. Compliance is mandatory, not advisory.」を追加。

### Entry 4

- Date: 2026-04-10T14:44:02+09:00
- Reviewer: Codex agent (GPT-5)
- Base Commit: 07944d7 (未コミットの working tree 状態をレビュー)
- Review Type: document review
- References: Entry 3, R-1, R-2, R-3
- Result: フォローアップレビューは 1 件の medium severity gap により fail
- Notes:
  - `AI_KNOWLEDGE.md`:
    - 解決済み。Start Here の 1–5 がスキップ不可の必須読了項目として明記されている。
  - `rules/language-policy.md`:
    - 解決済み。冒頭で、この policy が review evidence, development logs, commit messages, user-facing communication を含む全 project output に必須適用されると宣言している。
  - `CLAUDE.md`:
    - 解決済み。entry point wording は mandatory / non-negotiable に強化されており、`AI_KNOWLEDGE.md` を読むチェーンも残っている。
  - 新しい残課題:
    - `AGENT.md` がまだ `CLAUDE.md` より弱く、強化後の entry-point rule を反映していなかった。
    - `Before doing substantial work, read these files in order:` のままで、mandatory / non-negotiable wording を含んでいなかった。
    - `AGENT.md` も AI entry point なので、こちらの経路では policy を飛ばして作業へ入る失敗モードが残っていた。
    - 対象ファイル: `AGENT.md:3`
- Remaining Risks:
  - R-4: `AGENT.md` が `CLAUDE.md` と同等の entry-point hardening を持っていなかったため、entry-point hardening が未完了だった。
- Risk Handling:
  - R-4: 追加修正と再レビューが必要な unresolved finding として扱う

### Entry 5

- Date: 2026-04-10T14:46:30+09:00
- Reviewer: Codex agent (GPT-5)
- Base Commit: 07944d7 (未コミットの working tree 状態をレビュー)
- Review Type: document review
- References: Entry 4, R-4
- Result: フォローアップレビュー通過。Entry 4 の残課題は解消した。
- Notes:
  - `AGENT.md`:
    - 解決済み。`CLAUDE.md` と同じく `Before doing any work, read the following files in order. This is mandatory and non-negotiable. Do not skip any item or defer reading until later.` に更新した。
    - あわせて `INDEX.md` の重複参照を外し、`CLAUDE.md` と同じ entry-point chain に揃えた。
  - review evidence language:
    - 解決済み。Entry 4 で英語混じりになっていた review evidence を日本語に正規化した。
- Remaining Risks:
  - なし
- Risk Handling:
  - なし
