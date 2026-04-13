# Feature: Orchestration Visibility And Control

## Metadata

- Feature ID: epic-005
- Date: 2026-04-09
- Status: candidate
- Source: `reference/historical-documents/chatlobby-ideal-experience-spec-2026-04-09-v2.md`, `design/00-ideal-experience.md`

## Problem

- 配下ワーカーの状態を把握したいが、raw event の羅列や手作業の追跡は負担が高い。

## Experience Contribution

- Advances: Orchestration Visibility and Control

## Why Important

- 状態可視化はすでに初期版があるが、前面 AI から「今どうなってる？」へ整理して返す段までは未達である。

## Scope

- In scope:
  - user-visible orchestration summary
  - approval / blockage visibility
  - override entry points
- Out of scope:
  - 常時の raw thinking 主画面表示

## Dependencies

- Required inputs:
  - status model
  - front agent responsibility
- Related docs:
  - `design/00-ideal-experience.md`

## Decision Inputs

- Open questions:
  - summary panel と chat response の責務分担
  - thinking visibility の境界
- Needed ADRs or design docs:
  - orchestration visibility policy

## Acceptance

- ユーザーが自然言語で進捗確認すると、担当、停止理由、承認待ち、次アクションが整理されて返る。

## Promotion Condition

- front agent からの progress synthesis 要件が言語化できた時点で roadmap 候補に昇格する。
