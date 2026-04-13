# Review: Roadmap2 Project Insight

- Date: 2026-04-09T14:29:02+09:00
- Reviewer: GPT-5.4 Thinking
- Base Commit: development-docs `018fedf`
- Scope: roadmap1 の中断・再編前提での全体計画レビュー。対象は `design/01-project-charter.md`、`design/02-architecture.md`、`roadmap/01-initial-roadmap.md`、`features/01-feature-backlog.md`、および理想体験設計入力である。
- Review Type: design review
- Trigger: roadmap2 / 理想体験設計 / feature backlog の再編検討
- Criteria:
  - 当初想定していた理想体験に対して、現行計画がどこまで直結しているか
  - roadmap2 を起動するための入力文書として、feature backlog が十分な粒度と構造を持っているか
  - 長期的な AI 主体開発サイクルに耐える文書構造になっているか
  - 体験設計、責務分離、将来の実装優先順位づけに必要な論点が漏れていないか
  - 壁打ちからプロジェクト昇格までの導線が、本質的な設計サイクルの妨げになっていないか
  - 新規会話 / 継続会話の自動理解と、誤判定時の再ルーティング体験が設計対象として十分に扱われているか

---

## Evidence Normalization Note

- 元文書 `chatlobby-roadmap2-project-insight-review-2026-04-09-v2.md` は review evidence の命名規則と metadata 形式に沿っていなかった。
- review 内容は保持しつつ、`reviews/` 配下の evidence 形式へ正規化した。
- source evidence には日付のみがあり時刻がなかったため、`Date` には import timestamp を採用した。

## Findings

### Critical

- [C1] 現行 `features/01-feature-backlog.md` は、roadmap2 を起こすための体験設計入力として不十分である。
  - 各項目が「どの課題を解決するためのものか」「どの理想体験に寄与するのか」「未実装だと何が困るのか」を記述していない。
  - そのため、deferred 項目の一覧としては使えても、体験から逆算して優先順位を判断する材料になっていない。
  - この状態のまま roadmap2 を策定すると、機能実装の順番表は作れても、「ユーザーが何を体験できるようになるのか」という上位目的から開発を制御できない。
  - 是正が必要である。feature は単なる要望の見出しではなく、体験・問題・境界・依存関係・成功状態を持つ設計入力へ改める必要がある。

- [C2] 現行 backlog は、異なる階層の論点を 1 ファイルに混在させており、分解単位が不適切である。
  - 体験の中核、UI 派生、外部連携、公開準備、将来一般化が同列に並んでいる。
  - これにより、重要だが地味な基盤設計と、後回しでよい派生機能の重みづけが壊れている。
  - 特に roadmap2 は体験設計主導へ切り替える局面であるため、この情報設計の甘さはそのまま計画の失敗要因になる。

- [C3] 当初想定の理想体験を成立させる中核である「前面 AI の継続記憶・文脈復元・監督責務」が、設計対象として明示分解されていない。
  - 現行の charter / architecture / roadmap1 は、frontdoor、dispatcher、adapter、Git 正本、status 可視化までは整理されている。
  - しかし、ユーザーが本当に求めているのは、それらを束ねた「前面 AI が全体を覚え、文脈を復元し、必要なワーカーに適切に割り振り、結果を整理して返す体験」である。
  - 現在の feature backlog では、その核心が「類似話題・関連作業への自動スレッド振り分け」と「前面エージェントによる配下エージェント振り分け」に断片化され、しかも薄い deferred 項目として保持されているだけである。
  - この扱いでは弱い。roadmap2 の基礎となるべき中核テーマとして、少なくとも以下を独立設計対象に格上げすべきである。
  - front agent / supervisor の責務
  - context / memory model
  - thread routing / project boundary
  - task decomposition / result synthesis
  - conversation re-routing / context correction

- [C4] 「壁打ちから速やかにプロジェクトへ昇格する体験」が設計対象として欠落している。
  - ユーザーは、本質的には体験設計、機能設計、仕様整理に入りたいのであって、project 体裁、文書置き場、命名、テンプレート選択、正本化作法の検討から始めたいわけではない。
  - にもかかわらず、現行文書群では「正本化する」「文書を置く」「テンプレートを持つ」ことは整理されている一方で、「壁打ち段階から、ほぼ摩擦なく project へ昇格させる」導線が体験要件として固定されていない。
  - これは重大である。なぜなら、このプロジェクトの目的は文書運用を正しくすること自体ではなく、文書整備の迷いを前面 AI が吸収し、ユーザーを本質的な開発サイクルへ早く入れることにあるからである。
  - roadmap2 では `project bootstrap friction removal` を中核 experience pillar として明示すべきである。

