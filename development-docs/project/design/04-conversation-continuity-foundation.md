# 会話継続の基礎設計

## 1. この文書の位置づけ

- active roadmap Milestone 1「前の続きが自然につながる状態へ近づける」の planning package である。
- ここで定義するのは **文書ベースの軽量 pilot** であり、会話継続の最終実装ではない。
- dedicated persistence layer の追加は将来の enrichment path として `features/01-feature-backlog.md` Feature 012 に記録済みである。
- pilot の検証結果が、後続の memory model 設計判断の入力になる。

## 2. なぜ今これが必要か

- 現在の ChatLobby は、状態確認・知識の正本化・ワーカー起動が動作している。
- しかし「前の続き」「この前の件」のような曖昧な再開に対して、有力な文脈を自然に返す仕組みはまだ無い。
- この不足が残ると、ユーザーは毎回背景を説明し直し、後続の worker 選定や project 化も前段で詰まる。
- 理想体験 Pillar 2「Context Memory and Conversation Continuity」の最初の前進として、まず「自然な再開」と「短い訂正で戻れること」を検証する。

## 3. 構造判断の記録

- Milestone 1 の出発点として、2つの構造選択肢を検討した。
  - **Option A**: 新しい persistence layer を追加せず、Git の canonical documents と recent task summaries を継続情報源として使う文書ベースの軽量 pilot。
  - **Option B**: Milestone 1 の段階で conversation continuity 専用の persistent store を追加し、会話要約や thread summaries を継続的に保持する。
- Autonomous Proceed Conditions（`rules/development-process.md` Section 5）に基づき、Option A を自律的に選択した。
  - 推奨理由は design document に記載済み、合理的なユーザー好みで覆す余地が少ない、後からの方針転換が容易。
- **Option A はこの pilot の出発点であり、最終形ではない。** Option B は `features/01-feature-backlog.md` Feature 012 に deferred item として保持されている。pilot の検証結果から、dedicated persistence layer が必要と判明した場合に昇格する。

## 4. 前提

### すでにあるもの

- Open WebUI が前面入口。dispatcher、knowledge adapter、status store、publish flow が動作している。
- canonical documents は Git にあり、knowledge adapter で検索・読取できる。
- status store に最近の worker task の要約が蓄積される。

### まだ無いもの

- Open WebUI の会話履歴を継続会話判定のために直接読む層。
- 会話継続専用の persistent memory store。
- thread と project の再接続ルール（front agent がユーザーへどう見せるかという動作定義）。

## 5. pilot の範囲

### 対象に含めるもの

- 継続会話候補を出す最小情報源の定義
- 継続会話と新規会話の最小境界
- 誤接続時の correction flow
- pilot で実際に見せるユーザー向け動作

### 対象に含めないもの

- full memory model の永続実装
- project elevation の本実装
- worker auto-selection の本実装
- Open WebUI conversation history の完全同期

## 6. 用語

- **会話継続**: ユーザーが曖昧参照で会話を再開したときに、有力な過去文脈を推定して返せること。
- **文脈候補**: 現在のメッセージともっとも関連が強いと推定された既存の文脈。pilot では thread 候補だけでなく、関連 project や直近 task summary も含めてよい。
- **訂正フロー**: システムが推定した文脈候補が間違っていたときに、ユーザーの短い訂正で再候補化または新規文脈へ戻せる流れ。

## 7. pilot の提案動作

### 7.1 継続情報源

- Git 上の canonical documents（spec、ADR、worklog、knowledge、roadmap、feature documents）
- recent task の status と result summary（status store 上の task title、current step、result summary）
- 昇格済みの会話要約（publish 済みで Git 正本へ上がった要約のみ）

### 7.2 routing の分岐

- 有力候補が無い場合: 新規会話として扱う。
- 有力候補が一つの場合: その文脈を第一候補として提示しつつ会話を進める。
- 複数候補があり得る場合: 最有力候補を先に示し、必要なら他候補へ短く切り直せるようにする。

### 7.3 訂正優先の原則

- pilot の目的は、毎回ユーザーへ「新規ですか、継続ですか」と聞き返すことではない。
- 最有力候補を会話上で示しつつ、そのまま前へ進める correction-first の方針を推奨する。
- 誤っていた場合は、ユーザーの短い訂正で別候補または新規文脈へ戻せることを最重要にする。

## 8. pilot の範囲限界と将来パス

この pilot は以下を **扱えない**。これらは pilot の検証結果を受けて判断する。

- **publish されていない純粋な会話文脈**: Git 正本に上がっていない雑談ベースの前回の話は、pilot の情報源に含まれない。この不足が深刻と判明した場合、Feature 012（dedicated persistence layer）の昇格を検討する。
- **会話要約の自動生成**: pilot では publish 済み要約のみを使う。自動要約が必要と判明した場合は別途設計する。
- **高精度の thread 自動接続**: pilot は correction-first であり、auto-connect の精度向上は Feature 003 の範囲。

## 9. validation scenario

### Scenario A: 「前の続き」

- 入力: ユーザーが「この前の続きなんだけど」と再開する。
- 期待動作: front agent は最有力候補の文脈を短く示し、その前提で会話を進める。
- 訂正時の動作: ユーザーが「いや別件」と短く返せば、別候補または新規文脈へ戻る。

### Scenario B: 似た話題だが別 project

- 入力: ユーザーが似た話題だが別 project の相談を始める。
- 期待動作: front agent は既存 project 候補を示しつつ、確定しきらない場合は誤接続前提の correction を許容する。
- 訂正時の動作: ユーザーが project 差分を一言で言えば、文脈を切り替え直せる。

### Scenario C: 有力候補が無い

- 入力: ユーザーが完全に新しい相談を始める。
- 期待動作: front agent は無理に継続会話へ寄せず、新規文脈として扱う。

## 10. 実装境界

- candidate extraction は knowledge adapter と status store の read path を中心に設計する。
- front agent pipe / dispatcher 前段で candidate proposal payload を返す最小 pilot を定義する。
- correction flow は chat 上の短い言い換えで再評価する。
- pilot 完了後、「publish 前の会話文脈が必要か」「auto-thread routing の精度をどこまで上げるか」を検証結果から判断する。
