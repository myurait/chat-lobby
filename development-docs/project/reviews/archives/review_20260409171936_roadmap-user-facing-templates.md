# Review: Roadmap User Facing Templates

- Date: 2026-04-09T17:19:36+09:00
- Reviewer: Codex agent (GPT-5)
- Base Commit: development-docs `2828cae`
- Scope: roadmap consultation/share template を user-facing communication template として再設計した変更。対象は `roadmap/roadmap_consultation_template.md`、`roadmap/roadmap_share_template.md`、`roadmap/README.md`、`rules/development-process.md` である。
- Review Type: document review
- Trigger: ユーザー指摘により、roadmap template が内部用語前提で user-facing quality を満たしていないと判明したため
- Criteria:
  - template がそのままユーザーに送る文章の型として使えるか
  - 文書名や内部識別子より先に user meaning が来る構造になっているか
  - Documentation language と ideal experience language に従う拘束が明記されているか

---

## Findings

### Critical

- None

### High

- None

### Medium

- None

### Low

- None

## Review Dimensions

### Document Review

- 相談 template と共有 template の両方で、internal jargon を前提にしないこと、`design/01-project-charter.md` の Documentation language に従うこと、`design/00-ideal-experience.md` の表現を優先することが明記された。
- 悪い例と良い例の方向が追加され、template 使用者が user-facing failure mode を避けやすくなった。
- `roadmap/README.md` と `rules/development-process.md` にも、roadmap consultation/share が direct user communication であることを戻したため、template 単体に依存しない運用になった。

## Implementation Response Plan

- Date: 2026-04-09T17:19:36+09:00
- Reviewer: Codex agent (GPT-5)
- Base Commit: development-docs `2828cae`
- Plan Summary:
  - review findings は無く、追加修正は不要である。
- Planned Fixes:
  - None
- Deferred Items:
  - 実際の roadmap consultation/share の運用で文体や粒度の補正が必要なら、その時点で再度改善する。
