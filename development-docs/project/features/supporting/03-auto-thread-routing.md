# Feature: Auto Thread Routing

## Metadata

- Feature ID: feature-003
- Date: 2026-04-09
- Status: deferred
- Parent Epic: `epic-002`, `epic-003`
- Source: user request on 2026-04-08

## Problem

- 新規チャット開始時に既存文脈との関連を毎回ユーザーが判断すると、会話の入口が管理作業になる。

## Experience Contribution

- Advances: Context Memory and Conversation Continuity

## Why Important

- 「前の続き」が自然に通るかどうかは、ChatLobby の継続会話体験の中心である。

## Scope

- In scope:
  - 類似話題と関連 project 作業の検出
  - 既存 thread への自動接続
  - 誤接続時の correction flow
- Out of scope:
  - memory model 全体の最終実装

## Dependencies

- Required inputs:
  - `epic-002` context memory continuity
  - `epic-003` thread routing and conversation reentry
- Related docs:
  - `features/epics/02-context-memory-continuity.md`
  - `features/epics/03-thread-routing-and-conversation-reentry.md`
  - `design/04-conversation-continuity-foundation.md` (Milestone 1 planning package)

## Decision Inputs

- Open questions:
  - auto-connect する confidence threshold
  - correction flow を chat でどこまで吸収するか

## Roadmap Readiness

- Priority assumption:
  - near
- Expected order:
  - context / memory model と thread / project boundary の整理後
- Blockers:
  - correction flow policy
  - confidence threshold policy
  - Milestone 1 pilot（文書ベース方式）の検証結果。dedicated persistence layer（Feature 012）への移行判断が先に必要になる可能性がある

## Acceptance

- 新規メッセージから有力な既存文脈を自然に引き継げて、誤接続時も短い訂正で別文脈に戻せる。

## Validation Scenarios

- Representative scenarios:
  - `design/00-ideal-experience.md` Scenario 1
  - `design/00-ideal-experience.md` Scenario 2
- Failure signals:
  - 新規会話か継続会話かの確認を毎回ユーザーへ返してしまう
  - 誤接続したあとに会話だけで別文脈へ戻れない

## Promotion Condition

- context / memory model と correction flow の方針が揃った時点で roadmap 候補に昇格する。
