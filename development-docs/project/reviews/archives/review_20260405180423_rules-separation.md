# Review

- Date: 2026-04-05
- Scope: 原則不変の規約文書を `rules/` 配下へ再配置し、参照導線を更新する変更
- Reviewer: Codex
- Review Type: design review
- Criteria:
  - 不変ルール文書が通常更新文書と物理的に分離されているか
  - `rules/` の意味と変更制約が明示されているか
  - エントリポイントと参照導線が破綻していないか

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
  - 規約文書を `rules/` に寄せることで、日常的に更新される設計・判断文書への accidental edit を減らせる。

### Decomposition and Boundaries

- Notes:
  - `rules/` は不変規約、`design/` は設計、`roadmap/` は進行、`decisions.md` は判断記録という境界が明確になった。

### Alignment With Declared Design

- Notes:
  - `knowledge.md` に追加した「rules 配下は通常変更しない」ルールと、実際のディレクトリ構造が一致している。

### Senior-Engineer Smell Detection

- Notes:
  - 将来 `rules/` 配下の文書数が増えた場合は、`rules/README.md` か `INDEX.md` に rule maintenance policy をさらに明示してもよい。

## Follow-Up Review

- Date: 2026-04-05
- Result: Completed.
- Notes:
  - 参照導線は `AGENT.md`, `CLAUDE.md`, `README`, `AI_KNOWLEDGE.md`, `INDEX.md` まで更新されている。
