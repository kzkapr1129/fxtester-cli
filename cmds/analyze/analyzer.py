"""抽出モジュール
"""

from pathlib import Path
from common.zigzag import mark_zigzag2
from common.sma import mark_sma
from common.ichimoku import mark_ichimoku
import common.graph as g
import pandas as pd


class Analyzer:
    """解析クラス

    入力されたローソク足から抵抗帯を検出する

    Attributes:
        config (dict[str,Any]): 設定情報が格納された辞書データ
    """

    def __init__(self, config):
        """コンストラクタ

        Args:
            config (dict[str,Any]): 設定情報が格納された辞書データ
        """
        self.config = config

    def main(self, args):
        """メイン処理

        抽出処理のメインとなる処理を実行する
        """

        # 入力ファイルパスの取得
        input_path = Path(args.input) if args.input != None else Path(self.config["analyze"]["input"])
        # 出力ファイルパスの取得
        output_path = args.output if args.output != None else self.config["analyze"]["output"]
        # 出力ファイルの拡張子取得
        output_ext = args.ext if args.ext != None else self.config["analyze"]["ext"]
        # グラフ表示の可否取得
        show_graph = args.show_graph if args.show_graph else bool(self.config["analyze"]["show_graph"])
        # SMAの数値取得
        sma = args.sma if args.sma != None else self.config["analyze"]["sma"]
        # 一目均衡表の可否取得
        enable_ichimoku = args.ichimoku if args.ichimoku else bool(self.config["analyze"]["ichimoku"])
        # ジグザグの可否取得
        enable_zigzag = args.zigzag if args.zigzag else bool(self.config["analyze"]["zigzag"])
        # 入力CSVファイルのエンコーディング
        csv_encoding = "utf-16le"

        # ファイル直接指定かフォルダ指定かチェックする
        if input_path.is_file():
            # ファイルが直接指定された場合
            file_list = [input_path]
        else:
            # フォルダが指定された場合
            file_list = [file for file in input_path.glob("*.csv") if file.is_file()]

        # 入力ファイル(.csv)の読み込み
        for file in file_list:
            df = pd.read_csv(file, parse_dates=["datetime"], dayfirst=False, encoding=csv_encoding, names=[
                             "datetime", "open", "high", "low", "close", "tick", "volume"])
            # ジグザグを計算する
            if enable_zigzag:
                mark_zigzag2(df)
            # 単純移動平均線を計算する
            mark_sma(df, sma)
            # 一目均衡表を計算する
            if enable_ichimoku:
                mark_ichimoku(df)

            if show_graph:
                g.show(df, title=file.name)

            if output_path:
                data = []
                if output_ext == "json":
                    data = df.to_json(orient="records",
                                      date_format="iso", date_unit="s", indent=4)
                elif output_ext == "csv":
                    data = df.to_csv(index=True, index_label="index")
                output_full_path = output_path / \
                    Path(file.stem + f".{output_ext}")
                output_full_path.parent.mkdir(parents=True, exist_ok=True)
                with open(output_full_path, mode='w') as f:
                    # 抽出結果の出力
                    f.write(data)
