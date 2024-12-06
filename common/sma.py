"""単純移動平均線計算モジュール
"""
from pandas import DataFrame


def mark_sma(df: DataFrame, average=25) -> DataFrame:
    """単純移動平均線をデータフレームに書き込む

    Args:
        df (DataFrame): ローソク足の情報が格納されたデータフレーム

    Returns:
        DataFrame: 単純移動平均線が書き込まれたデータフレーム
    """
    df['sma'] = df['close'].rolling(
        window=average, min_periods=average).mean()
    return df
