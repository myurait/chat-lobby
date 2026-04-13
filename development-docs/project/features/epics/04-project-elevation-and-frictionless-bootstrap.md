# Feature: Project Elevation And Frictionless Bootstrap

## Metadata

- Feature ID: epic-004
- Date: 2026-04-09
- Status: candidate
- Source: `development-docs/project/reference/historical-documents/chatlobby-ideal-experience-spec-2026-04-09-v2.md`, `development-docs/project/design/00-ideal-experience.md`, review `development-docs/project/reviews/archives/review_20260409142902_roadmap2-project-insight.md`

## Problem

- 壁打ちを project に育てる前に、文書体裁、置き場、命名、テンプレート選択が摩擦になる。

## Experience Contribution

- Advances: Frictionless Project Elevation

## Why Important

- これは documentation correctness ではなく、ユーザーを本質的な設計判断へ早く入れるための体験要件である。

## Scope

- In scope:
  - wall-bounce から project 化への判断
  - 初期文書と epic の骨組み抽出
  - 元会話との接続維持
- Out of scope:
  - すべての publish flow 実装詳細

## Dependencies

- Required inputs:
  - ideal experience
  - feature and roadmap planning rules
- Related docs:
  - `development-docs/project/design/00-ideal-experience.md`

## Decision Inputs

- Open questions:
  - project 化の閾値
  - ユーザーに露出しない生成物の範囲
- Needed ADRs or design docs:
  - project-elevation-flow

## Acceptance

- 曖昧な相談から始めても、ユーザーが文書種別を先に選ばずに project 骨組みへ進める。

## Promotion Condition

- project elevation flow と publish / documentation flow の分離が設計できた時点で roadmap 候補に昇格する。
