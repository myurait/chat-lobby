# Tech Debt Registry

Record temporary compromises so they do not disappear into chat history or commit summaries.

---

### TD-001: adapter 間の task lifecycle / HTTP utility 共通化が途中段階

- Date: 2026-04-05
- Area: services/shared
- Debt: adapter 間で task lifecycle と HTTP utility の共通化が途中段階で、spawn/poll 本体はまだ claude/codex に重複している
- Risk: Phase F で status store を追加する際に adapter 差分管理が煩雑化する
- Planned Fix: Phase F 着手前に `services/shared/` へ task runner 基盤を追加し、claude/codex の差分を command build と parse に限定する
- Owner: team
- Status: open

---

### TD-002: Python pipe の共通 helper 抽出が未着手

- Date: 2026-04-05
- Area: openwebui pipes
- Debt: Python pipe は Open WebUI function が単一ファイル前提のため helper 抽出が未着手
- Risk: 同一ロジック修正時に pipe 間で差分が出やすい
- Planned Fix: Open WebUI function packaging 方針を決め、共通 helper を import 可能な形へ寄せる
- Owner: team
- Status: open

---

### TD-003: adapter / status-store の in-memory 問題

- Date: 2026-04-05
- Area: worker status
- Debt: adapter / status-store ともに in-memory で、再起動を跨ぐ task 継続性と履歴保持がない
- Risk: status panel の可視化は成立しても、restart recovery と長期監査ができない
- Planned Fix: adapter push 型 status store は ADR-015 で固定済み。次は永続 backend または recovery 方針を判断する
- Owner: team
- Status: open

---

### TD-004: 長大な request body のオフロード未設計

- Date: 2026-04-05
- Area: request intake
- Debt: 長大な request body をオフロードする仕組みがなく、サイズ前提も未設計
- Risk: 大きい payload の扱いが場当たり化し、body buffering や prompt 引数長の制約に触れやすい
- Planned Fix: 直接サイズ制限ではなく、large payload offload の方式を Phase F 以降で設計する
- Owner: team
- Status: open

---

### TD-005: prompt の CLI 引数渡しによる OS 引数長制限

- Date: 2026-04-05
- Area: worker invocation
- Debt: prompt を CLI 引数で渡しており、長い prompt では OS 引数長制限に触れる
- Risk: 大きい依頼で task 起動が失敗する
- Planned Fix: 一定閾値以上は stdin pipe に切り替える
- Owner: team
- Status: open

---

### TD-006: claude/codex pipe の同期 polling 問題

- Date: 2026-04-05
- Area: openwebui pipes
- Debt: claude/codex pipe は同期 polling で Open WebUI worker を占有しうる
- Risk: 並列 task 数が増えた際に frontdoor 応答性を下げる
- Planned Fix: dispatch pipe と status panel を主導線にし、direct pipe は async 化方針を検討する
- Owner: team
- Status: open

---

### TD-007: TypeScript service の graceful shutdown 未実装

- Date: 2026-04-05
- Area: lifecycle
- Debt: TypeScript service に graceful shutdown がない
- Risk: 実行中 task が `running` のまま失われる
- Planned Fix: status store 実装時に SIGTERM / SIGINT での終了処理を追加する
- Owner: team
- Status: open

---

### TD-008: tools/openwebui/ と plugins/ の構成整理方針が未確定

- Date: 2026-04-05
- Area: architecture
- Debt: `tools/openwebui/` と目標の `plugins/` 構成の整理方針が未確定
- Risk: plugin 周辺の構成が後続フェーズで肥大化しやすい
- Planned Fix: plugin / tools directory strategy を ADR 化し、長期配置方針を固定する
- Owner: team
- Status: open

---

### TD-009: 前面エージェントの実現方式が未決定

- Date: 2026-04-05
- Area: front agent
- Debt: 初期構想が求める前面エージェントの実現方式が未決定
- Risk: Phase F–G で status / spec loop を積み上げても会話統合責務が曖昧なまま残る
- Planned Fix: front agent 実現方式を ADR で固定する
- Owner: team
- Status: open
