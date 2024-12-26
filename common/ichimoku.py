"""一目均衡表計算モジュール
"""

from pandas import DataFrame


def mark_ichimoku(df: DataFrame) -> DataFrame:
    # 基準線（赤線）＝（26日間の最高値+26日間の最安値）÷2
    # 転換線（青線）＝（9日間の最高値+9日間の最安値）÷2
    # 先行スパン1（水色線）＝（基準線+転換線）÷2を26日間先行させたもの
    # 先行スパン2（橙線）＝（52日間の最高値+52日間の最安値）÷2を26日間先行させたもの
    # 遅行スパン（黄色線）＝当日の終値を26日遅行させたもの

    tenkansen = 9
    kijunsen = 26
    senkou_span_b = 52

    dfc = df.copy()

    # 基準線（26日間の最高値 + 最安値）÷ 2
    dfc['26日間の最高値'] = df['high'].rolling(window=26).max()
    dfc['26日間の最安値'] = df['low'].rolling(window=26).min()
    df['ichimoku_kijun_sen'] = (dfc['26日間の最高値'] + dfc['26日間の最安値']) / 2

    # 転換線（9日間の最高値 + 最安値）÷ 2
    dfc['9日間の最高値'] = df['high'].rolling(window=9).max()
    dfc['9日間の最安値'] = df['low'].rolling(window=9).min()
    df['ichimoku_tenkan_sen'] = (dfc['9日間の最高値'] + dfc['9日間の最安値']) / 2

    # 先行スパン1（水色線）＝（基準線 + 転換線）÷ 2 を26日間先行
    df['ichimoku_senkou_span_1'] = (
        (df['ichimoku_kijun_sen'] + df['ichimoku_tenkan_sen']) / 2).shift(26)

    # 先行スパン2（橙線）＝（52日間の最高値 + 最安値）÷ 2 を26日間先行
    dfc['52日間の最高値'] = df['high'].rolling(window=52).max()
    dfc['52日間の最安値'] = df['low'].rolling(window=52).min()
    df['ichimoku_senkou_span_2'] = (
        (dfc['52日間の最高値'] + dfc['52日間の最安値']) / 2).shift(26)

    # 遅行スパン（黄色線）＝当日の終値を26日遅行
    df['ichimoku_chikou_span'] = df['close'].shift(-26)

    return df
