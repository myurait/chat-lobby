# Review

Use flat bullets and headings. Do not use Markdown tables in review evidence.

- Date: 2026-04-10T10:00:00+09:00
- Reviewer: Claude Opus 4.6
- Base Commit: 07944d7
- Scope: rules/language-policy.md
- Review Type: document review
- Trigger: user request for critical review of language policy proposal as a long-term operational rule
- Criteria:
  - Does the document cause misunderstanding or inconsistency when read standalone?
  - Is the content appropriate as a long-term operational rule?
  - Was the chosen approach justified against simpler alternatives?
  - Did the change add unnecessary complexity or layers?
  - Can the user understand why this change exists and what it enables?

---

## Findings

### Critical

- None

### High

- H-1: user-facing error messages の分類が Code-Internal と Product の間で曖昧
  - §3 Code-Internal Language の Covers に `user-facing error messages` はなく、§4 Product Language の Covers に含まれる
  - しかし現行 coding-conventions.md §2 は「user-facing error messages in logs」を English 対象として明示している
  - language-policy.md の §4 Product Language は「decide it in development planning」としており、未決定期間中にエラーメッセージをどの言語で書くべきか判断できない
  - user-facing error messages は code-internal（ログ向け英語エラー）と product（UI向けエラー）の両方に跨る。この境界が定義されていないため、実装時にルール競合が起きる
  - 推奨: 「code-internal error messages（ログ出力、例外メッセージ）」と「product-facing error messages（ユーザーUI表示）」を明示的に分離し、前者は Code-Internal、後者は Product に帰属させる

- H-2: README ファイルの言語分類が未定義
  - 現行 coding-conventions.md §2 は README を English 対象として明示している
  - language-policy.md は README をどのカテゴリにも明示的に割り当てていない
  - README はプロジェクトルートに置かれる公開ドキュメントであり、Code-Internal でも Documentation Language でもない独自の位置にある
  - chat-lobby の実態では README.md（英語）と README.ja.md（日本語）の並存であり、単一カテゴリでは処理できない
  - 推奨: README の言語ルールを Document Language Rules に明示するか、dedicated な項目を設ける

### Medium

- M-1: canonical source の二重性が解消されていない
  - 「言語を何にするか」の定義は project-charter にある（Development language, Documentation language, Commit message language）
  - language-policy.md も Project Policy セクションで同等の宣言を持つ
  - どちらが canonical か不明。長期運用で片方だけ更新され、もう片方が陳腐化するリスクがある
  - 推奨: policy（ルール、how）はこのファイル、project-specific declaration（what）は charter に一元化し、このファイルの Project Policy セクションは charter への参照ポインタとする旨を明記する

- M-2: 「Stable Rule Documents should be written in English」の enforcement boundary が不明
  - language-policy.md 自身が rules/ 配下にあるが、このファイル自体は English で書かれている
  - しかし rules/development-process.md の Step Details 等には日本語コメントが散見される（対応予定とのこと）
  - 長期運用上、「English で書くべきだが現状は日本語が混在している」状態が暗黙の例外になり、ルールの信頼性が低下する
  - 推奨: 移行期間中の扱いを Exception Handling セクションに 1 行明記する（例: 「Existing Japanese content in rules/ will be migrated to English. Until migration is complete, mixed content is a known exception.」）

- M-3: commit message language の統合が暗黙的すぎる
  - §2 Notes に「dialogue language and commit message language are handled as part of Documentation Language」とあるが、これが Notes に埋もれている
  - commit message は CI、git log、PR で高頻度参照されるため、独立した判断が必要になるプロジェクトが多い
  - 推奨: commit message language を Covers リストの独立行に昇格させ、Notes の統合宣言は「default behavior」として記述する。分離したいプロジェクトはセットアップフローで override できる構造にする

### Low

- L-1: §4 Product Language の Covers に「onboarding text」があるが、chat-lobby は現時点で onboarding UI を持たない
  - テンプレートとしては汎用的で正しいが、プロジェクト固有の instantiation 時に未使用カテゴリが残る
  - 影響は軽微。テンプレート化時にプレースホルダーとして残す形で問題なし

- L-2: Language Policy Setup Flow の Step 5 「Exception Rule」で「who decides them」とあるが、個人プロジェクトでは自明
  - テンプレートとしてはチーム開発を想定した汎用記述として適切

## Review Dimensions

### Document Review

