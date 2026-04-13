# Feature Backlog

This file is the structured deferred request ledger. Use it to keep non-roadmap items rich enough that later planning does not underestimate them.

## Status

- Purpose: active roadmap の外にある request を、将来の planning input として十分な情報量で保持する
- Rule: この文書の項目は deferred request であり、そのまま implementation-ready ではない
- Rule: `near` の項目だけが `development-docs/project/features/supporting/` へ昇格する候補になる
- Rule: `heavy` または `architectural` な項目は、現在の実装がその将来設計を潰さないよう制約を明記する

## Deferred Request Ledger

### Feature 001: 仕様差し戻しループの tool 化

- Source: old initial roadmap Phase G
- Status: deferred
- Priority Assumption: later
- Expected Order:
  - `epic-006` knowledge elevation loop の方針を先に安定させる
- Blockers:
  - document kind policy
  - AI 主導更新と user confirmation の境界
- Experience Tie:
  - Pillar 5: Knowledge Elevation and Reuse
- Thickness: medium
- Design Impact: cross-cutting
- Current Design Constraint:
  - 現行の document update flow を最終 UX とみなして固定しない
- Supporting Feature: none
- Why Not In Roadmap Yet:
  - 既存の文書更新 loop で当面は成立しており、より中核的な体験設計の前提ではない

### Feature 002: 公開準備

- Source: old initial roadmap Phase H
- Status: deferred
- Priority Assumption: far
- Expected Order:
  - product boundary と deployment target の決定後
- Blockers:
  - 誰に試してもらうかの定義
  - deployment / distribution 方針
- Experience Tie:
  - current canonical ideal experience の外側
- Thickness: medium
- Design Impact: cross-cutting
- Current Design Constraint:
  - 現時点の docs / container 構成を public distribution 前提で固定しない
- Supporting Feature: none
- Why Not In Roadmap Yet:
  - 次フェーズは公開準備を目的にしない

### Feature 003: 類似話題・関連作業への自動スレッド振り分け

- Source: user request on 2026-04-08
- Status: deferred
- Priority Assumption: near
- Expected Order:
  - context / memory model の明確化後に比較候補へ上げる
- Blockers:
  - thread / project boundary
  - correction flow policy
  - confidence threshold policy
- Experience Tie:
  - Pillar 2: Context Memory and Conversation Continuity
- Thickness: heavy
- Design Impact: architectural
- Current Design Constraint:
  - thread / project のデータ境界や routing 前提を、将来の auto-connect と correction flow を無視して固定しない
- Supporting Feature:
  - [03-auto-thread-routing.md](development-docs/project/features/supporting/03-auto-thread-routing.md)
- Why Not In Roadmap Yet:
  - memory model と correction flow の設計がまだ先に必要である

### Feature 004: 前面エージェントによる配下エージェント振り分けと実行モデル選定

- Source: user request on 2026-04-08
- Status: deferred
- Priority Assumption: near
- Expected Order:
  - front agent と dispatcher の責務定義後
- Blockers:
  - front agent responsibility
  - dispatcher boundary
  - model selection policy
- Experience Tie:
  - Pillar 1: Front Agent As Single Entry Point
- Thickness: heavy
- Design Impact: architectural
- Current Design Constraint:
  - 現在の dispatcher や adapter interface を、front agent 不在の最終形として固定しない
- Supporting Feature:
  - [04-front-agent-worker-selection.md](development-docs/project/features/supporting/04-front-agent-worker-selection.md)
- Why Not In Roadmap Yet:
  - front agent の責務境界が未確定であり、先に設計判断が必要

### Feature 005: 配下エージェント thinking の別パネル表示

- Source: user request on 2026-04-08
- Status: deferred
- Priority Assumption: later
- Expected Order:
  - progress synthesis と visibility policy の後
- Blockers:
  - thinking visibility policy
  - summary panel と detailed panel の責務分離
- Experience Tie:
  - Pillar 4: Orchestration Visibility and Control
- Thickness: medium
- Design Impact: cross-cutting
- Current Design Constraint:
  - 現在の status / event surface は、thinking を主画面へ常時露出する前提で固定しない
- Supporting Feature: none
- Why Not In Roadmap Yet:
  - まずは整理済み progress visibility の方が優先される

### Feature 006: Open WebUI スタイルのプロダクト UI 再編

- Source: user request on 2026-04-08
- Status: deferred
- Priority Assumption: later
- Expected Order:
  - frontdoor UX policy と non-fork extension strategy の整理後
- Blockers:
  - upstream non-fork 方針との整合
  - product shell の責務定義
- Experience Tie:
  - Pillar 1: Front Agent As Single Entry Point
  - Pillar 4: Orchestration Visibility and Control
- Thickness: heavy
- Design Impact: cross-cutting
- Current Design Constraint:
  - 現在の Open WebUI 見た目や情報配置を最終プロダクト UI と見なして設計しない
- Supporting Feature: none
- Why Not In Roadmap Yet:
  - 体験の中核動線が先に固まるべきであり、UI 再編はその後の方がやり直しが少ない

