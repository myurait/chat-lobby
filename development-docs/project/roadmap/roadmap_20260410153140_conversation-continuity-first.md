# Roadmap

## Metadata

- Date: 2026-04-10T15:31:40+09:00
- Owner: Codex agent (GPT-5)
- Status: approved
- Source ideal experience:
  - `development-docs/project/design/00-ideal-experience.md`
- Source reviews:
  - `development-docs/project/reviews/archives/review_20260409142902_roadmap2-project-insight.md`
  - `development-docs/project/reviews/archives/review_20260409150414_critical-review-development-flow-redesign.md`
  - `development-docs/project/reviews/archives/review_20260409162349_instruction-coverage-audit-process-redesign.md`
- Source features:
  - `development-docs/project/features/epics/02-context-memory-continuity.md`
  - `development-docs/project/features/epics/03-thread-routing-and-conversation-reentry.md`
  - `development-docs/project/features/epics/04-project-elevation-and-frictionless-bootstrap.md`
  - `development-docs/project/features/epics/01-front-agent-supervision.md`
  - `development-docs/project/features/supporting/03-auto-thread-routing.md`
  - `development-docs/project/features/supporting/04-front-agent-worker-selection.md`

## Goal

- まず「前の会話の続きが自然につながる」体験を前進させ、その次に「どの worker に頼むかを毎回考えなくてよい」体験を前面 AI 側へ引き上げ、最後に「壁打ちから project 化へ自然に進める」体験へ広げる。

## Why This Roadmap Exists Now

- 現在の ChatLobby は、状態確認や知識の正本化は前進しているが、「前の続きが自然につながる」「曖昧な相談から project 骨組みへ自然に進む」「依頼先を前面 AI が吸収する」という理想体験の中核はまだ未達である。
- この中で最初に埋めるべき不足は、「毎回背景を説明し直さなくてよい」ことである。
- ここが弱いまま worker 自動選択や project 化を先に進めると、ユーザーは結局その前段で文脈説明をやり直すことになる。
- したがって、この roadmap は会話継続の自然さを最初に改善し、その次に依頼先吸収を前進させ、最後に project 化へ広げる順番で進める。

## Milestones

### Milestone 1: 前の続きが自然につながる状態へ近づける

- Experience delta:
  - ユーザーが「この前の続き」「前に話していた件」のように曖昧に再開しても、有力な既存文脈が候補化され、誤ってつながっても短い訂正で戻せる。
- Why now:
  - 理想体験の中で最も日常的な不便を減らせる。
  - 後続の project 化や worker 選定も、この前提がないと結局毎回の再説明に依存する。
- In scope:
  - 継続会話と新規会話の境界方針
  - 既存 thread / project 候補の出し方
  - 誤接続時の correction flow
  - 最小の route candidate / correction pilot
  - 必要な design doc / ADR / validation scenario
- Out of scope:
  - memory model 全体の最終実装
  - worker 自動選択の本実装
  - project 化フローの本実装
- Dependencies:
  - `development-docs/project/design/00-ideal-experience.md`
  - `development-docs/project/features/epics/02-context-memory-continuity.md`
  - `development-docs/project/features/epics/03-thread-routing-and-conversation-reentry.md`
  - `development-docs/project/features/supporting/03-auto-thread-routing.md`
- Validation:
  - Scenario 1 と 2 について、「有力候補の提示」と「短い訂正での復帰」を会話シナリオで説明できる。
  - ユーザーが新規会話か継続会話かを毎回明示しなくても前へ進める最小体験が見える。

### Milestone 2: 依頼先を前面 AI が吸収する

- Experience delta:
  - ユーザーが worker 名やモデル名を言わなくても、前面 AI が適切な依頼先を選び、整理された結果を返す。
- Why now:
  - ユーザーが意識する抽象度を一段階上げるには、まず依頼先判断を前面 AI 側へ吸収する完成度を高める必要があるから。
- In scope:
  - front agent による task interpretation
  - worker / model selection の最小方針
  - 結果整理と前面会話への返却
  - 最小の override boundary
- Out of scope:
  - adapter 一般化
  - voice input
  - external provider expansion
- Dependencies:
  - Milestone 1
  - `development-docs/project/features/epics/01-front-agent-supervision.md`
  - `development-docs/project/features/supporting/04-front-agent-worker-selection.md`
- Validation:
  - Scenario 1 と 4 を会話ベースで通せる。
  - ユーザーが依頼先判断を自分でしなくても前に進める。

### Milestone 3: 壁打ちから project 骨組みへ自然に進める

- Experience delta:
  - 曖昧な相談から始めても、ユーザーが文書種別や置き場を先に決めずに project の骨組みへ進める。
- Why now:
  - 会話継続と依頼先吸収の前提ができたあとなら、project 化も前面 AI の自然な延長として扱えるから。
- In scope:
  - project 化の判断条件
  - 初期文書と epic の骨組み提案
  - 元会話との接続維持
  - publish / documentation flow との境界整理
- Out of scope:
  - すべての publish flow の本実装
  - UI polish
- Dependencies:
  - Milestone 1
  - Milestone 2
  - `development-docs/project/features/epics/04-project-elevation-and-frictionless-bootstrap.md`
- Validation:
  - Scenario 3 を会話ベースで通せる。
  - ユーザーが「どの文書を作るか」を先に決めなくても骨組みへ進める。

## Active Cycle Candidate

- Selected task:
  - Milestone 1 の planning package と最小 pilot 定義を作る
- Source milestone:
  - Milestone 1: 前の続きが自然につながる状態へ近づける
- Expected user-visible change:
  - まだ完成した自動接続ではないが、「前の続き」を自然につなぐために何を出し、どう訂正を受けるかが、会話体験として見える形になる。
- Verification evidence:
  - `development-docs/project/design/04-conversation-continuity-foundation.md` — 継続会話境界、候補提示、correction flow の planning package
  - ADR-017 — 文書ベース pilot の構造選択記録
  - design/04 Section 9 — Scenario 1, 2 に対する validation scenario
  - `development-docs/project/features/supporting/03-auto-thread-routing.md` の blocker 状態更新済み

## Deferred Items

- Deferred:
  - worker thinking panel、runtime override、external adapters、MCP surface、voice input
  - Why deferred:
    - 今回の roadmap は会話継続、project 化、front agent という中核体験を先に前進させるため
  - Where tracked:
    - `development-docs/project/features/01-feature-backlog.md`

- Deferred:
  - 公開準備
  - Why deferred:
    - 現時点では他者向け公開より、理想体験の中核を成立させる方が先
  - Where tracked:
    - `development-docs/project/features/01-feature-backlog.md`
