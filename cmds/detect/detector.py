"""検出モジュール"""

from pathlib import Path
import common.graph as g
import pandas as pd
import re
import logging
from itertools import chain

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

            # ジグザグのマーク化された箇所を収集する
            zigzag_indices = df.index[df["zigzag"]].tolist() if "zigzag" in df.columns else []

            # 抵抗帯ポイント列の初期化
            df["resistance-point"] = False

            # 抵抗帯として認識されたインジケータを検出する
            # ジグザグマークの箇所をループ
            for zigzag_idx in zigzag_indices:

                # 抵抗帯ごとにループ
                for target_resistance_band_name in target_resistance_band_names:

                    found = False

                    over_area = 0  # 抵抗帯より上の実体面積
                    under_area = 0  # 抵抗帯より下の実体面積
                    over_count = 0  # 抵抗帯より実体が上にある数
                    under_count = 0  # 抵抗帯より実体が下にある数
                    count_overlap = 0  # 高値から安値の間で抵抗帯が存在しているローソク足の数

                    inspect_start = max(0, zigzag_idx - window_size)
                    inspect_end = min(len(df), zigzag_idx + window_size + 1)
                    inspect_rows = df.iloc[inspect_start:inspect_end]

                    for _, inspect_row in inspect_rows.iterrows():
                        resistant_band_price = inspect_row[target_resistance_band_name]
                        if pd.isna(resistant_band_price):
                            continue

                        high_price = inspect_row["high"]
                        low_price = inspect_row["low"]
                        if low_price <= resistant_band_price and resistant_band_price <= high_price:
                            # 高値から安値の間で抵抗帯が含まれている場合
                            count_overlap += 1

                        open_price = inspect_row["open"]
                        close_price = inspect_row["close"]
                        max_body = max(open_price, close_price)
                        min_body = min(open_price, close_price)

                        if min_body <= resistant_band_price and resistant_band_price <= max_body:
                            # 実体の中に抵抗帯が存在している場合 (実体の一部を合算)
                            over_area += max_body - resistant_band_price
                            under_area += resistant_band_price - min_body
                        elif max_body < resistant_band_price:
                            # 抵抗帯より下に実体がある (実体を全て合算)
                            under_area += max_body - min_body
                            under_count += 1
                        elif resistant_band_price < min_body:
                            # 抵抗帯より上に実体がある (実体を全て合算)
                            over_area += max_body - min_body
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
                        df.loc[zigzag_idx, "resistance-point"] = True
                        df.loc[zigzag_idx, f"resistance-point-{target_resistance_band_name}"] = df.loc[zigzag_idx, target_resistance_band_name]

            lastPeak = None
            lastBottom = None
            # 高値・安値更新が行われたジグザグの起点を検出する
            for zigzag_idx in zigzag_indices:
                row = df.iloc[zigzag_idx]
                kind = row["zigzag-kind"]
                if kind == "peak":
                    bodyMax = max(row["open"], row["close"])
                    if lastPeak is not None:
                        lastPeakBodyMax = max(df.loc[lastPeak, "open"], df.loc[lastPeak, "close"])
                        if lastPeakBodyMax < bodyMax and lastBottom is not None:
                            df.loc[lastBottom, "origin-up"] = min(df.loc[lastBottom, "open"], df.loc[lastBottom, "close"])
                            # 前回高値と今の高値の比率を求める
                            origin = min(df.loc[lastBottom, "open"], df.loc[lastBottom, "close"])
                            pre = max(df.loc[lastPeak, "open"], df.loc[lastPeak, "close"])
                            dist = bodyMax - origin
                            update_rate = dist / (pre - origin)
                            df.loc[lastBottom, "origin-up-rate"] = update_rate
                            df.loc[lastBottom, "origin-up-dist"] = dist

                    lastPeak = zigzag_idx
                elif kind == "bottom":
                    bodyMin = min(row["open"], row["close"])
                    if lastBottom is not None:
                        lastBottomBodyMin = min(df.loc[lastBottom, "open"], df.loc[lastBottom, "close"])
                        if bodyMin < lastBottomBodyMin and lastPeak is not None:
                            df.loc[lastPeak, "origin-down"] = max(df.loc[lastPeak, "open"], df.loc[lastPeak, "close"])
                            # 前回高値と今の高値の比率を求める
                            origin = max(df.loc[lastPeak, "open"], df.loc[lastPeak, "close"])
                            pre = min(df.loc[lastBottom, "open"], df.loc[lastBottom, "close"])
                            dist = origin - bodyMin
                            update_rate = dist / (origin - pre)
                            df.loc[lastPeak, "origin-down-rate"] = update_rate
                            df.loc[lastPeak, "origin-down-dist"] = dist
                    lastBottom = zigzag_idx

            if show_graph:
                g.show(df, title=file.name)

            if output_path:
                data = []
                if output_ext == "json":
                    data = df.to_json(orient="records", date_format="iso", date_unit="s", indent=4)
                elif output_ext == "csv":
                    data = df.to_csv(index=True, index_label="index")
                output_full_path = Path(output_path) / Path(file.stem + f".{output_ext}")
                output_full_path.parent.mkdir(parents=True, exist_ok=True)
                with open(output_full_path, mode="w") as f:
                    # 抽出結果の出力
                    f.write(data)
