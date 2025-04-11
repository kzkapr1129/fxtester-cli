from analyzer import Analyzer
import pandas as pd
import os
import re
from pathlib import Path

test_folder = os.path.join(os.path.join(os.path.dirname(__file__), "test"))
test_file_path = os.path.join(os.path.join(os.path.dirname(__file__), "test"), "USDJPYH1.csv")

config = {
    "analyze": {
        "input": None,
        "output": None,
        "ext": None,
        "show_graph": False,
        "sma": [1],
        "ichimoku": False,
        "zigzag": False,
    }
}

class MockArgs:
    def __init__(self):
        self.input = test_file_path
        self.output = None
        self.ext = "json"
        self.show_graph = False
        self.sma = [1]
        self.ichimoku = False
        self.zigzag = False

def check_output(output_file: Path, args: MockArgs):
    if output_file.suffix == ".json":
        df = pd.read_json(output_file)
    elif output_file.suffix == ".csv":
        df = pd.read_csv(output_file)

    expect_columns = 7
    if args.zigzag:
        expect_columns += 7
    if 0 < len(args.sma):
        expect_columns += len(args.sma)
    if args.ichimoku:
        expect_columns += 5

    # カラムの確認
    assert len(df.columns) == expect_columns
    assert "datetime" in df.columns
    assert "open" in df.columns
    assert "high" in df.columns
    assert "low" in df.columns
    assert "close" in df.columns
    assert "tick" in df.columns
    assert "volume" in df.columns

    if args.zigzag:
        assert "zigzag" in df.columns
        assert "zigzag-kind" in df.columns
        assert "zigzag-from" in df.columns
        assert "zigzag-velocity" in df.columns
        assert "zigzag-delta" in df.columns
        assert "zigzag-peak-price" in df.columns
    else:
        assert "zigzag" not in df.columns
        assert "zigzag-kind" not in df.columns
        assert "zigzag-from" not in df.columns
        assert "zigzag-velocity" not in df.columns
        assert "zigzag-delta" not in df.columns
        assert "zigzag-peak-price" not in df.columns

    if args.ichimoku:
        assert "ichimoku_kijun_sen" in df.columns
        assert "ichimoku_tenkan_sen" in df.columns
        assert "ichimoku_senkou_span_1" in df.columns
        assert "ichimoku_senkou_span_2" in df.columns
        assert "ichimoku_chikou_span" in df.columns
    else:
        assert "ichimoku_kijun_sen" not in df.columns
        assert "ichimoku_tenkan_sen" not in df.columns
        assert "ichimoku_senkou_span_1" not in df.columns
        assert "ichimoku_senkou_span_2" not in df.columns
        assert "ichimoku_chikou_span" not in df.columns

    for average in args.sma:
        assert f"sma-{average}" in df.columns

def test_Analyzer_main_out_json(tmp_path):
    output_file = tmp_path / "USDJPYH1.json"
    args = MockArgs()
    args.ext = "json"
    args.sma = []
    args.ichimoku = False
    args.zigzag = False
    args.output = tmp_path
    Analyzer(config).main(args)

    # 出力ファイルの存在確認
    assert os.path.exists(output_file)

    # 出力ファイルの内容確認
    check_output(output_file, args)

def test_Analyzer_main_out_csv(tmp_path):
    output_file = tmp_path / "USDJPYH1.csv"
    args = MockArgs()
    args.ext = "csv"
    args.sma = []
    args.ichimoku = False
    args.zigzag = False
    args.output = tmp_path
    Analyzer(config).main(args)

    # 出力ファイルの存在確認
    assert os.path.exists(output_file)

    # 出力ファイルの内容確認
    check_output(output_file, args)

def test_Analyzer_main_json_indicator(tmp_path):
    output_file = tmp_path / "USDJPYH1.json"
    args = MockArgs()
    args.ext = "json"
    args.sma = [20, 50]
    args.ichimoku = True
    args.zigzag = True
    args.output = tmp_path
    Analyzer(config).main(args)

    # 出力ファイルの存在確認
    assert os.path.exists(output_file)

    # 出力ファイルの内容確認
    check_output(output_file, args)


def test_Analyzer_main_csv_indicator(tmp_path):
    output_file = tmp_path / "USDJPYH1.csv"
    args = MockArgs()
    args.ext = "csv"
    args.sma = [20, 50]
    args.ichimoku = True
    args.zigzag = True
    args.output = tmp_path
    Analyzer(config).main(args)

    # 出力ファイルの存在確認
    assert os.path.exists(output_file)

    # 出力ファイルの内容確認
    check_output(output_file, args)

def test_Analyzer_main_input_folder(tmp_path):
    output_file = tmp_path / "USDJPYH1.csv"
    args = MockArgs()
    args.input = test_folder
    args.ext = "csv"
    args.sma = [20, 50]
    args.ichimoku = True
    args.zigzag = True
    args.output = tmp_path
    Analyzer(config).main(args)

    # 出力ファイルの存在確認
    assert os.path.exists(output_file)

    # 出力ファイルの内容確認
    check_output(output_file, args)