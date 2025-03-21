"""検出モジュール
"""

from pathlib import Path
import common.graph as g
import pandas as pd
import re
import math

class Detector:
    """検出クラス

    抵抗帯の情報を検出する

    Attributes:
        config (dict[str,Any]): 設定情報が格納された辞書データ
    """

    def __init__(self, config):
        self.config = config

    def main(self, input_path: Path, output_path: str, show_graph: bool, window_size: int, threshold: float=0.8):
        # ファイル直接指定かフォルダ指定かチェックする
        if input_path.is_file():
            # ファイルが直接指定された場合
            file_list = [input_path]
        else:
            # フォルダが指定された場合
            file_list = [file for file in input_path.glob(
                "*.csv.json") if file.is_file()]

        # 抵抗帯名の一覧
        candidate_resistance_band_names = self.config["detect"]["candidate_resistance_band_names"]

        # 入力ファイル(.csv.json)の読み込み
        for file in file_list:
            df=pd.read_json(file)

            # 抵抗帯名を収集する
            target_resistance_band_names = []
            for column in df.columns:
                for candidate_resistance_band_name in candidate_resistance_band_names:
                    if re.match(candidate_resistance_band_name, column):
                        target_resistance_band_names.append(column)

            # ジグザグのマーク化された箇所を収集する
            zigzag_indices = df.index[df['zigzag'] == True].tolist()

            # ジグザグマークの箇所をループ
            for zigzag_idx in zigzag_indices:

                # 抵抗帯ごとにループ
                for target_resistance_band_name in target_resistance_band_names:

                    found = False

                    over_area = 0   # 抵抗帯より上の実体面積
                    under_area = 0  # 抵抗帯より下の実体面積
                    over_count = 0  # 抵抗帯より実体が上にある数
                    under_count = 0 # 抵抗帯より実体が下にある数
                    count_overlap = 0 # 高値から安値の間で抵抗帯が存在しているローソク足の数

                    inspect_start = max(0, zigzag_idx - window_size)
                    inspect_end = min(len(df), zigzag_idx + window_size + 1)
                    inspect_rows = df.iloc[inspect_start:inspect_end]

                    for _, inspect_row in inspect_rows.iterrows():
                        resistant_band_price = inspect_row[target_resistance_band_name]
                        if pd.isna(resistant_band_price):
                            continue

                        high_price = inspect_row['high']
                        low_price = inspect_row['low']
                        if low_price <= resistant_band_price and resistant_band_price <= high_price:
                            # 高値から安値の間で抵抗帯が含まれている場合
                            count_overlap += 1

                        open_price = inspect_row['open']
                        close_price = inspect_row['close']
                        max_body = max(open_price, close_price)
                        min_body = min(open_price, close_price)

                        if min_body <= resistant_band_price and resistant_band_price <= max_body:
                            # 実体の中に抵抗帯が存在している場合 (実体の一部を合算)
                            over_area += (max_body - resistant_band_price)
                            under_area += (resistant_band_price - min_body)
                        elif max_body < resistant_band_price:
                            # 抵抗帯より下に実体がある (実体を全て合算)
                            under_area += (max_body - min_body)
                            under_count += 1
                        elif resistant_band_price < min_body:
                            # 抵抗帯より上に実体がある (実体を全て合算)
                            over_area += (max_body - min_body)
                            over_count += 1

                    all_area = over_area + under_area
                    if all_area == 0.0:
                        # 面積がない場合 (クロスの場合)
                        continue

                    zigzag_kind = df.loc[zigzag_idx, "zigzag-kind"]
                    if zigzag_kind == "peak" and threshold <= (under_area / all_area) and 1 <= count_overlap and 0 == over_count:
                        # 上に抵抗帯があり、抵抗帯より下に実体が多く存在している場合
                        found = True
                    elif zigzag_kind == "bottom" and threshold <= (over_area / all_area) and 1 <= count_overlap and 0 == under_count:
                        # 下に抵抗帯があり、抵抗帯より上に実体が多く存在している場合
                        found = True

                    if found:
                        # dataframeに抵抗帯をマーク
                        df.loc[zigzag_idx, f'resistance-point-{target_resistance_band_name}'] = df.loc[zigzag_idx, target_resistance_band_name]

            if show_graph:
                g.show(df)

            if output_path:
                json = df.to_json(orient="records", date_format="iso", date_unit="s", indent=4)
                output_full_path = Path(output_path) / Path(file.name + "_detect.json")
                output_full_path.parent.mkdir(parents=True, exist_ok=True)
                with open(output_full_path, mode='w') as f:
                    # 抽出結果の出力
                    f.write(json)


