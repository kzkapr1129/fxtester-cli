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

    # analyzerパーサーの初期化
    analyzer_parser = sub_parser.add_parser(
        "analyze", help="インジケータを計算する", parents=[common_parser])
    analyzer_parser.add_argument("-i", "--input", type=str, required=True,
                                 help="入力ファイルのパス (csvまたはcsvが格納されたフォルダ)")
    analyzer_parser.add_argument("-o", "--output", type=str,
                                 help="出力ファイルのパス")
    analyzer_parser.add_argument(
        "-e", "--ext", choices=["json", "csv"], help="出力ファイルの拡張子", default="json")
    analyzer_parser.add_argument(
        "-g", "--show-graph", action='store_true', help="検出した特徴をグラフに重畳して表示する")
    analyzer_parser.add_argument(
        "-s", "--sma", type=int, nargs='*', help="単純移動平均線の平均値を指定する")
    analyzer_parser.add_argument(
        "-k", "--ichimoku", action="store_true", help="一目均衡表を計算する")
    analyzer_parser.add_argument(
        "-z", "--zigzag", action="store_true", help="ジグザグを検出する")

    # detectorパーサーの初期化
    detector_parser = sub_parser.add_parser(
        "detect", help="抵抗帯の情報を検出する", parents=[common_parser])
    detector_parser.add_argument("-i", "--input", type=str, required=True,
                                 help="入力ファイルのパス (csvまたはcsvが格納されたフォルダ)")
    detector_parser.add_argument("-o", "--output", type=str,
                                 help="出力ファイルのパス")
    detector_parser.add_argument(
        "-e", "--ext", choices=["json", "csv"], help="出力ファイルの拡張子", default="json")
    detector_parser.add_argument(
        "-g", "--show-graph", action='store_true', help="検出した特徴をグラフに重畳して表示する")
    detector_parser.add_argument(
        "-w", "--window", type=int, help="抵抗帯判定に使用するウインドウの幅", default=1)
    detector_parser.add_argument(
        "-t", "--threshold", type=float, help="抵抗帯面積率の閾値", default=0.8)
    # コマンドのパース
    args = parser.parse_args()

    # 設定読み込み
    config = load_config(Path(args.config))

    match args.mode:
        case 'analyze':
            analyzer = importlib.import_module(
                "cmds.analyze.analyzer").Analyzer(config)
            analyzer.main(input_path=Path(args.input),
                          output_path=args.output,
                          output_ext=args.ext,
                          show_graph=args.show_graph,
                          sma=args.sma,
                          enable_ichimoku=args.ichimoku,
                          enable_zigzag=args.zigzag)
        case 'detect':
            detector = importlib.import_module(
                "cmds.detect.detector").Detector(config)
            detector.main(input_path=Path(args.input),
                          output_path=args.output,
                          output_ext=args.ext,
                          show_graph=args.show_graph,
                          window_size=args.window,
                          threshold=args.threshold)
        case _:
            print(f"予期しないモードが指定されました: {args.mode}")
            sys.exit()


if __name__ == "__main__":
    main()
