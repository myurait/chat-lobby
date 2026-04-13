# ChatLobby ロードマップ

## 1. ロードマップの目的

本ロードマップは、ChatLobby を「構想段階」から「公開可能な self-hosted 統合チャット基盤」へ進めるための段階計画を示すものである。

本ロードマップでは、要件定義書および開発計画書を前提に、優先順位、到達目標、段階的な公開可能性を整理する。

---

## 2. 開発方針

ChatLobby は、以下の方針で進める。

- frontdoor は Open WebUI を採用する
- 文書・仕様・設計・決定の正本は Git に置く
- Codex / Claude Code は背後ワーカーとして扱う
- 最初からすべてを自動化しない
- まずは「会話 → 文書化 → Git 昇格 → ワーカー依頼」を成立させる
- その後に「自動振り分け」「状態可視化」「仕様差し戻しループ」を追加する
- 公開可能性を意識し、Open WebUI 本体改変は最小化する

---

## 3. フェーズ別ロードマップ

以下は優先実装順である。

### Phase A. 基盤起動

#### 目的

ChatLobby の最小 self-host 環境を成立させる。

#### 到達目標

- Open WebUI が Docker で起動する
- スマホからログインして会話できる
- Notes / Folders & Projects / File Browser が使える
- テスト用 Git repo を Open Terminal から扱える

#### 成果物

- `docker-compose.yml`
- `README.md`
- 初期セットアップ手順

#### 成功判定

- スマホから Open WebUI にアクセスできる
- テスト用 repo を clone し、ファイルを閲覧できる

### Phase B. 正本化フロー

#### 目的

会話内容や Notes を Markdown 文書として Git に昇格させる。

#### 到達目標

- 会話や草案メモから spec / ADR / worklog を生成できる
- 生成した文書が repo の所定位置へ保存される
- Open WebUI 上から文書を確認できる

#### 成果物

- publish tool
- Markdown テンプレート
- 文書配置規約

#### 成功判定

- 「これを仕様書にして」で repo に文書が生成される
- その文書が以後の会話で参照可能になる

### Phase C. 単一ワーカー接続

#### 目的

前面チャットから、まずは1種類の実装ワーカーを起動できるようにする。

#### 到達目標

- 前面エージェントから Codex または Claude Code のいずれかに依頼できる
- ワーカーが同じ repo を読める
- 作業結果が前面チャットに戻る

#### 優先順位

初期優先は Claude Code 接続とする。
理由は、スマホからの状態確認価値が高く、Remote Control と組み合わせた体験を早く検証できるためである。

#### 成果物

- Claude adapter または Codex adapter
- 最低限の task 実行 UI

#### 成功判定

- frontdoor からワーカー起動が行える
- 実装結果がチャットへ戻る

### Phase D. 両ワーカー接続

#### 目的

Codex / Claude Code の双方を ChatLobby 配下に置く。

#### 到達目標

- 前面エージェントから両ワーカーへ依頼できる
- 両者が同じ Git 正本とコードベースを参照できる
- 手動でのワーカー選択が可能になる

#### 成果物

- Codex adapter
- Claude adapter
- knowledge adapter

#### 成功判定

- 同一 repo に対して両ワーカーが作業できる
- 作業結果が同一会話面に返る

### Phase E. 自動振り分け

#### 目的

ユーザーが Claude / Codex を選ばなくてよい状態を作る。

#### 到達目標

- 実装依頼、不具合修正、仕様差し戻しの類型ごとに routing rule が動作する
- ルーティング結果がユーザーに提示される
- 必要時のみ手動 override を行う

#### 成果物

- dispatcher
- routing rules
- routing policy ドキュメント

#### 成功判定

- 「実装して」「これを直して」で適切なワーカーに流れる

### Phase F. 状態可視化

#### 目的

配下ワーカーの作業状態を前面チャットから確認できるようにする。

#### 到達目標

- 実行中タスク一覧が見える
- current step が見える
- changed files が見える
- approval 待ちが見える
- 停止理由が見える

#### 成果物

- status store
- status panel
- status model ドキュメント

#### 成功判定

