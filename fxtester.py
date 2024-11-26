import argparse
import sys
import importlib
from config.config import load_config
from pathlib import Path

parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('mode', help="処理モード")

args = parser.parse_args()

# 設定読み込み
config = load_config(Path("config/config.toml"))
print(config)

match args.mode:
    case 'analyze':
        analyzer = importlib.import_module("analyze.analyze").Analyzer(config)
        analyzer.main()
    case _:
        print(f"予期しないモードが指定されました: {args.mode}")
        sys.exit()
