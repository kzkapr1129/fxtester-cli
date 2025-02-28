# FXTester-cli

## 概要

本システムはMT4,5から出力したCSVを入力値として、傾向分析を実施し、実トレードに有用となる情報を発見することを目的としています。
FXTester-cliは複数のコマンドで構成されており、各コマンドの出力値を別コマンドへ入力することで複雑な分析を行えるように構成されています。

|# | コマンド名 | 入力値 | 出力値 | 機能 |
|-|-|-|-|-|
|1|Analyze|MT4,5のCSV|MT4,5が出力したローソク足の情報が格納されたjsonファイル| ローソク足の前後関係から計算できる情報を分析する |

## 実行例

Analyze機能
```
$ python fxtester.py analyze -i input.csv -o output.json
```

## 開発環境の構築

本システムを開発する上で必要となる環境と環境構築手順は以下の通りです。

開発環境のマシン
```
PC: Mac
OS: Monterey
```

環境構築手順
```
$ brew install go-task
$ task init
$ task init:py
```

## 開発の便利コマンド

開発時に必要となる

自動テストの実行
```
$ task test
```

lintの実行 (コードの自動修正なし)
```
$ task lint
```

lintの実行 (コードの自動修正あり)
```
$ task lint:fix
```