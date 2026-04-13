# Ideal Experience

## 1. Purpose

- この文書は、ChatLobby の中長期計画を体験設計主導で進めるための正規化済み設計入力である。
- roadmap、feature epics、validation ルールは本書の理想体験と experience pillar を起点に導出する。
- 本書が理想体験の canonical source であり、raw input や superseded drafts は `reference/historical-documents/` に保存する。

## 2. Product Definition

- One-sentence definition:
  - ChatLobby は、前面 AI を入口として、会話、記憶、文書、タスク、配下ワーカーを統合し、文脈再説明やツール切替なしに継続開発を進められる self-hosted 開発 frontdoor である。
- Product boundary:
  - 単なる複数 AI 起動基盤ではなく、前面 AI が文脈復元、監督、昇格判断、結果整理を担う体験までを対象とする。

## 3. User and Context

- Primary user:
  - 個人または少人数で複数プロジェクトを並行する開発者
- Working environment:
  - ChatGPT、Claude Code、Codex、ローカルツールを併用しつつ、会話・仕様・コード・タスクが散逸しやすい環境
- Device continuity expectations:
  - スマホとデスクトップをまたぎ、断続的に作業しても同じ会話と文脈を継続できること

## 4. Core Problems

- 会話、仕様、コード、タスク、判断履歴が複数の AI とツールに散逸している。
- どの AI に何を頼むべきかを毎回自分で判断しなければならない。
- 同じ背景や文脈を繰り返し説明し直さなければならない。
- 過去の重要な会話が埋もれ、「あの話」の再開が自然につながらない。
- 壁打ちから project 化へ進むとき、文書種別、配置、命名、テンプレート選択が摩擦になる。
- 新規会話か継続会話かを自分で管理する負担が惜しい。

## 5. Ideal Experience Summary

- ユーザーは基本的に前面 AI とだけ会話すればよい。
- 前面 AI は、会話の継続性、関連文脈、必要な知識、適切な配下ワーカーを自動で判断する。
- 壁打ちから project 昇格までの導線は frictionless で、ユーザーは文書体裁の前準備ではなく設計判断そのものに集中できる。
- 誤った文脈接続が起きても、対話の中で自然に切り直せる。
- 「今どうなってる？」と聞けば、前面 AI が raw event ではなく整理された進行状況を返す。

## 6. Experience Pillars

### Pillar 1: Front Agent As Single Entry Point

- Why it matters:
  - ユーザーに AI や tool の交通整理を押しつけないため
- What is in scope:
  - 前面 AI の会話理解、タスク分解、ワーカー選定、結果統合
- What failure looks like:
  - ユーザーが毎回どの AI を使うか選ばされる

### Pillar 2: Context Memory and Conversation Continuity

- Why it matters:
  - 文脈再説明コストを減らし、過去会話を開発資産として再利用するため
- What is in scope:
  - 継続会話理解、関連 thread / project 推定、記憶層設計、誤接続 correction
- What failure looks like:
  - 「前の続き」が自然につながらず、AI が毎回初見の会話相手に戻る

### Pillar 3: Frictionless Project Elevation

- Why it matters:
  - 壁打ちから project 化へ移るときの documentation ceremony を消すため
- What is in scope:
  - project 昇格判断、骨組み抽出、必要文書や epic の初期提案
- What failure looks like:
  - ユーザーが文書の置き場や体裁を自分で先に設計しないと前へ進めない

### Pillar 4: Orchestration Visibility and Control

- Why it matters:
  - 配下ワーカーが複数動いても、ユーザーが状況把握と必要判断だけに集中できるようにするため
- What is in scope:
  - 状態可視化、承認可視化、必要時の override、整理済み進行報告
- What failure looks like:
  - 状態確認が raw event の閲覧や手作業の追跡になる

### Pillar 5: Knowledge Elevation and Reuse

- Why it matters:
  - 会話の価値を散逸させず、次回以降の作業へ戻せるようにするため
- What is in scope:
  - spec / ADR / worklog / knowledge への昇格判断、正本化、再利用
- What failure looks like:
  - 会話で決まったことが後で参照できず、同じ議論をやり直す

## 7. Representative Scenarios

### Scenario 1: New mobile conversation starts naturally

- Trigger:
  - ユーザーがスマホから新しい相談を始める
- Expected behavior:
  - 前面 AI が関連文脈を集め、必要なら相談を設計タスクへ分解する
- Correction behavior if the system guesses wrong:
  - ユーザーの短い訂正で文脈を再計算し、新しい thread または別 project に切り替える

### Scenario 2: “That previous discussion” is resumed

- Trigger:
  - ユーザーが曖昧参照で過去の話を再開する
- Expected behavior:
  - 前面 AI が有力候補を推定し、既存決定や未確定点を整理して返す
- Correction behavior if the system guesses wrong:
  - 誤った候補を外し、再候補を立て直す

### Scenario 3: Wall-bouncing becomes a project

- Trigger:
  - ユーザーが曖昧な構想から始める
- Expected behavior:
  - 前面 AI が論点、体験課題、必要文書、初期 epic を抽出して project 化の骨組みを作る
- Correction behavior if the system guesses wrong:
  - project 化の境界や文書粒度を会話で補正できる

### Scenario 4: Progress is queried in natural language

- Trigger:
  - ユーザーが「今どうなってる？」と尋ねる
- Expected behavior:
  - 前面 AI が、稼働中タスク、停止理由、承認待ち、次アクションを整理して返す
- Correction behavior if the system guesses wrong:
  - 特定 task や project の指定で文脈を絞れる

## 8. Acceptance Signals

- ユーザーが継続会話で過去文脈を貼り直さずに済む。
- 誤った thread / project 接続から自然に会話で復帰できる。
- 壁打ちから project 化へ進むとき、文書体裁や保存先の迷いが主作業にならない。
- 配下ワーカーの進行状況を自然言語で確認でき、次に何をすればよいかが分かる。
- 会話で確定した知識が後続作業へ再利用される。

## 9. Non-Goals

- 単に複数 AI を並べて手動で使い分けるだけの UI に留まること
- documentation process そのものをユーザーの主作業にすること
- raw thinking や内部 event を常時主画面へ露出すること

## 10. Planning Implications

- Candidate epics:
  - front-agent-supervision
  - context-memory-continuity
  - thread-routing-and-conversation-reentry
  - project-elevation-and-frictionless-bootstrap
  - orchestration-visibility-and-control
  - knowledge-elevation-and-document-loop
- Open design questions:
  - front agent と dispatcher の責務境界
  - context / memory model の記憶層と correction flow
  - project elevation と publish / documentation flow の分離
- Validation constraints:
  - roadmap と cycle task は、体験変化を会話シナリオで検証できなければならない
  - technical correctness だけでなく、ユーザーが何をしなくてよくなったかで判断する
