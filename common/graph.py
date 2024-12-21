"""グラフ表示モジュール
"""
import mplfinance as mpf
from pandas import DataFrame
import pandas as pd
import numpy as np

sma_colors = [
    'blue',
    'red',
    'green',
    'purple',
    'black',
    'cyan'
]


def show(df: DataFrame, sma: list[int] = [], title: str = ""):
    dfc = df.copy()
    dfc["datetime"] = pd.to_datetime(dfc["datetime"])
    dfc = dfc.set_index("datetime")

    apds = []

    # 単純移動平均線のマーカー追加
    for i, s in enumerate(sma if sma != None else []):
        color = sma_colors[i % len(sma_colors)]
        apds.append(mpf.make_addplot(
            dfc[f'sma-{s}'], color=color, label=f'SMA {s}'))

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

    mpf.plot(dfc, title=title, addplot=apds, type="candle",
             style='yahoo', ylabel='Price', volume=False)
