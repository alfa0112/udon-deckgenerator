import argparse
import datetime
import os
import sys
from pathlib import Path

import polars as pl
import pyudon

from udon_deckgen import data


def main():
    # 引数解析
    parser = argparse.ArgumentParser()
    parser.add_argument("define_csv",
                        nargs="?",
                        default=None,
                        help="デッキ内のカード一覧を定義するcsvファイル")
    parser.add_argument("image_dir",
                        nargs="?",
                        default=None,
                        help="define_csvで用いられている画像を格納しているディレクトリパス")
    parser.add_argument("output_dir",
                        nargs="?",
                        default=None,
                        help="生成したアーカイブファイルの保存先ディレクトリ")
    parser.add_argument("-n", "--name",
                        help="アーカイブのファイル名。渡さない場合は生成時刻を表す文字列がファイル名となる")
    parser.add_argument("--output-template",
                        action="store_true",
                        help="このオプションが渡された場合、カレントディレクトリにdefine_csvのテンプレートファイルを出力する")
    args = parser.parse_args()

    # テンプレート生成が指定されていた場合、生成処理を行ってプログラムを終了
    do_output_template: bool = args.output_template
    if do_output_template:
        df = data.DecksDefine.generate_template()
        current_dir = Path(os.getcwd())
        file_path = current_dir / "define_template.csv"
        df.write_csv(file_path)
        print(f"The define template file generated at {file_path}")
        sys.exit(0)

    # 引数が足りない場合、exit
    if not all((args.define_csv, args.image_dir, args.output_dir)):
        print("usage: __main__.exe [-h] [--output-template] define_csv image_dir output_dir\n"
              "error: the following arguments are required: define_csv, image_dir, output_dir")
        sys.exit(1)

    define_csv = Path(args.define_csv)
    image_dir = Path(args.image_dir)
    output_dir = Path(args.output_dir)
    name: str = args.name

    # 出力先ディレクトリ確保
    if not output_dir.exists():
        output_dir.mkdir(parents=True)

    # 読み込み
    try:
        define_csv_df = pl.read_csv(
            define_csv,
            columns=data.DecksDefine.REQUIRED_COLUMNS,
            dtypes=data.DecksDefine.DTYPES
        )
    except FileNotFoundError as e:
        print("The define file is not found.")
        print(e)
        sys.exit(2)
    define = data.DecksDefine(define_csv_df)

    image_dir = data.ImageDirectory(image_dir)

    # ゲーム生成
    table = pyudon.Table("Table", pyudon.DefaultBackgroudImage())
    game = pyudon.Game(table)

    # デッキ生成
    for i, deck_name in enumerate(define.unique_deck_names):
        try:
            deck = define.get_deck(deck_name, image_dir)
        except FileNotFoundError as e:
            print("The image file with specified name is not found. Check the image directory path.")
            print(e)
            sys.exit(2)
        game.add_deck(deck, i*100, 0)

    # Zipファイル作成
    if name:
        if not name.endswith(".zip"):
            name = f"{name}.zip"
        zip_path = output_dir / name
    else:
        now = datetime.datetime.now().strftime("%y%m%d_%H%M%S")
        zip_path = output_dir / f"{now}.zip"
    game.create_zip(zip_path)


if __name__ == "__main__":
    main()
