"""前回高値・安値更新検知モジュール"""

from pandas import DataFrame


def mark_breakout(df: DataFrame) -> DataFrame:
    # ジグザグのマーク化された箇所を収集する
    zigzag_indices = df.index[df["zigzag"]].tolist() if "zigzag" in df.columns else []

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
    return df