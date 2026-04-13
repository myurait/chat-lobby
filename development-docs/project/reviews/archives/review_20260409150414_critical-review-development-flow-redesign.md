# Review: Critical Review Development Flow Redesign

- Date: 2026-04-09T15:04:14+09:00
- Reviewer: Codex agent (GPT-5)
- Base Commit: development-docs `19d901b`
- Scope: `19d901b` で入った planning / requirement discovery / ideal experience / feature hierarchy の再設計。対象は `rules/development-process.md`, `design/00-ideal-experience.md`, `features/00-feature-index.md`, `features/supporting/`, `features/01-feature-backlog.md`, `INDEX.md`, `AI_KNOWLEDGE.md`。
- Review Type: tech lead review
- Trigger: ユーザー要求による批判的レビューの再実施
- Criteria:
  - chosen approach は simpler alternative と比較して正当化されているか
  - planning layer の追加が user value に見合うか
  - canonical source と責務境界が曖昧になっていないか
  - ユーザーに対して「なぜこの層が必要か」を説明できるか

---

## Findings

### Critical

- None

### High

- [H1] raw request を一律に supporting feature 化したことで、roadmap2 の優先順位づけ前に文書階層を作り込みすぎている。これは planning を前に進めるというより、deferred 項目の保守負荷を先に増やしている。
  - `rules/development-process.md:124-137` は feature backlog から supporting feature への正規化を強く促しているが、どの request まで正規化すべきかの停止条件がない。
  - `features/00-feature-index.md:22-39` では deferred request 11 件が supporting feature 群として展開され、`features/01-feature-backlog.md:11-110` に同じ request ledger も残っている。
  - この構成だと、roadmap に上げないと決めた項目まで planning-ready 文書として管理対象になり、説明責任と更新負荷が増える。

- [H2] 新しい supporting feature 層は、自身のルールをすでに破っている。層の意味が安定していない。
  - `features/supporting/README.md:3-10` では、supporting feature は epic の下にあり、少なくとも 1 つの parent epic を持つと定義している。
  - しかし `features/supporting/02-public-readiness.md:5-18` は `Parent Epic: none` であり、しかも current ideal experience baseline の外にある item を同じ層に置いている。
  - これは supporting feature 層が「epic を具体化する層」なのか、「roadmap 外 request の受け皿」なのか、定義が揺れていることを示す。

- [H3] active ideal experience input と normalized ideal experience doc の権威関係が曖昧で、planning の正本が衝突しうる。
  - `INDEX.md:12-15` と `AI_KNOWLEDGE.md:10-13` は root の active ideal experience input を先に読ませ、その後に `design/00-ideal-experience.md` を読む導線にしている。
  - 一方で `design/00-ideal-experience.md:5-6` は、自身を roadmap と feature epics の起点になる正規化済み設計入力としている。
  - 両者に差分や矛盾が出たとき、どちらが勝つかの rule が無い。この状態で roadmap planning を始めると、AI と人間で参照元が割れる。

### Medium

- [M1] feature-level acceptance がまだ抽象的で、roadmap 選定や検証に十分な disconfirming check を持っていない。
  - `features/supporting/03-auto-thread-routing.md:47-49` と `features/supporting/04-front-agent-worker-selection.md:45-47` は望ましい状態を一文で述べているが、どの代表シナリオで確かめるのか、何が失敗なら不合格かが分からない。
  - `design/00-ideal-experience.md:153-155` で scenario-based validation を要求しているが、supporting feature まで落ちた時点でその粒度が失われている。

- [M2] 今回のような planning hierarchy の再設計に対して、ユーザー向けの「何が増え、何が減り、何のためか」の説明 obligation が弱かった。
  - `19d901b` では layer を増やしているが、その必要性と simpler alternative を一緒に固定した文書が無かった。
  - 結果として、構造自体は整っていても、ユーザーから見ると「複雑化していないか」という疑義が自然に残る。

### Low

- [L1] `features/00-feature-index.md:22-39` の supporting feature grouping は読みやすさ優先で、優先順位や decision sequence を直接は表していない。
  - 致命的ではないが、roadmap2 策定時には「読む順」と「決める順」が別文書で補われないと迷いやすい。

## Review Dimensions

### Tech Lead Review

#### Debt Prevention

- supporting feature を一律展開したことで、まだ決めない item まで maintenance surface にした。
- canonical source の競合は planning debt の温床になる。

#### Complexity Versus Value

- ideal experience, epics, supporting features, backlog ledger という 4 層構造自体は説明可能だが、現時点では supporting feature の適用範囲が広すぎる。
- `public-readiness` のような current ideal experience baseline 外の item まで同じ層に乗っており、価値より複雑さが先行している。

#### Decomposition and Boundaries

- root ideal input と normalized ideal experience の境界が曖昧である。
- epic と supporting feature の境界は概ね見えるが、supporting feature と deferred ledger の境界はまだ弱い。

#### Alignment With Declared Design

- 体験設計主導へ寄せる方向自体は `design/00-ideal-experience.md` と整合している。
- ただし supporting feature の一部は、その ideal baseline の外側にある request まで同じ規則で包んでおり、alignment が崩れている。

