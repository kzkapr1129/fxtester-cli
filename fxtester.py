"""メインジュール
"""

import argparse
import sys
import importlib
from config.config import load_config
from pathlib import Path


def main():
    """メイン関数

    FXTester-cliのエントリーポイントとなる関数
    """
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('mode', help="処理モード")
    parser.add_argument("-i", "--input", type=str,
                        help="入力ファイルのパス (csvまたはcsvが格納されたフォルダ)", required=True)
    parser.add_argument("-o", "--output", type=str,
                        help="出力ファイルのパス", required=True)

    args = parser.parse_args()

    # 設定読み込み
    config = load_config(Path("config/config.toml"))

    match args.mode:
        case 'analyze':
            analyzer = importlib.import_module(
                "analyze.analyze").Analyzer(config)
            analyzer.main(input_path=Path(args.input), output_path=args.output)
        case _:
            print(f"予期しないモードが指定されました: {args.mode}")
            sys.exit()


if __name__ == "__main__":
    main()
