# Feature: Context Memory Continuity

## Metadata

- Feature ID: epic-002
- Date: 2026-04-09
- Status: candidate
- Source: `reference/historical-documents/chatlobby-ideal-experience-spec-2026-04-09-v2.md`, `design/00-ideal-experience.md`, review `review_20260409142902_roadmap2-project-insight.md`

## Problem

- 過去の会話、project、task、decision が自然に再利用されず、同じ背景説明が繰り返される。

## Experience Contribution

- Advances: Context Memory and Conversation Continuity

## Why Important

- 継続会話の自然さは理想体験の中心であり、これが弱いと ChatLobby は記憶しない会話 UI に留まる。

## Scope

- In scope:
  - 記憶層の定義
  - 関連文脈推定
  - 継続会話の復元
- Out of scope:
  - raw data retention policy の最終実装

## Dependencies

- Required inputs:
  - ideal experience
- Related docs:
  - `design/00-ideal-experience.md`
  - `design/04-conversation-continuity-foundation.md` (Milestone 1 planning package)

## Decision Inputs

- Open questions:
  - 一時記憶、構造化記憶、永続知識の境界
  - 何を memory とし、何を Git 正本へ上げるか
- Needed ADRs or design docs:
  - context-memory-model

## Acceptance

- 「前の続き」と言えば、前面 AI が有力文脈を復元し、未確定点を整理して返せる。

## Promotion Condition

- context / memory model の設計ができ、validation scenario が言語化できた時点で roadmap 候補に昇格する。
