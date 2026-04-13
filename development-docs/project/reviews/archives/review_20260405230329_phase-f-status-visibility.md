# Review: Phase F Status Visibility

- Date: 2026-04-05T23:03:29+09:00
- Reviewer: Codex agent (GPT-5)
- Base Commit: root `7907e0a` / development-docs `7f2c548`
- Scope: `status-store`, adapter status propagation, `chatlobby_status_panel`, Phase F documentation updates
- Review Type: tech lead review
- Trigger: Phase F 完了判定前の実装レビュー
- Criteria:
  - status store と status panel が frontdoor から使える最小構成であること
  - `approvalState` を含む status model が Claude / Codex / knowledge で破綻なく扱えること
  - 状態伝搬方式が ADR と README / roadmap / architecture に反映されていること

---

## Findings

### Critical

- None

### High

- None

### Medium

- None

### Low

- None

## Review Dimensions

### Tech Lead Review

#### Debt Prevention

- `statusId` と `approvalState` を shared type に切り出してから adapter 側へ配線しており、worker 追加時の再利用性は確保されている。
- `status-store` は in-memory のままなので restart recovery は未対応だが、これは ADR-015 と TD-003 で意図的に後続課題化されている。

#### Decomposition and Boundaries

- adapter は event publish、status store は normalize / merge / query、status panel は read-only 表示に責務分離できている。
- Open WebUI への統合は引き続き custom pipe と sync helper の範囲に留まり、fork / vendoring 方針を崩していない。

#### Alignment With Declared Design

- `approvalState` の正規化、central status store、frontdoor status panel は `design/02-architecture.md` と ADR-015 に整合している。
- README / README.ja / roadmap / development log まで同一方針が反映されている。

#### Senior-Engineer Smell Detection

- `status-store` は `requireTokenForNonLoopbackBind` と bearer token で保護されており、host bind 時の安全性を前提にしている。
- runtime smoke のために `open-webui` を token 付きで再作成したが、この前提は `.env.example` と README に明記されている。

## Implementation Response Plan

- Date: 2026-04-05T23:03:29+09:00
- Reviewer: Codex agent (GPT-5)
- Base Commit: root `7907e0a` / development-docs `7f2c548`
- Plan Summary:
  - Findings なしのため、Phase F 実装をそのまま commit 対象とする。
- Planned Fixes:
  - None.
- Deferred Items:
  - TD-003: status-store 永続化または restart recovery
  - TD-006: direct pipe の同期 polling 縮退
  - TD-009: front agent 実現方式の ADR 化

## Follow-Up Review History

### Entry 1

- Date: 2026-04-05T23:03:29+09:00
- Reviewer: Codex agent (GPT-5)
- Base Commit: root `7907e0a` / development-docs `7f2c548`
- Review Type: tech lead review
- References:
  - `services/shared/status.ts`
  - `services/status-store/src/server.ts`
  - `tools/openwebui/chatlobby_status_panel_pipe.py`
  - `README.md`, `README.ja.md`
  - `development-docs/decisions.md`, `development-docs/design/02-architecture.md`, `development-docs/roadmap/01-initial-roadmap.md`
- Result: Pass
- Notes:
  - `python3 -m unittest tests.test_status_store tests.test_codex_adapter tests.test_knowledge_adapter`, `npm test`, `npm run typecheck` が通過した。
  - Open WebUI に `chatlobby_status_panel` を同期し、`status` の chat completion で `worker`, `state`, `approval`, `step` が返ることを確認した。
- Remaining Risks:
  - status store は in-memory 実装のため、プロセス再起動を跨ぐ履歴保持は行わない。
