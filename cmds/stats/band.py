from pathlib import Path
from itertools import chain
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


class StatsBand:
    """ジグザグの変動幅を調べる

    抵抗帯の情報を検出する

    Attributes:
        config (dict[str,Any]): 設定情報が格納された辞書データ
    """

    def __init__(self, config):
        self.config = config

    def main(self, args):
        # 入力ファイルパスの取得
        input_path = Path(args.input)
        # 等級数の取得
        bins = args.bins

        # ファイル直接指定かフォルダ指定かチェックする
        if input_path.is_file():
            # ファイルが直接指定された場合
            file_list = [input_path]
        else:
            # フォルダが指定された場合
            file_list_json = [file for file in input_path.glob("*.json") if file.is_file()]
            file_list_csv = [file for file in input_path.glob("*.csv") if file.is_file()]
            file_list = chain(file_list_json, file_list_csv)

        for file in file_list:
            df = pd.DataFrame()
            print(file)
            if file.suffix == ".json":
                df = pd.read_json(file)
            elif file.suffix == ".csv":
                df = pd.read_csv(file, encoding="utf-8")

            df["zigzag-delta-abs"] = df["zigzag-delta"].abs()

            data = df.query("0 < `zigzag-delta-abs`").sort_values(by="zigzag-delta-abs", ascending=False)["zigzag-delta-abs"].to_numpy()
            bins = np.histogram_bin_edges(data, bins=bins)
            print(bins)
            labels = [f"{float(bins[i]):.3f}-{float(bins[i + 1]):.3f}" for i in range(len(bins) - 1)]
            categories = np.digitize(data, bins, right=True)
            counts = [np.sum(categories == i) for i in range(1, len(bins))]
            plt.figure(figsize=(6, 6))
            plt.pie(counts, labels=labels, autopct="%1.1f%%", startangle=140, colors=plt.cm.Paired.colors)
            plt.title("Data Distribution by Grade (Auto-generated bins)")
            plt.show()
