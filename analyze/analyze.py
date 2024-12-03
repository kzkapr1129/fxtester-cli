"""解析モジュール
"""

from pathlib import Path
from common.zigzag import mark_zigzag
import pandas as pd
import json


class Analyzer:
    """解析クラス

    ローソク足配列を解析し検査に有用なデータを抽出または作成を行い結果を出力する

    Attributes:
        config (dict[str,Any]): 設定情報が格納された辞書データ
        csv_data_path (str): 入力ファイルが格納されたフォルダへのパス
        csv_encoding (str): csvファイルのエンコーディング
    """

    def __init__(self, config):
        """コンストラクタ

        Args:
            config (dict[str,Any]): 設定情報が格納された辞書データ
        """
        self.config = config
        self.csv_data_path = Path(self.config['analyze']['csv_data_path'])
        self.csv_encoding = self.config['analyze']['csv_encoding']

    def main(self):
        """メイン処理

        解析処理のメインとなる処理を実行する
        """
        json_array = []
        # 入力ファイル(.csv)の読み込み
        file_list = [file for file in self.csv_data_path.glob(
            "*.csv") if file.is_file()]
        for file in file_list:
            df = pd.read_csv(file, parse_dates=["datetime"], dayfirst=False, encoding=self.csv_encoding, names=[
                             "datetime", "open", "high", "low", "close", "volume", "tick"])
            # ジグザグを計算する
            mark_zigzag(df)
            json_array.append(json.loads(df.to_json(orient="records")))

        # 解析結果の出力
        final_json = json.dumps(json_array, indent=4, ensure_ascii=False)
        print(final_json)

