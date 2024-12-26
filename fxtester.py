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
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('mode', help="処理モード", choices=["analyze"])
    parser.add_argument("-i", "--input", type=str,
                        help="入力ファイルのパス (csvまたはcsvが格納されたフォルダ)")
    parser.add_argument("-o", "--output", type=str,
                        help="出力ファイルのパス")
    parser.add_argument("--show-graph", action='store_true')
    parser.add_argument("--sma", type=int, nargs='*')
    parser.add_argument("--ichimoku", action="store_true")
    parser.add_argument("--zigzag", action="store_true")

    args = parser.parse_args()
    print(args)

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
