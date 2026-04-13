# Feature: Knowledge Elevation And Document Loop

## Metadata

- Feature ID: epic-006
- Date: 2026-04-09
- Status: candidate
- Source: `development-docs/project/reference/historical-documents/chatlobby-ideal-experience-spec-2026-04-09-v2.md`, `development-docs/project/design/00-ideal-experience.md`

## Problem

- 会話で整理した知識が散逸すると、次の作業に戻せず、同じ議論をやり直すことになる。

## Experience Contribution

- Advances: Knowledge Elevation and Reuse

## Why Important

- publish の仕組みはあるが、前面 AI が何をどの文書へ昇格させるべきかを判断する loop は未整理である。

## Scope

- In scope:
  - spec / ADR / worklog / knowledge への昇格判断
  - 実装後の文書更新候補返却
  - 次回再利用への接続
- Out of scope:
  - 完全自動無人昇格

## Dependencies

- Required inputs:
  - project elevation flow
  - front agent responsibility
- Related docs:
  - `development-docs/project/design/00-ideal-experience.md`

## Decision Inputs

- Open questions:
  - どの昇格判断を AI が主導し、どこで user confirmation を取るか
- Needed ADRs or design docs:
  - knowledge-elevation-loop

## Acceptance

- 会話で確定した内容が適切な文書種別へ戻り、次回以降の作業で自然に再利用される。

## Promotion Condition

- 昇格判断と validation loop の関係が整理できた時点で roadmap 候補に昇格する。
