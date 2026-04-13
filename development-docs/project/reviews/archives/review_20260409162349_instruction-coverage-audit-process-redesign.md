# Review: Instruction Coverage Audit Process Redesign

- Date: 2026-04-09T16:23:49+09:00
- Reviewer: Codex agent (GPT-5)
- Base Commit: development-docs `aa2ac94`
- Scope: 2026-04-09 の「理想体験正本ドキュメントの配置と開発フロー指摘」以降にユーザーが出した要求群について、要求棚卸しと遂行状況を監査する。対象は `rules/development-process.md`、`requirements/`、`design/00-ideal-experience.md`、`features/`、`reference/historical-documents/`、関連 review / log である。
- Review Type: document review
- Trigger: ユーザー要求による instruction coverage audit
- Criteria:
  - 今日の要求が漏れなく洗い出されているか
  - 各要求が意図どおりのレベルまで遂行されているか
  - 規約とテンプレートが次回運用でも同じ意図を保てるか
  - 途中で追加された批判的レビュー、説明責任、意思決定 escalation の要求が process に反映されているか

---

## Findings

### Critical

- None

### High

- None

### Medium

- [M1] 理想体験の正本を `design/00-ideal-experience.md` に固定する rule は入ったが、その rule が理想体験 template 自体には埋め込まれていない。次回 requirement discovery で別名の ideal experience 文書を新設してしまう余地が残る。
  - `rules/development-process.md:131-154` は canonical source を `design/00-ideal-experience.md` に固定している。
  - しかし `requirements/ideal-experience-spec-template.md:3-60` は canonical path や archive 元入力との関係を明示していない。
  - 今回の要求には「理想体験の正本の取り扱いを定義する」が含まれていたため、運用ルールだけでなく template 側でも同じ拘束が見える方が再発防止としては強い。

### Low

- None

## Review Dimensions

### Document Review

- 洗い出した対象要求は次の 12 項目である。
- 1. `chatlobby-roadmap2-project-insight-review-2026-04-09-v2` を review evidence として正規配置する。
- 2. 理想体験文書は process 整理が終わるまで `development-docs/` root に置く。
- 3. ideal experience が開発初期に必須であり、不在時は requirement discovery interview を mandatory にする。
- 4. requirement discovery の interview 項目、ルール、template を追加する。
- 5. ideal experience -> feature -> roadmap -> cycle task -> validation の planning chain を process に入れる。
- 6. 現行開発サイクルの問題点を再度洗い出し、`review_20260409142902_roadmap2-project-insight.md` に follow-up として反映する。
- 7. process 改善と hierarchy 設計が終わったら、整理してユーザーへ共有する。
- 8. review rule を「必ず批判的にレビューする」前提へ強化し、複雑化と説明責任も review 観点へ入れる。
- 9. その新ルールに従って、今回の flow redesign 自体を再レビューする。
- 10. preference-sensitive な構造判断は、メリット・デメリット・影響範囲を添えて user decision を取る process rule にする。
- 11. 理想体験の canonical source と historical document の正式な archive rule を定義する。
- 12. `supporting/` は近い roadmap 候補だけに限定し、deferred item は rich backlog として priority, order, blockers, experience tie, thickness, design impact, current design constraint を必須化し、template も用意する。
- 上記のうち 1, 3, 4, 5, 6, 8, 9, 10, 11, 12 は現物で実行済みである。
- 2 は一時措置として守られ、その後 process 整理完了後に `design/00-ideal-experience.md` へ正規移管されたため、意図どおりに完了している。
- 7 もユーザー向け説明として実施済みであり、関連 review と log にも痕跡が残っている。
- 監査対象の中で、意図未達と判定したのは `M1` のみである。これは成果物の欠落ではなく、template への rule 埋め込み不足であり、運用再発防止の観点で詰めが甘い。
- 総評として、今日の要求群は概ね意図どおり遂行されている。特に `design/00-ideal-experience.md` の canonical 化、historical archive index、planning chain、critical review rule、rich backlog への移行は要求と整合している。

## Implementation Response Plan

- Date: 2026-04-09T16:23:49+09:00
- Reviewer: Codex agent (GPT-5)
- Base Commit: development-docs `aa2ac94`
- Plan Summary:
  - 今回の instruction coverage audit で見つかった不足は template への canonical rule 埋め込みである。次回修正では `requirements/ideal-experience-spec-template.md` に canonical output path と historical source handling を追記する。
- Planned Fixes:
  - `requirements/ideal-experience-spec-template.md` に、正規出力先が `design/00-ideal-experience.md` であることを明記する。
  - historical input を normalize した後は `reference/historical-documents/` へ archive する導線を template に書く。
- Deferred Items:
  - roadmap2 sequencing の実作業

## Follow-Up Review History

### Entry 1

- Date: 2026-04-09T16:32:23+09:00
- Reviewer: Codex agent (GPT-5)
- Base Commit: development-docs `aa2ac94`
- Review Type: document review
- References:
  - Planned fix: ideal experience template canonical output path
  - Planned fix: historical input archive handling in template
  - `requirements/ideal-experience-spec-template.md`
  - `rules/development-process.md`
- Result: Pass
- Notes:
  - `requirements/ideal-experience-spec-template.md` に canonical output path と historical source handling が追記され、監査で残っていた未遂項目は解消された。
  - これにより、ideal experience の正本運用は process rule だけでなく template でも拘束されるようになった。
- Remaining Risks:
  - None
- Risk Handling:
  - None
