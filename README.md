# udon-deckgenerator

## Description

定義ファイルと画像からデッキを組み立て、ユドナリウムのアーカイブを生成するツールです。
Deck generator for Udonarium from a define csv file and images.

## Install

クローン後に以下を実行してください。

```bash
pip install .
```

## Usage

まず、定義ファイルのテンプレートファイルを生成します。
下記コマンドを実行すると、"define_template.csv"がカレントディレクトリに生成されます。

```bash
udon-deckgen --output-tamplate
```

定義ファイルは下記のフォーマットになっています。

|列名|値|型|
|-|-|-|
|name|カード名|str|
|image_top|表面の画像名|str|
|image_bottom|裏面の画像名|str|
|deck|属するデッキ|str|
|number_of|枚数|int|

定義ファイル、定義ファイルで用いられている画像を格納したディレクトリを用意したら、
下記コマンドを実行します。
"output_dir"で指定したディレクトリにアーカイブファイルが生成されます。

```bash
udon-deckgen define_csv image_dir output_dir
```