- スマホからでも進捗確認が可能になる

### Phase G. 仕様差し戻しループ

#### 目的

実装結果をもとに仕様・決定記録を更新し、再び共通知識として使えるようにする。

#### 到達目標

- 差分要約から spec / ADR / worklog 更新ができる
- 実装結果を受けて仕様の修正案が生成できる
- 修正後の仕様が次のワーカー入力に使われる

#### 成果物

- spec update tool
- ADR update tool
- spec feedback loop ドキュメント

#### 成功判定

- 実装 → 仕様更新 → 再実装 の往復が会話圏で成立する

### Phase H. 公開準備

#### 目的

ChatLobby を他者が試せる状態に整える。

#### 到達目標

- サンプル構成付き README を整備する
- deploy 手順を簡略化する
- example project を添付する
- Open WebUI 依存範囲と自作範囲を明確にする

#### 成果物

- 公開用 README
- example project
- deployment guide
- architecture doc

#### 成功判定

- 第三者が repo を clone し、最小構成を起動できる

---

## 4. リリース戦略

### v0.1

最小の ChatLobby。

含めるもの:
- Open WebUI 起動
- Git 正本運用
- Notes / Projects 運用
- 文書 publish
- 単一ワーカー接続

目的:
- 会話 → 文書 → 実装依頼 の最短ループを成立させる

### v0.2

複数ワーカー統合版。

含めるもの:
- Codex / Claude 両対応
- knowledge adapter
- 手動ワーカー切替

目的:
- 同一 frontdoor から複数ワーカーを扱えることを示す

### v0.3

運用補助版。

含めるもの:
- 自動振り分け
- 状態パネル
- approval 可視化

目的:
- 「どちらを使うか」と「今どうなっているか」をユーザーから隠蔽する

### v0.4

仕様ループ版。

含めるもの:
- 仕様差し戻し
- ADR 更新
- worklog 自動生成

目的:
- 仕様と実装の往復を ChatLobby の中核体験にする

### v1.0

公開可能版。

含めるもの:
- 導入手順整備
- サンプルプロジェクト
- 最小構成の安定化
- 運用ドキュメント整備

目的:
- 自分用の統合基盤から、他者にも公開可能な OSS へ移行する

---

## 5. 初期優先順位

初期段階で最優先にすべきものは以下である。

1. Open WebUI + Git 正本の成立
2. 文書 publish フロー
3. Claude Code 接続
4. Codex 接続
5. 自動振り分け
6. 状態パネル
7. 仕様差し戻し
8. 公開整備

この順序にする理由は、まず会話を正本へ昇格させる流れを作らない限り、その後のワーカー統合が安定しないためである。

---

## 6. リスクと対策

### 6.1 Open WebUI 依存の偏り

#### リスク
Open WebUI への依存が強すぎると、将来的な置換が難しくなる。

#### 対策
本体改変は最小化し、plugin / sidecar / adapter を基本とする。

### 6.2 ワーカー状態可視化の不統一

#### リスク
Codex と Claude Code のイベント粒度が異なり、統一表示が難しい。

#### 対策
status model を先に定義し、各ワーカー側で正規化する。

### 6.3 正本化の手間

#### リスク
会話から Git 正本へ昇格する作業が億劫になり、運用が途切れる。

#### 対策
publish action を frontdoor 上のワンアクションに寄せる。
文書テンプレートと保存先規約を固定する。

### 6.4 ChatGPT 依存の期待値ずれ

#### リスク
ChatGPT Projects 的体験を frontdoor 側で完全再現できるとは限らない。

#### 対策
ChatLobby は ChatGPT 互換ではなく、「会話から実装チームを動かす frontdoor」として価値定義する。

---

## 7. ロードマップ要約

ChatLobby は、まず Open WebUI と Git を基盤にして「会話を正本へ昇格できる」状態を作り、その上に Claude Code / Codex のワーカー統合、自動振り分け、状態可視化、仕様差し戻しを順に積み上げる。

この順序により、最初から大規模なオーケストレータを作り込まずに、会話中心の体験を維持したまま、段階的に統合開発基盤へ育てていく。
