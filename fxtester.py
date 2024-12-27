"""メインジュール
"""

import argparse
import sys
import importlib
from config.config import load_config
from pathlib import Path
import logging

logger = logging.getLogger("fxtester")


def main():
    """メイン関数

    FXTester-cliのエントリーポイントとなる関数
    """
    # 共通パーサーの初期化
    common_parser = argparse.ArgumentParser(add_help=False)
    common_parser.add_argument(
        "-c", "--config", default="config/config.toml", help="設定ファイルのパスを指定する")

    # サブコマンドパーサーの初期化
    parser = argparse.ArgumentParser(description="", add_help=False)
    sub_parser = parser.add_subparsers(
        dest="mode", required=True, help="サブコマンド")

    # extractパーサーの初期化
    extract_parser = sub_parser.add_parser(
        "extract", help="ローソク足の特徴を抽出する", parents=[common_parser])
    extract_parser.add_argument("-i", "--input", type=str,
                                help="入力ファイルのパス (csvまたはcsvが格納されたフォルダ)")
    extract_parser.add_argument("-o", "--output", type=str,
                                help="出力ファイルのパス")
    extract_parser.add_argument(
        "--show-graph", action='store_true', help="検出した特徴をグラフに重畳して表示する")
    extract_parser.add_argument(
        "--sma", type=int, nargs='*', help="単純移動平均線の平均値を指定する")
    extract_parser.add_argument(
        "--ichimoku", action="store_true", help="一目均衡表を計算する")
    extract_parser.add_argument(
        "--zigzag", action="store_true", help="ジグザグを検出する")

    # コマンドのパース
    args = parser.parse_args()

    # 設定読み込み
    config = load_config(Path("config/config.toml"))

    match args.mode:
        case 'extract':
            if args.input is None:
                logger.error("-i or --input is mandatory")
                return
            extractor = importlib.import_module(
                "cmds.extract.extract").Extractor(config)
            extractor.main(input_path=Path(args.input),
                           output_path=args.output,
                           show_graph=args.show_graph,
                           sma=args.sma,
                           enable_ichimoku=args.ichimoku,
                           enable_zigzag=args.zigzag)
        case _:
            print(f"予期しないモードが指定されました: {args.mode}")
            sys.exit()


if __name__ == "__main__":
    main()