- [C5] 新規会話 / 継続会話の判定をユーザーへ委ねない体験と、誤判定時の再ルーティング体験が不足している。
  - ユーザーは「これは新しい会話ですか？」のような yes/no 確認を繰り返したくない。
  - また、高度な会話継続体験では、単に自動判定するだけでは足りない。誤って既存コンテキストへ接続した会話を、自然な対話の中で別コンテキストへ切り直せる必要がある。
  - 例:
  - AI「このプロジェクトの話ですね。前回の続きとして整理します」
  - User「勘違いさせた。別の話だ」
  - AI「失礼しました。新しい会話スレッドに戻します」
  - これは UI 上の小改善ではなく、thread routing と memory model の根幹要件である。
  - 現行 feature backlog では「自動スレッド振り分け」までしか触れられておらず、再振り分け、文脈切替、誤接続修正の責務が設計対象として抜けている。

- [C6] 「完成したらユーザーがどのように感じるか」の受け皿となる体験仕様が薄い。
  - roadmap2 では、「ユーザーは何をしなくてよくなるのか」「どの不快が消えるのか」「どういう会話が自然に通るべきか」を基準にしなければ、理想体験からの逸脱を検知できない。
  - 特にこのプロジェクトは、単に機能を足すよりも、会話起点の負荷をどれだけ消せるかが本質である。
  - よって、機能一覧の前に、体験仕様文書を正本として置く必要がある。

### High

- [H1] 現行 backlog は、各 feature の「なぜ重要か」を説明していない。
- [H2] backlog が solution-first になっており、problem-first ではない。
- [H3] deferred 管理の使い方が適切でない可能性がある。
- [H4] roadmap1 のフェーズ構造は、統合基盤の立ち上げとしては妥当だが、体験設計駆動の開発へ移るための橋渡しがない。

### Medium

- [M1] feature 間の依存関係が明示されていない。
- [M2] ユーザー体験の受け入れ基準がない。
- [M3] feature の配置先が不適切である。

### Low

- [L1] 現行 feature 名称は、寄与体験よりも実装対象を先に見せるものが多い。
- [L2] Source と Promotion Condition は残してよいが、それだけでは設計上の意味が弱い。

## Review Dimensions

### Design Review

#### Debt Prevention

- 現状のまま backlog を増築し続けると、将来の設計負債は「コード」ではなく「計画文書の誤構造」として蓄積する。
- 特に危険なのは、体験の中核要件が deferred backlog の一項目として埋もれ、後続フェーズで派生機能と同列に扱われることである。
- roadmap2 着手前に、少なくとも feature の分類体系を再構築する必要がある。
- 推奨する分類:
- Experience Pillars
- Product Epics
- Supporting Features
- Exploratory / Deferred Features

#### Decomposition and Boundaries

- 現行 feature backlog は分解境界が曖昧である。
- 少なくとも以下の境界は分けるべきである。
- 体験仕様
- プロダクト責務
- UI / interaction
- 外部連携
- 後回し項目
- front agent / supervisor と dispatcher は別物として明確に分離すべきである。
- publish / documentation flow と `project elevation flow` も別物として分離すべきである。

#### Alignment With Declared Design

- charter と architecture は、frontdoor、複数ワーカー統合、Git 正本、状態可視化という方針ではよく整合している。
- しかし、理想体験の中心にある「記憶された会話の継続性」「壁打ちから project への即時昇格」「前面 AI の監督役としての責務」は、まだ宣言レベルに達していない。
- roadmap2 の前提として、理想体験仕様、context / memory model、front agent / supervisor、thread routing / project boundary / re-routing、project elevation flow、experience-driven roadmap を補完すべきである。

#### Senior-Engineer Smell Detection

- backlog が「いつかやりたいことの保管庫」になっており、「計画を動かす判断装置」になっていない。
- 重要な項目が backlog の下層へ沈む、派生 UI と中核機能の優先度が混ざる、roadmap 昇格時に背景整理を毎回やり直す、といった破綻が起きやすい。

## Implementation Response Plan

- Date: 2026-04-09T14:29:02+09:00
- Reviewer: Codex agent (GPT-5)
- Base Commit: development-docs `018fedf`
- Plan Summary:
  - 現段階では review evidence の正規配置を先に行い、理想体験文書そのものの正規展開は後続のプロセス整理と要件定義ルール整備の後に行う。
