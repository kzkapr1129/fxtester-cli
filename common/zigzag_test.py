from zigzag import mark_zigzag, mark_zigzag_bottom_to_peak, mark_zigzag_peak_to_bottom
import pandas as pd
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
test_data_path = f"{current_dir}/test/USDJPYDaily.csv"


def test_mark_zigzag():
    test_data_expect = [
        0, 2, 5, 6, 9, 11, 14, 15, 17, 18, 22,
        24, 25, 30, 33, 34, 42, 43, 50, 58, 62,
        66, 67, 83, 89, 95, 97, 103, 105, 106,
        111, 115, 116, 123, 125, 131, 133, 136,
        138, 140, 142, 143, 155, 157, 159, 162,
        171, 174, 179, 180, 185, 189, 190, 192,
        194, 198, 200, 201, 203, 207, 208,
        215, 220, 221, 224, 228, 229, 231
    ]
    df = mark_zigzag(pd.read_csv(test_data_path, parse_dates=["datetime"], dayfirst=False, encoding="utf-16le", names=[
        "datetime", "open", "high", "low", "close", "volume", "tick"]))
    assert test_data_expect == df[df['zigzag']].index.tolist()


def test_mark_zigzag_bottom_to_peak():
    test_data_expect = [
        0, 5, 9, 14, 17, 22, 25, 33, 43,
        50, 62, 67, 89, 97, 105, 111, 116,
        125, 133, 138, 142, 155, 159, 171,
        179, 185, 190, 194, 200, 203, 208,
        220, 224, 229
    ]
    df = pd.read_csv(test_data_path, parse_dates=["datetime"], dayfirst=False, encoding="utf-16le", names=[
        "datetime", "open", "high", "low", "close", "volume", "tick"])
    df['zigzag'] = False
    mark_zigzag_bottom_to_peak(df)
    assert test_data_expect == df[df['zigzag']].index.tolist()


def test_mark_zigzag_peak_to_bottom():
    test_data_expect = [
        2, 6, 11, 15, 18, 24, 30, 34, 42, 58,
        66, 83, 95, 103, 106, 115, 123, 131,
        136, 140, 143, 157, 162, 174, 180, 189,
        192, 198, 201, 207, 215, 221, 228, 231,
    ]
    df = pd.read_csv(test_data_path, parse_dates=["datetime"], dayfirst=False, encoding="utf-16le", names=[
        "datetime", "open", "high", "low", "close", "volume", "tick"])
    df['zigzag'] = False
    mark_zigzag_peak_to_bottom(df)
    assert test_data_expect == df[df['zigzag']].index.tolist()
