"""グラフ表示モジュール
"""
import mplfinance as mpf
from pandas import DataFrame
import pandas as pd
import japanize_matplotlib  # noqa: F401
import matplotlib.pyplot as plt
import re

sma_colors = [
    'blue',
    'red',
    'green',
    'purple',
    'black',
    'cyan'
]


def show(df: DataFrame, title: str = ""):
    dfc = df.copy()
    dfc["datetime"] = pd.to_datetime(dfc["datetime"])
    dfc = dfc.set_index("datetime")

    # カラム名からSMAの数値を取得する
    sma = []
    for column in dfc.columns:
        res = re.findall(r'^sma-(\d+)$', column)
        if 0 < len(res):
            sma.append(*res)

    # カラム名から抵抗帯を取得する
    resistance_points = []
    for column in dfc.columns:
        if re.match(r'^resistance-point-.+$', column):
            resistance_points.append(column)

    apds = []

    # 単純移動平均線のマーカー追加
    for i, s in enumerate(sma if sma is not None else []):
        color = sma_colors[i % len(sma_colors)]
        apds.append(mpf.make_addplot(
            dfc[f'sma-{s}'], color=color, label=f'SMA {s}'))

    if "ichimoku_senkou_span_1" in dfc.columns:
        apds.append(mpf.make_addplot(
            dfc['ichimoku_senkou_span_1'], color='sandybrown', label='先行スパン1'))
    if "ichimoku_senkou_span_2" in dfc.columns:
        apds.append(mpf.make_addplot(
            dfc['ichimoku_senkou_span_2'], color='thistle', label='先行スパン2'))

    zigzag_inputs = [
        {"name": 'zigzag-peak-price', "marker": "v", "color": 'red'},
        {"name": 'zigzag-bottom-price', "marker": "^", "color": 'blue'},
        {"name": 'zigzag-update', "marker": "o", "color": 'orange'},
        *[{"name": name, "marker": "o", "color": "gold"} for name in resistance_points]
    ]

    # ジグザグのマーカーを追加
    for zi in zigzag_inputs:
        if zi["name"] in dfc.columns:
            zigzag_prices = dfc[zi["name"]]
            if zigzag_prices.nunique() <= 1 or zigzag_prices.isna().all():
                # MEMO:
                # 空配列、または全てNaN,null,Noneのデータの場合。
                # このケースは配列を引数とするmax関数でエラーになるため、この段階で弾いておく。
                continue
            apds.append(mpf.make_addplot(zigzag_prices, type='scatter',
                        markersize=10, marker=zi["marker"], color=zi["color"]))

    s = mpf.make_mpf_style(
        # 基本はdefaultの設定値を使う。
        base_mpf_style='default',
        # font.family を matplotlibに設定されている値にする。
        rc={"font.family": plt.rcParams["font.family"][0]},
    )

    mpf.plot(dfc, title=title, addplot=apds, type="candle",
             style=s, ylabel='Price', volume=False)
