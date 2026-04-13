# Tech Debt Registry

Record temporary compromises so they do not disappear into chat history or commit summaries.

| ID | Date | Area | Debt | Risk | Planned Fix | Owner | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| TD-001 | 2026-04-05 | services/shared | adapter 間で task lifecycle と HTTP utility の共通化が途中段階で、spawn/poll 本体はまだ claude/codex に重複している | Phase F で status store を追加する際に adapter 差分管理が煩雑化する | Phase F 着手前に `services/shared/` へ task runner 基盤を追加し、claude/codex の差分を command build と parse に限定する | team | open |
| TD-002 | 2026-04-05 | openwebui pipes | Python pipe は Open WebUI function が単一ファイル前提のため helper 抽出が未着手 | 同一ロジック修正時に pipe 間で差分が出やすい | Open WebUI function packaging 方針を決め、共通 helper を import 可能な形へ寄せる | team | open |
| TD-003 | 2026-04-05 | worker status | adapter / status-store ともに in-memory で、再起動を跨ぐ task 継続性と履歴保持がない | status panel の可視化は成立しても、restart recovery と長期監査ができない | adapter push 型 status store は ADR-015 で固定済み。次は永続 backend または recovery 方針を判断する | team | open |
| TD-004 | 2026-04-05 | request intake | 長大な request body をオフロードする仕組みがなく、サイズ前提も未設計 | 大きい payload の扱いが場当たり化し、body buffering や prompt 引数長の制約に触れやすい | 直接サイズ制限ではなく、large payload offload の方式を Phase F 以降で設計する | team | open |
| TD-005 | 2026-04-05 | worker invocation | prompt を CLI 引数で渡しており、長い prompt では OS 引数長制限に触れる | 大きい依頼で task 起動が失敗する | 一定閾値以上は stdin pipe に切り替える | team | open |
| TD-006 | 2026-04-05 | openwebui pipes | claude/codex pipe は同期 polling で Open WebUI worker を占有しうる | 並列 task 数が増えた際に frontdoor 応答性を下げる | dispatch pipe と status panel を主導線にし、direct pipe は async 化方針を検討する | team | open |
| TD-007 | 2026-04-05 | lifecycle | TypeScript service に graceful shutdown がない | 実行中 task が `running` のまま失われる | status store 実装時に SIGTERM / SIGINT での終了処理を追加する | team | open |
| TD-008 | 2026-04-05 | architecture | `tools/openwebui/` と目標の `plugins/` 構成の整理方針が未確定 | plugin 周辺の構成が後続フェーズで肥大化しやすい | plugin / tools directory strategy を ADR 化し、長期配置方針を固定する | team | open |
| TD-009 | 2026-04-05 | front agent | 初期構想が求める前面エージェントの実現方式が未決定 | Phase F–G で status / spec loop を積み上げても会話統合責務が曖昧なまま残る | front agent 実現方式を ADR で固定する | team | open |
