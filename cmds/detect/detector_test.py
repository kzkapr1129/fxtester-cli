from detector import Detector
import os
import pandas as pd
from pandas import DataFrame
from pathlib import Path

test_folder = os.path.join(os.path.join(os.path.dirname(__file__), "test"))
test_file_csv = os.path.join(os.path.join(os.path.dirname(__file__), "test"), "USDJPYH1.csv")
test_file_json = os.path.join(os.path.join(os.path.dirname(__file__), "test"), "USDJPYH1.json")

config = {
    "detect": {
        "input": None,
        "output": None,
        "ext": "json",
        "show_graph": False,
        "window": 1,
        "threshold": 0.5,
        "candidate_resistance_band_names": [
            "^ichimoku_senkou_span_[12]$",
            "^sma-[1-9][0-9]+?$"
        ]
    }
}

class MockArgs:
    def __init__(self):
        self.input = None
        self.output = None
        self.ext = None
        self.show_graph = False
        self.window = None
        self.threshold = None

def check_output(output_file: Path):
    if output_file.suffix == ".json":
        df = pd.read_json(output_file)
    elif output_file.suffix == ".csv":
        df = pd.read_csv(output_file)
    assert len(df.columns) == 39
    assert "datetime" in df.columns
    assert "open" in df.columns
    assert "high" in df.columns
    assert "low" in df.columns
    assert "close" in df.columns
    assert "tick" in df.columns
    assert "volume" in df.columns
    assert "zigzag" in df.columns
    assert "zigzag-kind" in df.columns
    assert "zigzag-from" in df.columns
    assert "zigzag-velocity" in df.columns
    assert "zigzag-delta" in df.columns
    assert "zigzag-peak-price" in df.columns
    assert "zigzag-bottom-price" in df.columns
    assert "ichimoku_kijun_sen" in df.columns
    assert "ichimoku_tenkan_sen" in df.columns
    assert "ichimoku_senkou_span_1" in df.columns
    assert "ichimoku_senkou_span_2" in df.columns
    assert "ichimoku_chikou_span" in df.columns
    assert "sma-20" in df.columns
    assert "sma-25" in df.columns
    assert "sma-50" in df.columns
    assert "sma-75" in df.columns
    assert "sma-100" in df.columns
    assert "reflection" in df.columns
    assert "reflection-from-sma-20" in df.columns
    assert "reflection-from-sma-25" in df.columns
    assert "reflection-from-sma-50" in df.columns
    assert "reflection-from-sma-75" in df.columns
    assert "reflection-from-sma-100" in df.columns
    assert "reflection-from-ichimoku_senkou_span_1" in df.columns
    assert "reflection-from-ichimoku_senkou_span_2" in df.columns
    assert "breakout" in df.columns
    assert "breakout-top" in df.columns
    assert "breakout-top-rate" in df.columns
    assert "breakout-top-dist" in df.columns
    assert "breakout-bottom" in df.columns
    assert "breakout-bottom-rate" in df.columns
    assert "breakout-bottom-dist" in df.columns

def test_Detector_main_out_json(tmp_path):
    output_file = tmp_path / "USDJPYH1.json"
    args = MockArgs()
    args.input = test_folder
    args.ext = "json"
    args.output = tmp_path
    Detector(config).main(args)

    assert os.path.exists(output_file)

    # 出力ファイルの内容確認
    check_output(output_file)

def test_Detector_main_out_csv(tmp_path):
    output_file = tmp_path / "USDJPYH1.csv"
    args = MockArgs()
    args.input = test_folder
    args.ext = "csv"
    args.output = tmp_path
    Detector(config).main(args)

    assert os.path.exists(output_file)

    # 出力ファイルの内容確認
    check_output(output_file)

def test_Detector_main_input_folder(tmp_path):
    output_file = tmp_path / "USDJPYH1.csv"
    args = MockArgs()
    args.input = test_folder
    args.ext = "csv"
    args.output = tmp_path
    Detector(config).main(args)

    assert os.path.exists(output_file)

    # 出力ファイルの内容確認
    check_output(output_file)

def test_Detector_main_input_file_csv(tmp_path):
    output_file = tmp_path / "USDJPYH1.csv"
    args = MockArgs()
    args.input = test_file_csv
    args.ext = "csv"
    args.output = tmp_path
    Detector(config).main(args)

    assert os.path.exists(output_file)

    # 出力ファイルの内容確認
    check_output(output_file)

def test_Detector_main_input_file_json(tmp_path):
    output_file = tmp_path / "USDJPYH1.csv"
    args = MockArgs()
    args.input = test_file_json
    args.ext = "csv"
    args.output = tmp_path
    Detector(config).main(args)

    assert os.path.exists(output_file)

    # 出力ファイルの内容確認
    check_output(output_file)