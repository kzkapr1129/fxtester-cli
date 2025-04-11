"""抵抗帯反発検知モジュール"""

import pandas as pd
from pandas import DataFrame


def mark_reflection(df: DataFrame, target_resistance_band_names: list[str], window_size: int, threshold: float) -> DataFrame:
    # ジグザグのマーク化された箇所を収集する
    zigzag_indices = df.index[df["zigzag"]].tolist() if "zigzag" in df.columns else []

    # 抵抗帯ポイント列の初期化
    df["reflection"] = False

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
                df.loc[zigzag_idx, "reflection"] = True
                df.loc[zigzag_idx, f"reflection-from-{target_resistance_band_name}"] = df.loc[zigzag_idx, target_resistance_band_name]
    return df