- 4カテゴリ分離（Development / Documentation / Code-Internal / Product）は、従来の coding-conventions.md §2 の暗黙分類を明示化しており、設計意図は適正
- Document Language Rules の「Stable Rule Documents vs Project-Progress Documents」の二分法は長期運用に耐える構造
- Writing Rules セクションはユーザー向けコミュニケーションの品質劣化を防ぐ具体的な指針を提供しており、レビューで繰り返し指摘された問題の制度化として有効
- Language Policy Setup Flow は新規プロジェクトのセットアップ手順として実用的

### Design Review

- Notes:
  - 4カテゴリモデルは言語ポリシーの本質的な軸を捉えており、過剰でも不足でもない
  - ただし error message の Code-Internal / Product 境界（H-1）と README の分類欠落（H-2）は、モデルの隙間であり、実装判断時に混乱を招く
- Simpler alternative considered:
  - coding-conventions.md §2 を拡充するだけで済む可能性もあるが、言語ルールの複雑さ（4カテゴリ + ユーザー向け書き方 + セットアップフロー）を考えると、独立文書化は妥当
- Traceability from user problem to planning document:
  - 言語混在・ユーザー向け説明の品質低下という実運用の問題から導出されている
- Intended experience change:
  - 「どの言語で何を書くべきか」の判断コストが消え、レビューでの言語指摘が減る
- Validation completeness:
  - H-1, H-2 の境界曖昧性が解消されれば、ルールの完全性は高い

## Implementation Response Plan

- Date: 2026-04-10T13:54:56+09:00
- Reviewer: Codex agent (GPT-5)
- Base Commit: 07944d7
- Plan Summary:
  - review 指摘は概ね採用する。ただし `M-2` の「移行中例外を文書化する」は、この policy 文書を一度 completed rule として仕上げ、展開は後続タスクで扱うというユーザー判断により採用しない。
- Planned Fixes:
  - `H-1`
    - `code-internal error messages` と `product-facing error messages` を明示的に分離する。
    - 前者は Code-Internal Language、後者は Product Language に帰属させる。
  - `H-2`
    - README の言語分類を追加する。
    - README は Documentation Language と English を許可し、English 版を必須とする。
  - `M-1`
    - language-policy は policy と分類ルールを定義する文書として扱い、project-specific declaration との関係を明確にする方向で整理する。
    - ただし参照修正や全体展開はこのターンでは行わず、文書単体の完成を優先する。
  - `M-3`
    - commit message summary が Documentation Language に含まれることを、Notes に埋めず明示的なルールとして読める形にする。
  - Additional agreed direction:
    - `Product Language` は複数言語を取りうる前提とし、`Supported Product Languages` という表現へ寄せる。
    - user-facing message template から生成される文面は project-progress side として Documentation Language に従う。
- Deferred Items:
  - `M-2`
    - rules/ 配下の既存日本語混在の移行例外は、この policy 文書には書かない。
    - 理由:
      - ユーザー判断として、この文書を完成品として先に確定し、既存 rules 展開は独立タスクで扱うため。
  - cross-document reference alignment
    - `coding-conventions.md`, `development-process.md`, `project-charter` などへの参照統合は、language-policy 文書の確認後に別タスクで行う。

## Follow-Up Review History

### Entry 1

