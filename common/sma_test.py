from sma import mark_sma
import pandas as pd
from pandas import DataFrame
import numpy as np

def equals_nan_array(array1, array2) -> bool:
    return pd.Series(array1).equals(pd.Series(array2))

def test_mark_sma():
    # 空のDataFrame
    df = DataFrame()
    df = mark_sma(df, [])
    assert len(df) == 0
    assert len(df.columns) == 0

    # 空のDataFrame
    df = DataFrame()
    df = mark_sma(df, [2])
    assert len(df) == 0
    assert len(df.columns) == 0

    # SMA-2
    df = DataFrame(
        {
            "close": [5, 4, 3, 2, 3, 4, 3, 2, 1, 2, 3, 4, 5, 4]
        }
    )
    df = mark_sma(df, [2])
    assert len(df) == 14
    assert len(df.columns) == 2 and "sma-2" in df.columns
    assert equals_nan_array(df["sma-2"].to_list(), [np.nan, 4.5, 3.5, 2.5, 2.5, 3.5, 3.5, 2.5, 1.5, 1.5, 2.5, 3.5, 4.5, 4.5])

    # SMA-2, SMA-4
    df = DataFrame(
        {
            "close": [5, 4, 3, 2, 3, 4, 3, 2, 1, 2, 3, 4, 5, 4]
        }
    )
    df = mark_sma(df, [2, 4])
    assert len(df) == 14
    assert len(df.columns) == 3 and "sma-2" in df.columns and "sma-4" in df.columns
    assert equals_nan_array(df["sma-2"].to_list(), [np.nan, 4.5, 3.5, 2.5, 2.5, 3.5, 3.5, 2.5, 1.5, 1.5, 2.5, 3.5, 4.5, 4.5])
    assert equals_nan_array(df["sma-4"].to_list(), [np.nan, np.nan, np.nan, 3.5, 3.0, 3.0, 3.0, 3.0, 2.5, 2.0, 2.0, 2.5, 3.5, 4.0])

