# Review: Roadmap Active Archive Structure

- Date: 2026-04-09T16:45:28+09:00
- Reviewer: Codex agent (GPT-5)
- Base Commit: development-docs `ae832b0`
- Scope: roadmap の active / archive 構造を、現在の planning process と導線文書へ反映する変更。対象は `roadmap/README.md`、`roadmap/roadmap_template.md`、`rules/development-process.md`、`INDEX.md`、`AI_KNOWLEDGE.md`、`README.md`、`README.ja.md`、`roadmap/archives/` である。
- Review Type: document review
- Trigger: ユーザー要求による roadmap active/archive rule の追加
- Criteria:
  - 現在対応中の roadmap が一目で分かる構造になっているか
  - active roadmap と archived roadmap の責務が混ざらないか
  - 命名規則と配置規則が template と導線文書まで一貫しているか

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

- `roadmap/` 直下は active roadmap 1 本だけ、旧 roadmap は `roadmap/archives/` へ送る rule になり、本文を開かなくても current / historical を判別できるようになった。
- roadmap 命名規則は `roadmap_{YYYYMMDDhhmmss}_{scope}.md` に統一され、template でも同じ rule を見えるようにした。
- 旧 [roadmap_20260405174901_initial-roadmap.md](/Users/fox4foofighter/dev/chat-lobby/development-docs/roadmap/archives/roadmap_20260405174901_initial-roadmap.md) は archive 側へ移り、現在 `roadmap/` root に active roadmap が無いことも明確になった。
- `INDEX.md`、`AI_KNOWLEDGE.md`、README 群の reading order も「roadmap 直下の active 1 本」に揃っており、運用導線は一貫している。

## Implementation Response Plan

- Date: 2026-04-09T16:45:28+09:00
- Reviewer: Codex agent (GPT-5)
- Base Commit: development-docs `ae832b0`
- Plan Summary:
  - review findings は無く、追加修正は不要である。
- Planned Fixes:
  - None
- Deferred Items:
  - roadmap2 作成時に、この新しい active roadmap rule を最初に適用する。
