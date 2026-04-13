# Project Knowledge

This file stores reusable lessons that should survive beyond a single task or phase.
Detailed chronology belongs in `development-logs/`.

## 1. Greenfield Workflow

1. Write the project charter before writing code.
2. Read real reference implementations instead of summaries when they exist.
3. Create the roadmap before choosing tools and frameworks in detail.
4. Stabilize the foundation early: README, `.gitignore`, documentation, and test policy.
5. Make test isolation a first-class design requirement.
6. Cross-check the roadmap against reference implementations. Identify gaps and excess.
7. Do not accumulate test debt. Refactor untestable code immediately.
8. Pre-place test stubs for future phases.
9. Keep design documents in sync with the implementation. Add numbered design documents as the project evolves.
10. Start each cycle by confirming the roadmap; end each cycle by updating it.

## 2. Documentation Discipline

- `INDEX.md` is the development documentation entry point.
- Design documents should evolve in visible project documents, not only in chat history.
- General lessons belong here.
- Detailed work history belongs in `development-logs/`.
- Architecture documents (02) should provide an overview only. Delegate details to dedicated documents (single source of truth).
- Documents must be split at an appropriate granularity. When a document starts accumulating multiple concerns or grows enough to slow understanding, create or update dedicated documents instead of continuing to append.
- Existing documents must not be allowed to bloat through incremental append-only updates. Preserve readability by moving stable subsections into focused documents and keeping overview documents concise.
- Principle-stable rule documents belong under `rules/`. Unless the user explicitly asks for a rule change, treat documents in `rules/` as non-editable during ordinary implementation work.
- `rules/language-policy.md` is the canonical source for project-specific language settings and language-domain boundaries.
- Do not create or revise roadmaps without a trustworthy canonical ideal experience document. If one is missing or weak, run requirement discovery first.
- `design/00-ideal-experience.md` is the canonical planning source for the ideal experience. Historical inputs belong under `reference/historical-documents/`, never as parallel active sources.
- Do not let raw request ledgers drive planning directly.
- Use `features/supporting/` only for roadmap-adjacent candidates.
- Keep distant deferred requests in the backlog, but require them to record priority, order, blockers, experience tie, thickness, design impact, and current design constraints.
- If a deferred backlog item is heavy or architectural, reflect its constraint in the active design documents before locking adjacent implementation.
- Update the tech debt registry at the end of each phase.
- Development logs use `development-logs/log_{YYYYMMDDhhmmss}.md` for the active file and `development-logs/archives/` for closed files.
- Keep at most 20 entries in one development log file. If the next append would exceed 20 entries, move the current file to `development-logs/archives/` and create a new active file in `development-logs/`.
- Review evidence uses `reviews/review_{YYYYMMDDhhmmss}_{scope_description}.md`, where `scope_description` is a concise kebab-case scope label.
- Keep only the newest 5 review evidence files in `reviews/`. Move older evidence files to `reviews/archives/`.
- When the user decides a requested capability is outside the current roadmap, move it into a dedicated feature backlog document instead of leaving it as a pending roadmap phase.
- A roadmap item is not ready unless it explains the intended user-visible change and how that change will be validated.

## 3. Review Discipline

- Review findings need durable evidence, not only chat output.
- Re-review every meaningful fix, especially when the original issue was architectural.
- A passing test suite does not prove the user workflow is correct.
- Undocumented exceptions are treated as process failures, not harmless shortcuts.
- Code review alone cannot detect user-experience problems. Explicitly incorporate end-user perspective testing into the process.
- Review evidence should avoid Markdown tables. Use headings and flat bullet lists so AI readers can parse findings reliably.

## 4. Architecture Lessons

- Reference implementations carry implicit constraints. When adopting one, explicitly verify its design assumptions.
- Problems surfaced by tests are system problems, not test-design problems. Recognize architectural defects rather than patching tests.
- When applying a band-aid fix, record a root-cause fix plan in the tech debt registry. Never stop at the band-aid alone.

## 5. Security Lessons

- Prevent injection in structured data (YAML, JSON, SQL) by using safe serialization functions, not string interpolation.
- Prevent command injection by validating external input against a whitelist before passing it to shell commands.
- Never use pipe-to-shell patterns (`curl | bash`) in project scripts. Show the commands and let the user run them manually.
- For Open WebUI bootstrap settings, remember that `PersistentConfig` values survive restarts via the application database. Document the reset path for first-run security settings instead of assuming env changes will always apply.

## 6. AI Agent Communication Lessons

- 「ルールを読んで検査に使え」と「ルールに従って自分の出力も書け」は別の指示である。出力言語、出力フォーマット、出力対象の制約は、ロール定義内で明示的に指定しない限り適用されない。
- テンプレートの Bad Directions に実際の失敗例を入れる場合、テンプレート自体の言語ルール（例: English）に従い、失敗例も同じ言語に翻訳して記載する。
- AI の意思決定エスカレーションは「止まって聞く」と「勝手に進める」の二択ではない。推奨が明確なら「進めつつ事後通知する」という中間を設計できる。
- ユーザー向け相談メッセージに AI 自身の作業進捗報告を混ぜると、相談の本題が埋もれる。作業報告と意思決定相談は分離すること。