- Planned Fixes:
  - review evidence を `reviews/` 配下に正規配置する。
  - 理想体験文書は当面 `development-docs/` 直下の作業入力文書として保持する。
  - その後、development process に「理想体験仕様が無ければ要件定義ヒアリングを先に行う」規則を追加する。
  - interview 項目、要件定義ルール、テンプレートを設計する。
  - ideal experience -> feature -> roadmap -> cycle task -> validation の planning chain を development process に追加する。
  - roadmap / feature / review で user intent と validation traceability を必須化する。
- Deferred Items:
  - roadmap2 本体の策定
  - feature backlog の epic / deferred 分離

## Follow-Up Review History

### Entry 1

- Date: 2026-04-09T14:29:02+09:00
- Reviewer: Codex agent (GPT-5)
- Base Commit: development-docs `018fedf`
- Review Type: design review
- References:
  - review initial findings C1-C6, H1-H4, M1-M3, L1-L2
  - current `rules/development-process.md`
  - current `features/01-feature-backlog.md`
  - current planning chain absence
- Result: Pass with additional findings
- Notes:
  - 初回 review が指摘した feature backlog の弱さに加え、現行 development process には planning chain と validation loop の定義欠損がある。
  - 具体的には、ideal experience から roadmap をどう導くか、roadmap から cycle task をどう選ぶか、そして delivered work が user intent に合っているかをどう検証するかが規則化されていない。
  - この欠損は feature backlog の弱さとは別の process-level 問題であり、development process と supporting templates の再設計対象として追加で扱うべきである。
- Additional Findings:
  - [C7] ideal experience -> feature -> roadmap -> cycle task の planning chain が未定義である。
  - [C8] user intent に対する validation loop が未定義であり、実装が正しく動いても意図した体験を作れているか判断できない。
  - [H5] ideal experience が無い、または弱い場合の requirement discovery / interview protocol が無い。
  - [H6] roadmap item と feature item に、traceability と validation expectation を必須化する format rule が無い。
- Remaining Risks:
  - 現時点では理想体験文書が未正規化のまま残る。
  - planning chain と validation loop は、この後の process 改修で具体化されるまでは運用に残り続ける。

### Entry 2

- Date: 2026-04-09T14:43:42+09:00
- Reviewer: Codex agent (GPT-5)
- Base Commit: development-docs `018fedf`
- Review Type: design review
- References:
  - Entry 1 additional findings `C7`, `C8`, `H5`, `H6`
  - `rules/development-process.md`
  - `requirements/requirement-discovery-rules.md`
  - `requirements/ideal-experience-interview-template.md`
  - `requirements/ideal-experience-spec-template.md`
  - `roadmap/roadmap_template.md`
  - `features/feature_template.md`
- Result: Pass
- Notes:
  - planning chain は `ideal experience input -> requirement discovery -> planning inputs -> roadmap item -> cycle acceptance / validation` として development process に明記された。
  - requirement discovery が `requirements/` 配下に分離され、ideal experience 不在時に interview を必須化するルールと template が追加された。
  - roadmap と feature の template により、problem, experience contribution, acceptance, validation を planning input として持たせる導線ができた。
  - review template と AI reading order も更新され、planning docs の review で traceability と validation completeness を見る前提が共有された。
- Remaining Risks:
  - active ideal experience document の最終的な canonical placement と normalized filename は未確定である。
  - `features/01-feature-backlog.md` 自体はまだ holding area のままで、planning-ready feature spec への正規化は次サイクル課題である。

### Entry 3

- Date: 2026-04-09T14:51:12+09:00
- Reviewer: Codex agent (GPT-5)
- Base Commit: development-docs `018fedf`
- Review Type: design review
- References:
  - Entry 2 remaining risk `features/01-feature-backlog.md` normalization
  - `design/00-ideal-experience.md`
  - `features/00-feature-index.md`
  - `features/epics/`
  - `features/supporting/`
  - `features/01-feature-backlog.md`
- Result: Pass
- Notes:
  - raw ideal experience は planning-ready な `design/00-ideal-experience.md` へ正規化され、そこから `features/00-feature-index.md`、`features/epics/`、`features/supporting/` の順で planning chain を辿れる状態になった。
  - raw request をそのまま backlog に積む構造はやめ、`features/01-feature-backlog.md` は deferred request ledger に縮約した。
  - 各 deferred request は対応する supporting feature と parent epic を持つため、long-term goal から feature への分解と、feature から roadmap 候補への昇格判断の導線が明確になった。
- Remaining Risks:
  - roadmap2 自体はまだ user decision 待ちであり、epic / supporting feature から actual roadmap milestone への優先順位づけは未着手である。
  - root に保持している raw ideal experience input は、後続で canonical document に完全移管する必要がある。
