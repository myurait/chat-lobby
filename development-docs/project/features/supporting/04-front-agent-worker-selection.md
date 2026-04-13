# Feature: Front Agent Worker Selection

## Metadata

- Feature ID: feature-004
- Date: 2026-04-09
- Status: deferred
- Parent Epic: `epic-001`
- Source: user request on 2026-04-08

## Problem

- 現在は routing があっても、前面 AI が会話理解、worker 選定、実行モデル選定を統合する責務が未定義である。

## Experience Contribution

- Advances: Front Agent As Single Entry Point

## Why Important

- front agent が無いと、複数 worker が存在しても product としては分散した操作面に留まる。

## Scope

- In scope:
  - front agent による作業振り分け
  - 実行モデル選定
  - dispatcher との責務境界整理
- Out of scope:
  - adapter 一般化

## Dependencies

- Required inputs:
  - `epic-001` front agent supervision
- Related docs:
  - `development-docs/project/features/epics/01-front-agent-supervision.md`

## Decision Inputs

- Open questions:
  - routing と planning を同じ front agent が担うか
  - 実行モデル選定をどの粒度で user override 可能にするか

## Roadmap Readiness

- Priority assumption:
  - near
- Expected order:
  - front agent responsibility と dispatcher boundary の整理後
- Blockers:
  - model selection policy
  - front agent / dispatcher boundary

## Acceptance

- ユーザーが worker 名を意識せず依頼しても、前面 AI が適切な作業先と実行モデルを選んで結果を整理できる。

## Validation Scenarios

- Representative scenarios:
  - `development-docs/project/design/00-ideal-experience.md` Scenario 1
  - `development-docs/project/design/00-ideal-experience.md` Scenario 4
- Failure signals:
  - ユーザーがどの worker を使うべきか自分で判断しないと前に進めない
  - worker 実行結果が前面会話として整理されず、生の作業ログの寄せ集めになる

## Promotion Condition

- front agent と dispatcher の責務境界、および model selection policy が説明可能になった時点で roadmap 候補に昇格する。