#### Senior-Engineer Smell Detection

- 「今後必要そうだから先に文書化しておく」が積み重なっており、process-first の匂いがある。
- user value を unlock する前に planning surface が増える構造は、後で説明不能な ceremony になりやすい。

#### Explanation Responsibility

- 今回の再設計は内部的には整理されているが、ユーザーに対して「なぜ supporting feature 層が必要なのか」「なぜ backlog だけでは不十分なのか」を短く説明する obligation が弱かった。
- planning structure の変更は、構造上の正しさだけでなく、ユーザーが変更理由を追えることまで満たす必要がある。

## Implementation Response Plan

- Date: 2026-04-09T15:04:14+09:00
- Reviewer: Codex agent (GPT-5)
- Base Commit: development-docs `19d901b`
- Plan Summary:
  - review rule 自体はこのターンで強化するが、flow redesign 本体には追加修正が必要である。
- Planned Fixes:
  - active ideal input と normalized ideal experience の canonical authority rule を明記する。
  - supporting feature を作る条件と、ledger に留める条件を追加する。
  - process / planning hierarchy 変更時の user-facing summary obligation を development process に明記する。
  - supporting feature の acceptance を scenario-linked にし、validation まで落とす。
- Deferred Items:
  - roadmap2 の actual milestone sequencing
  - ideal baseline 外 feature の最終的な置き場再設計

## Follow-Up Review History

### Entry 1

- Date: 2026-04-09T16:12:45+09:00
- Reviewer: Codex agent (GPT-5)
- Base Commit: development-docs `ecc52e9`
- Review Type: tech lead review
- References:
  - Planned fix: canonical authority rule
  - Planned fix: supporting feature creation condition
  - Planned fix: process / planning hierarchy user-facing summary obligation
  - Planned fix: supporting feature acceptance and validation
  - `rules/development-process.md`
  - `design/00-ideal-experience.md`
  - `reference/historical-documents/INDEX.md`
  - `features/README.md`
  - `features/backlog_item_template.md`
  - `features/01-feature-backlog.md`
  - `features/supporting/README.md`
  - `features/supporting/03-auto-thread-routing.md`
  - `features/supporting/04-front-agent-worker-selection.md`
- Result: Pass
- Notes:
  - canonical ideal experience source は `design/00-ideal-experience.md` に固定され、raw ideal experience input は `reference/historical-documents/` へ archive された。
  - historical document の扱いには archive index rule が追加され、ad hoc な `original_documents` 運用は廃止された。
  - supporting feature は roadmap-adjacent candidate に限定され、遠い deferred request は rich backlog item として保持する構造へ修正された。
  - backlog item template に priority, order, blockers, experience tie, thickness, design impact, current design constraint が入り、heavy / architectural item を軽く見積もる危険は下がった。
  - user-facing summary obligation も process rule に明記された。
- Remaining Risks:
  - backlog の priority / thickness / design impact は依然として判断を要するため、重大 item の格下げを防ぐには継続的な critical review が必要である。
  - roadmap2 の actual sequencing はまだ未決定であり、`near` item 同士の順序づけは後続判断が必要である。
- Risk Handling:
  - backlog classification の残リスクは accepted residual risk として扱う。ただし `heavy` または `architectural` な item の `priority assumption`、`thickness`、`design impact`、supporting feature 昇格は、次回以降も critical review を通さない限り stable planning input とみなさない。
  - roadmap2 sequencing の残リスクは explicit user decision required として扱う。`near` item の順序は supporting feature の並びや文書順から自動決定せず、次の roadmap planning で明示的に決める。

### Entry 2

- Date: 2026-04-09T16:32:23+09:00
- Reviewer: Codex agent (GPT-5)
- Base Commit: development-docs `aa2ac94`
- Review Type: tech lead review
- References:
  - Entry 1 remaining risk: backlog classification judgment
  - Entry 1 remaining risk: roadmap2 sequencing
  - `rules/development-process.md`
  - `requirements/ideal-experience-spec-template.md`
  - `reviews/review_template.md`
  - `reviews/README.md`
- Result: Pass
- Notes:
  - `design/00-ideal-experience.md` の canonical output rule は `requirements/ideal-experience-spec-template.md` にも埋め込まれ、前回監査で残っていた template 側の穴は解消された。
  - follow-up review の `Remaining Risks` は、受容済み残余リスク、deferred planned work、explicit user decision、未解決 finding のいずれかに disposition する rule を追加した。
  - backlog classification の残リスクは、以後 `heavy` / `architectural` item の分類変更や supporting 昇格に critical review を必須化することで扱う。
  - roadmap2 sequencing の残リスクは、`near` item の並びから自動推定せず、明示的 roadmap planning または user decision でしか決めない rule に落とした。
- Remaining Risks:
  - roadmap2 自体の sequencing decision はまだ未実施である。
- Risk Handling:
  - deferred planned work with tracked destination document or phase
    - roadmap2 sequencing は次の roadmap planning サイクルで扱う。`review_20260409142902_roadmap2-project-insight.md` と将来の roadmap2 文書が追跡先になる。
