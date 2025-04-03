from zigzag import mark_zigzag2
from pandas import DataFrame
import pandas as pd
import numpy as np


def equals_nan_array(array1, array2) -> bool:
    return pd.Series(array1).equals(pd.Series(array2))


def test_mark_zigzag():
    # ローソク足の包含関係なし && 全て陽線
    df = DataFrame(
        {
            "open": [5, 4, 3, 2, 3, 4, 3, 2, 1, 2, 3, 4, 5, 4],
            "close": [4, 3, 2, 1, 2, 3, 2, 1, 0, 1, 2, 3, 4, 3],
        }
    )
    res = mark_zigzag2(df)
    assert res.index[res["zigzag"]].to_list() == [0, 3, 5, 8, 12, 13]
    assert res.index[res["zigzag-kind"] == "peak"].to_list() == [0, 5, 12]
    assert res.index[res["zigzag-kind"] == "bottom"].to_list() == [3, 8, 13]
    assert equals_nan_array(res["zigzag-from"].to_list(), [0.0, np.nan, np.nan, 0.0, np.nan, 3.0, np.nan, np.nan, 5.0, np.nan, np.nan, np.nan, 8.0, 12.0])
    assert equals_nan_array(res["zigzag-velocity"].to_list(), [0.0, np.nan, np.nan, -1.3333333333333333, np.nan, 1.500000, np.nan, np.nan, -1.3333333333333333, np.nan, np.nan, np.nan, 1.250000, -2.000000])
    assert equals_nan_array(res["zigzag-delta"].to_list(), [0.0, np.nan, np.nan, -4.0, np.nan, 3.0, np.nan, np.nan, -4.0, np.nan, np.nan, np.nan, 5.0, -2.0])
    assert equals_nan_array(res["zigzag-peak-price"].to_list(), [5.0, np.nan, np.nan, np.nan, np.nan, 4.0, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, 5.0, np.nan])
    assert equals_nan_array(res["zigzag-bottom-price"].to_list(), [np.nan, np.nan, np.nan, 1.0, np.nan, np.nan, np.nan, np.nan, 0.0, np.nan, np.nan, np.nan, np.nan, 3.0])

    # ローソク足の包含関係なし && 全て陰線
    df = DataFrame(
        {
            "open": [4, 3, 2, 1, 2, 3, 2, 1, 0, 1, 2, 3, 4, 3],
            "close": [5, 4, 3, 2, 3, 4, 3, 2, 1, 2, 3, 4, 5, 4],
        }
    )
    res = mark_zigzag2(df)
    assert res.index[res["zigzag"]].to_list() == [0, 3, 5, 8, 12, 13]
    assert res.index[res["zigzag-kind"] == "peak"].to_list() == [0, 5, 12]
    assert res.index[res["zigzag-kind"] == "bottom"].to_list() == [3, 8, 13]
    assert equals_nan_array(res["zigzag-from"].to_list(), [0.0, np.nan, np.nan, 0.0, np.nan, 3.0, np.nan, np.nan, 5.0, np.nan, np.nan, np.nan, 8.0, 12.0])
    assert equals_nan_array(res["zigzag-velocity"].to_list(), [0.0, np.nan, np.nan, -1.3333333333333333, np.nan, 1.500000, np.nan, np.nan, -1.3333333333333333, np.nan, np.nan, np.nan, 1.250000, -2.000000])
    assert equals_nan_array(res["zigzag-delta"].to_list(), [0.0, np.nan, np.nan, -4.0, np.nan, 3.0, np.nan, np.nan, -4.0, np.nan, np.nan, np.nan, 5.0, -2.0])
    assert equals_nan_array(res["zigzag-peak-price"].to_list(), [5.0, np.nan, np.nan, np.nan, np.nan, 4.0, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, 5.0, np.nan])
    assert equals_nan_array(res["zigzag-bottom-price"].to_list(), [np.nan, np.nan, np.nan, 1.0, np.nan, np.nan, np.nan, np.nan, 0.0, np.nan, np.nan, np.nan, np.nan, 3.0])

    # 右のローソク足が左のローソク足に包含 (高値更新、安値更新なし) && 陽線
    df = DataFrame(
        {
            "open": [5, 4, 3, 2, 1.5, 3, 4, 3, 2, 1, 2, 3, 4, 5, 4],
            "close": [4, 3, 2, 1, 1.3, 2, 3, 2, 1, 0, 1, 2, 3, 4, 3],
        }
    )
    res = mark_zigzag2(df)
    assert res.index[res["zigzag"]].to_list() == [0, 3, 6, 9, 13, 14]
    assert res.index[res["zigzag-kind"] == "peak"].to_list() == [0, 6, 13]
    assert res.index[res["zigzag-kind"] == "bottom"].to_list() == [3, 9, 14]

    # 右のローソク足が左のローソク足に包含 (高値更新、安値更新なし) && 陰線
    df = DataFrame(
        {
            "open": [5, 4, 3, 2, 1.3, 3, 4, 3, 2, 1, 2, 3, 4, 5, 4],
            "close": [4, 3, 2, 1, 1.5, 2, 3, 2, 1, 0, 1, 2, 3, 4, 3],
        }
    )
    res = mark_zigzag2(df)
    assert res.index[res["zigzag"]].to_list() == [0, 3, 6, 9, 13, 14]
    assert res.index[res["zigzag-kind"] == "peak"].to_list() == [0, 6, 13]
    assert res.index[res["zigzag-kind"] == "bottom"].to_list() == [3, 9, 14]

    # 左のローソク足が右のローソク足に包含 (高値更新・安値更新あり) && 陽線
    df = DataFrame(
        {
            "open": [5, 4, 3, 2, 2.1, 3, 4, 3, 2, 1, 2, 3, 4, 5, 4],
            "close": [4, 3, 2, 1, 0.9, 2, 3, 2, 1, 0, 1, 2, 3, 4, 3],
        }
    )
    res = mark_zigzag2(df)
    assert res.index[res["zigzag"]].to_list() == [0, 4, 6, 9, 13, 14]
    assert res.index[res["zigzag-kind"] == "peak"].to_list() == [0, 6, 13]
    assert res.index[res["zigzag-kind"] == "bottom"].to_list() == [4, 9, 14]

    # 左のローソク足が右のローソク足に包含 (高値更新・安値更新あり) && 陰線
    df = DataFrame(
        {
            "open": [5, 4, 3, 2, 0.9, 3, 4, 3, 2, 1, 2, 3, 4, 5, 4],
            "close": [4, 3, 2, 1, 2.1, 2, 3, 2, 1, 0, 1, 2, 3, 4, 3],
        }
    )
    res = mark_zigzag2(df)
    assert res.index[res["zigzag"]].to_list() == [0, 4, 6, 9, 13, 14]
    assert res.index[res["zigzag-kind"] == "peak"].to_list() == [0, 6, 13]
    assert res.index[res["zigzag-kind"] == "bottom"].to_list() == [4, 9, 14]

    # L194: ローソク足が陰線の場合
    df = DataFrame(
        {
            "open": [5, 4, 3, 2, 1.9, 1.8, 2, 3, 4, 3, 2, 1, 2, 3, 4, 5, 4],
            "close": [4, 3, 2, 1, 1.1, 1.2, 1, 2, 3, 2, 1, 0, 1, 2, 3, 4, 3],
        }
    )
    res = mark_zigzag2(df)
    assert res.index[res["zigzag"]].to_list() == [0, 3, 8, 11, 15, 16]

    # L197: ローソク足が陽線の場合
    df = DataFrame(
        {
            "open": [5, 4, 3, 2, 1.9, 1.8, 1, 3, 4, 3, 2, 1, 2, 3, 4, 5, 4],
            "close": [4, 3, 2, 1, 1.1, 1.2, 2, 2, 3, 2, 1, 0, 1, 2, 3, 4, 3],
        }
    )
    res = mark_zigzag2(df)
    assert res.index[res["zigzag"]].to_list() == [0, 3, 8, 11, 15, 16]

    # L186: 前回のローソク足の安値を更新した場合 (bottomの更新はなし、高値の更新はなし)
    df = DataFrame(
        {
            "open": [5, 4, 3, 2, 1.9, 1.8, 1.8, 1, 3, 4, 3, 2, 1, 2, 3, 4, 5, 4],
            "close": [4, 3, 2, 1, 1.1, 1.2, 1.1, 2, 2, 3, 2, 1, 0, 1, 2, 3, 4, 3],
        }
    )
    res = mark_zigzag2(df)
    assert res.index[res["zigzag"]].to_list() == [0, 3, 9, 12, 16, 17]
