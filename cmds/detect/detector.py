"""検出モジュール"""

from pathlib import Path
import common.graph as g
import pandas as pd
import re
import logging
from itertools import chain
from common.reflection import mark_reflection
from common.breakout import mark_breakout

logger = logging.getLogger("detector")


class Detector:
    """検出クラス

    抵抗帯の情報を検出する

    Attributes:
        config (dict[str,Any]): 設定情報が格納された辞書データ
    """

    def __init__(self, config):
        self.config = config

    def main(self, args):

        # 入力ファイルパスの取得
        input_path = Path(args.input) if args.input is not None else Path(self.config["detect"]["input"])
        # 出力ファイルパスの取得
        output_path = args.output if args.output is not None else self.config["detect"]["output"]
        # 出力ファイルの拡張子取得
        output_ext = args.ext if args.ext is not None else self.config["detect"]["ext"]
        # グラフ表示の可否取得
        show_graph = args.show_graph if args.show_graph else bool(self.config["detect"]["show_graph"])
        # 抵抗帯判定用ウインドウサイズの取得
        window_size = args.window if args.window is not None else self.config["detect"]["window"]
        # 抵抗帯判定用の閾値取得
        threshold = args.threshold if args.threshold is not None else self.config["detect"]["threshold"]

        if window_size < 0:
            logger.error(f"invalid window size: {window_size}")
            return
        if threshold <= 0.0 or 1.0 < threshold:
            logger.error(f"invalid threshold: {threshold}")
            return

        # ファイル直接指定かフォルダ指定かチェックする
        if input_path.is_file():
            # ファイルが直接指定された場合
            file_list = [input_path]
        else:
            # フォルダが指定された場合
            file_list_json = [file for file in input_path.glob("*.json") if file.is_file()]
            file_list_csv = [file for file in input_path.glob("*.csv") if file.is_file()]
            file_list = chain(file_list_json, file_list_csv)

        # 抵抗帯名の一覧
        candidate_resistance_band_names = self.config["detect"]["candidate_resistance_band_names"]

        # 入力ファイル(.csv.json)の読み込み
        for file in file_list:
            df = pd.DataFrame()
            if file.suffix == ".json":
                df = pd.read_json(file)
            elif file.suffix == ".csv":
                df = pd.read_csv(file)

            # 抵抗帯名を収集する
            target_resistance_band_names = []
            for column in df.columns:
                for candidate_resistance_band_name in candidate_resistance_band_names:
                    if re.match(candidate_resistance_band_name, column):
                        target_resistance_band_names.append(column)

            # 抵抗帯反発の検出
            mark_reflection(df, target_resistance_band_names, window_size, threshold)

            # 前回高値、安値更新の検出
            mark_breakout(df)

            if show_graph:
                g.show(df, title=file.name)

            if output_path:
                data = []
                if output_ext == "json":
                    data = df.to_json(orient="records", date_format="iso", date_unit="s", indent=4)
                elif output_ext == "csv":
                    data = df.to_csv(index=False)
                output_full_path = Path(output_path) / Path(file.stem + f".{output_ext}")
                output_full_path.parent.mkdir(parents=True, exist_ok=True)
                with open(output_full_path, mode="w") as f:
                    # 抽出結果の出力
                    f.write(data)
