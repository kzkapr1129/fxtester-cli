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
        res = re.findall('^sma-(\d+)$', column)
        if 0 < len(res):
            sma.append(*res)

    apds = []

    # 単純移動平均線のマーカー追加
    for i, s in enumerate(sma if sma is not None else []):
        color = sma_colors[i % len(sma_colors)]
        apds.append(mpf.make_addplot(
            dfc[f'sma-{s}'], color=color, label=f'SMA {s}'))

    if "ichimoku_senkou_span_1" in df.columns:
        apds.append(mpf.make_addplot(
            dfc['ichimoku_senkou_span_1'], color='sandybrown', label='先行スパン1'))
    if "ichimoku_senkou_span_2" in df.columns:
        apds.append(mpf.make_addplot(
            dfc['ichimoku_senkou_span_2'], color='thistle', label='先行スパン2'))

    zigzag_inputs = [
        {"name": 'zigzag-peak-price', "marker": "v", "color": 'red'},
        {"name": 'zigzag-bottom-price', "marker": "^", "color": 'blue'}
    ]

    # ジグザグのマーカーを追加
    for zi in zigzag_inputs:
        if zi["name"] in df.columns:
            zigzag_prices = df[zi["name"]]
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
