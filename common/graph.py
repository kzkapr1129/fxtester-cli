"""グラフ表示モジュール"""

import mplfinance as mpf
from pandas import DataFrame
import pandas as pd
import japanize_matplotlib  # noqa: F401
import matplotlib.pyplot as plt
import re

sma_colors = ["steelblue", "mediumpurple", "brown", "bisque", "yellowgreen", "lime"]


def show(df: DataFrame, title: str = ""):
    dfc = df.copy()
    dfc["datetime"] = pd.to_datetime(dfc["datetime"])
    dfc = dfc.set_index("datetime")

    # カラム名からSMAの数値を取得する
    sma = []
    for column in dfc.columns:
        res = re.findall(r"^sma-(\d+)$", column)
        if 0 < len(res):
            sma.append(*res)

    # カラム名から抵抗帯を取得する
    resistance_points = []
    for column in dfc.columns:
        if re.match(r"^resistance-point-.+$", column):
            resistance_points.append(column)

    apds = []

    # 単純移動平均線のマーカー追加
    for i, s in enumerate(sma if sma is not None else []):
        color = sma_colors[i % len(sma_colors)]
        apds.append(mpf.make_addplot(dfc[f"sma-{s}"], color=color, label=f"SMA {s}"))

    if "ichimoku_senkou_span_1" in dfc.columns:
        apds.append(mpf.make_addplot(dfc["ichimoku_senkou_span_1"], color="sandybrown", label="先行スパン1"))
    if "ichimoku_senkou_span_2" in dfc.columns:
        apds.append(mpf.make_addplot(dfc["ichimoku_senkou_span_2"], color="thistle", label="先行スパン2"))

    zigzag_inputs = [
        {"name": "zigzag-peak-price", "marker": "v", "color": "red"},
        {"name": "zigzag-bottom-price", "marker": "^", "color": "blue"},
        {"name": "origin-down", "marker": "v", "color": "green"},
        {"name": "origin-up", "marker": "^", "color": "yellow"},
        *[{"name": name, "marker": "o", "color": "gold"} for name in resistance_points],
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
            apds.append(mpf.make_addplot(zigzag_prices, type="scatter", markersize=10, marker=zi["marker"], color=zi["color"]))

    s = mpf.make_mpf_style(
        # 基本はdefaultの設定値を使う。
        base_mpf_style="default",
        # font.family を matplotlibに設定されている値にする。
        rc={"font.family": plt.rcParams["font.family"][0]},
    )

    # 時刻の種類に応じてX軸の表示フォーマットを変更する
    datetime_format = "%Y/%m/%d"
    # MEMO: .dt.timeで時刻だけを抽出して00:00:00以外のデータが存在するかをクエリーする
    if 0 < len(df.query("datetime.dt.time != @pd.to_datetime('00:00:00').time()")):
        # 00時00分00秒以外のデータが存在している場合
        datetime_format = "%Y/%m/%d %H:%M:%S"

    mpf.plot(dfc, title=title, addplot=apds, type="candle", style=s, ylabel="Price", volume=False, datetime_format=datetime_format)
