# ChatLobby 共有正本テンプレート

このディレクトリは、ChatLobby が参照する共有 Git リポジトリの最小構成テンプレートである。

## 目的

- 仕様、決定記録、作業ログ、実装コードの配置先を初期段階で固定する
- Open Terminal と File Browser から一貫した構造で参照できるようにする
- Phase B 以降の publish / update tool が保存先を前提化しやすくする

## ディレクトリ

- `docs/`: 安定化した公開・運用文書
- `specs/`: 機能仕様、要件、更新された spec
- `decisions/`: ADR や運用判断の記録
- `worklog/`: タスク単位の作業ログ
- `src/`: 実装コード

## 初期利用

1. このテンプレートを新しい共有リポジトリにコピーする
2. 共有リポジトリ側で `git init` するか、既存リポジトリに取り込む
3. Open Terminal から `/workspace/repos/...` に clone して利用する
