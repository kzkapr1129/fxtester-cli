"""単純移動平均線計算モジュール"""

from pandas import DataFrame


def mark_sma(df: DataFrame, averages: list[int]) -> DataFrame:
    """単純移動平均線をデータフレームに書き込む

    Args:
        df (DataFrame): ローソク足の情報が格納されたデータフレーム

    Returns:
        DataFrame: 単純移動平均線が書き込まれたデータフレーム
    """
    if "close" not in df.columns:
        return df
    for average in averages if averages is not None else []:
        df[f"sma-{average}"] = df["close"].rolling(window=average, min_periods=average).mean()
    return df
