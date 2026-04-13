# Feature: Thread Routing And Conversation Reentry

## Metadata

- Feature ID: epic-003
- Date: 2026-04-09
- Status: candidate
- Source: `development-docs/project/reference/historical-documents/chatlobby-ideal-experience-spec-2026-04-09-v2.md`, `development-docs/project/design/00-ideal-experience.md`, review `development-docs/project/reviews/archives/review_20260409142902_roadmap2-project-insight.md`

## Problem

- 新規会話と継続会話の判定をユーザーに委ねると、会話の入口が管理作業になる。
- 誤った文脈接続から自然に戻せないと、auto-routing が窮屈になる。

## Experience Contribution

- Advances: Context Memory and Conversation Continuity

## Why Important

- 自動 thread routing と correction flow は「前の続き」が自然に通る体験に直結する。

## Scope

- In scope:
  - 類似話題検出
  - 既存 thread / project 接続
  - correction flow
- Out of scope:
  - project memory 全体の永続化

## Dependencies

- Required inputs:
  - context / memory model
- Related docs:
  - `development-docs/project/design/00-ideal-experience.md`

## Decision Inputs

- Open questions:
  - high-confidence auto-connect の閾値
  - low-confidence case の会話補正 UX
- Needed ADRs or design docs:
  - thread-routing-and-project-boundary

## Acceptance

- 誤った thread 接続が起きても、ユーザーの短い訂正で自然に別文脈へ切り替えられる。

## Promotion Condition

- thread ownership と correction flow の設計が揃った時点で roadmap 候補に昇格する。
