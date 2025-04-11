from pandas import DataFrame
from common.zigzag import mark_zigzag2
from common.reflection import mark_reflection
import pandas as pd

def test_mark_reflection_bottom_reflection():
    df = DataFrame(
        {
            "high":  [5, 4, 3, 2, 3, 4, 3, 2, 1, 2, 3, 4, 5, 4],
            "open":  [5, 4, 3, 2, 3, 4, 3, 2, 1, 2, 3, 4, 5, 4],
            "close": [4, 3, 2, 1, 2, 3, 2, 1, 0, 1, 2, 3, 4, 3],
            "low":   [4, 3, 2, 1, 2, 3, 2, 1, 0, 1, 2, 3, 4, 3],
            "sma": [0.5 for _ in range(14)]
        }
    )
    mark_zigzag2(df)
    mark_reflection(df, ["sma"], 1, 0.5)

    assert df.index[df["reflection"]].to_list() == [8]
    assert df.index[pd.notna(df["reflection-from-sma"])].to_list() == [8]

def test_mark_reflection_top_reflection():
    df = DataFrame(
        {
            "high":  [5, 4, 3, 2, 3, 4, 3, 2, 1, 2, 3, 4, 5, 4],
            "open":  [5, 4, 3, 2, 3, 4, 3, 2, 1, 2, 3, 4, 5, 4],
            "close": [4, 3, 2, 1, 2, 3, 2, 1, 0, 1, 2, 3, 4, 3],
            "low":   [4, 3, 2, 1, 2, 3, 2, 1, 0, 1, 2, 3, 4, 3],
            "sma": [4.8 for _ in range(14)]
        }
    )
    mark_zigzag2(df)
    mark_reflection(df, ["sma"], 1, 0.5)

    assert df.index[df["reflection"]].to_list() == [0, 12]
    assert df.index[pd.notna(df["reflection-from-sma"])].to_list() == [0, 12]