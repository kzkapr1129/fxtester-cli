"""解析モジュール
"""

from pathlib import Path
from common.zigzag import mark_zigzag
from common.sma import mark_sma
import common.graph as g
import pandas as pd
import json


class Analyzer:
    """解析クラス

    ローソク足配列を解析し検査に有用なデータを抽出または作成を行い結果を出力する

    Attributes:
        config (dict[str,Any]): 設定情報が格納された辞書データ
    """

    def __init__(self, config):
        """コンストラクタ

        Args:
            config (dict[str,Any]): 設定情報が格納された辞書データ
        """
        self.config = config

    def main(self, input_path: Path, output_path: str, show_graph: bool, csv_encoding: str = "utf-16le"):
        """メイン処理

        解析処理のメインとなる処理を実行する
        """
        # ファイル直接指定かフォルダ指定かチェックする
        if input_path.is_file():
            # ファイルが直接指定された場合
            file_list = [input_path]
        else:
            # フォルダが指定された場合
            file_list = [file for file in input_path.glob(
                "*.csv") if file.is_file()]

        json_array = []
        # 入力ファイル(.csv)の読み込み
        for file in file_list:
            df = pd.read_csv(file, parse_dates=["datetime"], dayfirst=False, encoding=csv_encoding, names=[
                             "datetime", "open", "high", "low", "close", "tick", "volume"])
            # ジグザグを計算する
            mark_zigzag(df)
            # 単純移動平均線を計算する
            mark_sma(df)

            if show_graph:
                g.show(df, title=file.name)

            json_array.append(json.loads(df.to_json(
                orient="records", date_format="iso", date_unit="s")))

        with open(output_path, mode='w') as f:
            # 解析結果の出力
            f.write(json.dumps(json_array, indent=4, ensure_ascii=False))
