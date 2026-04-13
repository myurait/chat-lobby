# Review

- Date: 2026-04-05
- Scope: Phase E dispatcher (`services/dispatcher`, `chatlobby_dispatch_task`, `routing-policy`)
- Reviewer: Codex
- Review Type: tech lead review
- Criteria:
  - plain text の依頼から Claude / Codex / knowledge を自動選択できるか
  - routing result と reason が frontdoor の会話へ返るか
  - rule source と policy document が同期しているか

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

## Tech Lead Review Dimensions

### Debt Prevention

- Notes:
  - routing rule を `services/dispatcher/rules.json` に切り出したことで、判定ロジックの変更がコード改修と一体化しすぎるのを避けられている。
  - knowledge の file path match fallback を追加したことで、自然文検索の初期 UX を phase 内で最低限担保できている。

### Decomposition and Boundaries

- Notes:
  - Open WebUI pipe は frontdoor 変換と表示に留まり、routing 自体は dispatcher が持つため責務分離が保たれている。
  - rule source、dispatcher、本体 adapters の境界は phase 進行上ちょうどよい粒度で分かれている。

### Alignment With Declared Design

- Notes:
  - upstream Open WebUI 非 fork、TypeScript 主体、adapter / sidecar 境界維持という既存方針に整合している。
  - Phase E の「ユーザーが worker を選ばなくてよい状態を作る」というロードマップ到達目標に一致する。

### Senior-Engineer Smell Detection

- Notes:
  - 現段階では semantic routing や task history 参照はなく、ルールベース実装として意図どおり限定されている。
  - 次フェーズで status 表示を追加する前提として、dispatcher が worker と reason を明示返却している点は妥当である。

## Follow-Up Review

- Date: 2026-04-05
- Result: Pass
- Notes:
  - post-commit の別エージェント review で、Codex adapter の safer default、knowledge query handling、dispatcher error status を追加で見直した。
  - Phase F 着手前の routing 基盤としては十分。status 可視化時に route metadata の再利用性を再確認する。
