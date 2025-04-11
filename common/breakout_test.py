from pandas import DataFrame
from zigzag import mark_zigzag2
from breakout import mark_breakout
import numpy as np
import pandas as pd

def equals_nan_array(array1, array2) -> bool:
    return pd.Series(array1).equals(pd.Series(array2))

def test_mark_breakout():

    # ローソク足の包含関係なし && 全て陽線
    df = DataFrame(
        {
            "open": [5, 4, 3, 2, 3, 4, 3, 2, 1, 2, 3, 4, 5, 4],
            "close": [4, 3, 2, 1, 2, 3, 2, 1, 0, 1, 2, 3, 4, 3],
        }
    )
    mark_zigzag2(df)
    mark_breakout(df)

    assert df.index[pd.notna(df["origin-down"])].to_list() == [5]
    assert df.index[pd.notna(df["origin-up"])].to_list() == [8]
    assert equals_nan_array(df["origin-up-rate"].to_list(), [np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, 1.25, np.nan, np.nan, np.nan, np.nan, np.nan])
    assert equals_nan_array(df["origin-up-dist"].to_list(), [np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, 5.0, np.nan, np.nan, np.nan, np.nan, np.nan])
    assert equals_nan_array(df["origin-down-rate"].to_list(), [np.nan, np.nan, np.nan, np.nan, np.nan, 1.3333333333333333, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan])
    assert equals_nan_array(df["origin-down-dist"].to_list(), [np.nan, np.nan, np.nan, np.nan, np.nan, 4.0, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan])

