"""グラフ表示モジュール
"""
import mplfinance as mpf
from pandas import DataFrame
import pandas as pd


def show(df: DataFrame, title: str = ""):
    dfc = df.copy()
    dfc["datetime"] = pd.to_datetime(dfc["datetime"])
    dfc = dfc.set_index("datetime")

    apds = [
        mpf.make_addplot(dfc['sma'], color='blue', label='SMA 3 days')
    ]

    mpf.plot(dfc, title=title, addplot=apds, type="candle",
             style='yahoo', ylabel='Price', volume=True)
