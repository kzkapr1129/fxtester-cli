"""グラフ表示モジュール
"""
import mplfinance as mpf
from pandas import DataFrame
import pandas as pd

sma_colors=[
    'blue',
    'red',
    'green',
    'purple',
    'black',
    'cyan'
]

def show(df: DataFrame, sma: list[int]=[], title: str = ""):
    dfc = df.copy()
    dfc["datetime"] = pd.to_datetime(dfc["datetime"])
    dfc = dfc.set_index("datetime")

    apds = []
    for i, s in enumerate(sma):
        color = sma_colors[i % len(sma_colors)]
        apds.append(mpf.make_addplot(dfc[f'sma-{s}'], color=color, label=f'SMA {s}'))

    mpf.plot(dfc, title=title, addplot=apds, type="candle",
             style='yahoo', ylabel='Price', volume=False)