- Date: 2026-04-10T14:30:00+09:00
- Reviewer: Claude Opus 4.6
- Base Commit: 07944d7 (language-policy.md is untracked; reviewed working tree state)
- Review Type: document review
- References: H-1, H-2, M-1, M-3, Additional agreed direction, Deferred M-2
- Result: findings addressed with minor residual items
- Notes:
  - H-1 (error message 分類):
    - resolved. §3 Code-Internal Language の For Code-Internal Language セクションに「Code-internal error messages, log messages, and exception messages follow Code-Internal Language」を追加。§4 側に For Product Language セクションを新設し「Product-facing error messages follow Supported Product Languages」を明記。境界が明確になった。
  - H-2 (README 分類):
    - resolved. Document Language Rules に README Documents サブセクションを新設。English 版必須、Documentation Language 版は追加、と明記。chat-lobby の README.md / README.ja.md 並存実態と整合する。
  - M-1 (canonical source 二重性):
    - partially addressed. Project Policy セクションに project-specific declaration を残す形。Implementation Response Plan では「policy と declaration の関係を明確にする方向で整理」「参照修正は別タスク」としており、文書単体としては policy 側に宣言が残る構造。ただし Notes セクションに「project-specific values come from design/01-project-charter.md」等の参照ポインタが追加されておらず、二重性は厳密には未解消。cross-document reference alignment が deferred item として明示されているため、現時点では許容。
  - M-3 (commit message language):
    - resolved. §2 Covers リストに `commit message summaries` が独立行として存在。Notes の「handled as part of Documentation Language」も残っており、デフォルト統合かつ分離可能な構造になった。
  - Additional agreed direction (Product Language → Supported Product Languages):
    - resolved. §4 見出しは「Product Language」のまま（カテゴリ名としては妥当）だが、Project Policy では「Supported Product Languages: English / Japanese」に変更済み。Setup Flow Step 4 も「what supported product languages the product provides」に更新。§4 Notes の「when not yet fixed」文は削除されており、Product Language 未決定状態の扱いが不明になった点は軽微な退行だが、Setup Flow で担保されているため許容。
  - Additional agreed direction (user-facing message template):
    - not explicitly addressed in document text. Implementation Response Plan では「user-facing message template から生成される文面は Documentation Language に従う」とあるが、この規則が document 本文に反映された箇所が見当たらない。project-progress template から生成されるメッセージ（roadmap share messages 等）は §2 Covers に含まれるため暗黙的にはカバーされるが、template-generated text の明示的な言及はない。
  - M-2 (移行期間例外):
    - deferred as planned. ユーザー判断として文書単体の完成を優先し、既存 rules/ の日本語混在は独立タスクで対応。妥当。
- Remaining Risks:
  - R-1: M-1 の canonical source 二重性が文書内に残存。Project Policy セクションに charter への参照ポインタがない。
  - R-2: template-generated user-facing text が Documentation Language に従うことの明示的規則が欠落。
  - R-3: §4 Product Language Notes から「when not yet fixed」の扱いが消えたことで、Product Language 未決定時の暫定ルールが不在。
- Risk Handling:
  - R-1: deferred planned work with tracked destination document or phase — cross-document reference alignment タスクで対処予定
  - R-2: accepted residual risk with monitoring or next-review trigger — §2 Covers の roadmap consultation/share messages で暗黙カバー。template-generated text が増えた時点で明示規則を追加
  - R-3: accepted residual risk with monitoring or next-review trigger — Setup Flow Step 4 が Product Language 決定を義務化しているため、未決定状態は原理的に短期間。長期化した場合に再レビュー

### Entry 2

- Date: 2026-04-10T14:03:45+09:00
- Reviewer: Codex agent (GPT-5)
- Base Commit: 07944d7 (language-policy.md is untracked; reviewed working tree state)
- Review Type: document review
- References: R-1, R-2, R-3
- Result: policy-level risks addressed; rollout alignment remains deferred work
- Notes:
  - R-1 (canonical source duality):
    - resolved in policy direction. `language-policy.md` now declares itself as the authoritative source for both project-specific language decisions and language-domain rules.
    - This closes the ambiguity inside the policy document itself.
    - Remaining work is no longer "which file is canonical" but "which other documents must be updated to reference this policy".
  - R-2 (template-generated user-facing text):
    - resolved. `For User-Facing Communication` now explicitly states that user-facing messages generated from project templates follow Documentation Language.
    - This removes the need to infer the rule only from the project-progress document examples.
  - R-3 (Product Language undecided):
    - resolved. `Supported Product Languages: English / Japanese` is now defined in the project policy block.
- Remaining Risks:
  - R-4: cross-document alignment is still pending.
    - `design/01-project-charter.md` and other rule documents still restate language values independently.
    - Until they are updated to point at `rules/language-policy.md`, the repository still has duplicated declarations even though the canonical source has been chosen.
- Risk Handling:
  - R-4: deferred planned work with tracked destination document or phase — after policy approval, propagate references so other documents point to `rules/language-policy.md` instead of redefining language settings

### Entry 3

- Date: 2026-04-10T14:07:47+09:00
- Reviewer: myurait
- Base Commit: 07944d7 (language-policy.md is untracked; reviewed working tree state)
- Review Type: document review
- References: Entry 2, R-4
- Result: follow-up review passed; approved for rollout to other documents
- Notes:
  - The direction to make `rules/language-policy.md` the canonical source is accepted.
  - The additional explicit rule for template-generated user-facing text is accepted.
  - The next required action is retrospective rollout: other active documents should reference this policy instead of restating language settings.
- Remaining Risks:
  - None in the policy document itself.
- Risk Handling:
  - None
