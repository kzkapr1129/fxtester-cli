"""メインジュール
"""

import argparse
import sys
import importlib
from config.config import load_config
from pathlib import Path
import logging

logger = logging.getLogger("analyze")


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

    # analyzeパーサーの初期化
    analyze_parser = sub_parser.add_parser(
        "analyze", help="ローソク足の特徴を解析する", parents=[common_parser])
    analyze_parser.add_argument("-i", "--input", type=str,
                                help="入力ファイルのパス (csvまたはcsvが格納されたフォルダ)")
    analyze_parser.add_argument("-o", "--output", type=str,
                                help="出力ファイルのパス")
    analyze_parser.add_argument(
        "--show-graph", action='store_true', help="検出した特徴をグラフに重畳して表示する")
    analyze_parser.add_argument(
        "--sma", type=int, nargs='*', help="単純移動平均線の平均値を指定する")
    analyze_parser.add_argument(
        "--ichimoku", action="store_true", help="一目均衡表を計算する")
    analyze_parser.add_argument(
        "--zigzag", action="store_true", help="ジグザグを検出する")

    # コマンドのパース
    args = parser.parse_args()

    # 設定読み込み
    config = load_config(Path("config/config.toml"))

    match args.mode:
        case 'analyze':
            if args.input == None:
                logger.error("-i or --input is mandatory")
                return
            analyzer = importlib.import_module(
                "analyze.analyze").Analyzer(config)
            analyzer.main(input_path=Path(args.input),
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