### Feature 007: ChatGPT からの会話インポート

- Source: user request on 2026-04-08
- Status: deferred
- Priority Assumption: later
- Expected Order:
  - context / memory model と imported conversation policy の整理後
- Blockers:
  - import format
  - imported thread / project mapping
  - retained memory policy
- Experience Tie:
  - Pillar 2: Context Memory and Conversation Continuity
  - Pillar 5: Knowledge Elevation and Reuse
- Thickness: heavy
- Design Impact: architectural
- Current Design Constraint:
  - conversation storage や thread mapping を、外部会話 import を不可能にする形で固定しない
- Supporting Feature: none
- Why Not In Roadmap Yet:
  - import 仕様と imported conversation の扱いが未確定

### Feature 008: 配下エージェント起動時パラメータ・設定の任意変更

- Source: user request on 2026-04-08
- Status: deferred
- Priority Assumption: later
- Expected Order:
  - 標準実行動作と安全境界が安定した後
- Blockers:
  - execution control policy
  - safe override boundary
- Experience Tie:
  - Pillar 4: Orchestration Visibility and Control
- Thickness: medium
- Design Impact: cross-cutting
- Current Design Constraint:
  - 現在の default runtime を override 不可能な永久仕様として扱わない
- Supporting Feature: none
- Why Not In Roadmap Yet:
  - まず標準動作と承認ポリシーの安定が先

### Feature 009: 外部エージェント接続アダプタの拡充

- Source: user request on 2026-04-08
- Status: deferred
- Priority Assumption: later
- Expected Order:
  - front agent responsibility と adapter contract 整理後
- Blockers:
  - common adapter contract
  - provider capability 差分の扱い
- Experience Tie:
  - Pillar 1: Front Agent As Single Entry Point
- Thickness: heavy
- Design Impact: architectural
- Current Design Constraint:
  - 現行 adapter contract を Claude / Codex 固有前提で固めすぎない
- Supporting Feature: none
- Why Not In Roadmap Yet:
  - 一般化より先に front agent と core flow の設計が必要

### Feature 010: MCP サーバ化

- Source: user request on 2026-04-08
- Status: deferred
- Priority Assumption: later
- Expected Order:
  - capability surface と auth boundary の整理後
- Blockers:
  - 公開 capability 定義
  - 認証と権限の境界
- Experience Tie:
  - Pillar 1: Front Agent As Single Entry Point
  - Pillar 5: Knowledge Elevation and Reuse
- Thickness: heavy
- Design Impact: architectural
- Current Design Constraint:
  - internal API をそのまま外部公開前提で固定しない
- Supporting Feature: none
- Why Not In Roadmap Yet:
  - product boundary の拡張であり、core experience の前提整理より後に扱うべき

### Feature 011: WebUI の音声入力対応

- Source: user request on 2026-04-08
- Status: deferred
- Priority Assumption: far
- Expected Order:
  - product shell と input UX の方針整理後
- Blockers:
  - browser permission flow
  - speech pipeline choice
- Experience Tie:
  - Pillar 1: Front Agent As Single Entry Point
- Thickness: medium
- Design Impact: cross-cutting
- Current Design Constraint:
  - 現在の text-first UI を永続的な唯一入力手段として固定しない
- Supporting Feature: none
- Why Not In Roadmap Yet:
  - core conversation / planning flow の設計前提ではなく、後続の入力拡張である

### Feature 012: 会話継続専用の persistence layer

- Source: Milestone 1 planning で Option B として検討された構造選択肢
- Status: deferred
- Priority Assumption: near
- Expected Order:
  - Milestone 1 pilot（文書ベース軽量方式）の検証結果を受けて判断
- Blockers:
  - Milestone 1 pilot の検証完了
  - retention policy（何をどの粒度で、どれだけの期間保持するか）
  - correction flow と persistent state の関係整理
  - Git 正本との source-of-truth 境界の定義
- Experience Tie:
  - Pillar 2: Context Memory and Conversation Continuity
- Thickness: heavy
- Design Impact: architectural
- Current Design Constraint:
  - Milestone 1 の文書ベース pilot を、dedicated persistence layer の将来追加を不可能にする形で固定しない
  - pilot の candidate extraction interface は、将来 persistence layer が情報源に加わっても差し替え可能な設計にする
- Supporting Feature: none（pilot 完了後の昇格判断時に作成する。pilot 完了前は deferred のまま supporting feature を作成しない）
- Why Not In Roadmap Yet:
  - 現在の Milestone 1 は文書ベースの軽量 pilot として進めている。これは暫定的な出発点であり、最終形ではない。pilot で「自然な再開」と「短い訂正で戻れること」を先に検証し、publish 前の会話文脈の取り扱いが不足と判明した場合にこの feature を昇格する。dedicated persistence layer を入れると、保存単位・retention・Git 正本との境界整理が先に必要になり、体験検証より構造設計が主作業になるため、現段階では deferred としている。
