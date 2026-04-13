# Feature: Front Agent Supervision

## Metadata

- Feature ID: epic-001
- Date: 2026-04-09
- Status: candidate
- Source: `development-docs/project/reference/historical-documents/chatlobby-ideal-experience-spec-2026-04-09-v2.md`, `development-docs/project/design/00-ideal-experience.md`, review `development-docs/project/reviews/archives/review_20260409142902_roadmap2-project-insight.md`

## Problem

- ユーザーがどの AI に何を頼むかを毎回判断しなければならない。
- 配下ワーカーの結果が統合されず、前面会話として整理されない。

## Experience Contribution

- Advances: Front Agent As Single Entry Point

## Why Important

- これは ChatLobby を単なる multi-tool launcher ではなく frontdoor product にする中核責務である。
- これが無いと dispatcher や adapter は存在しても、理想体験の中心は成立しない。

## Scope

- In scope:
  - front agent の責務定義
  - task decomposition と result synthesis
  - dispatcher との差分整理
- Out of scope:
  - 具体的な UI polish
  - 外部エージェント adapter 一般化

## Dependencies

- Required inputs:
  - ideal experience
  - context / memory model
- Related docs:
  - `development-docs/project/design/00-ideal-experience.md`

## Decision Inputs

- Open questions:
  - front agent は model なのか orchestration layer なのか
  - dispatcher を内包するか上位利用するか
- Needed ADRs or design docs:
  - front-agent-supervisor design

## Acceptance

- ユーザーが自然言語で依頼すると、前面 AI が適切な subtask へ分け、整理済みの結果を返す。

## Promotion Condition

- front agent と dispatcher の責務境界が説明可能になった時点で roadmap 候補に昇格する。
