"""ジグザグ計算モジュール"""

from pandas import DataFrame
from typing import Any


def mark_zigzag2(df: DataFrame) -> DataFrame:
    """ジグザグ情報をデータフレームに書き込む
       v1との差分
       - ピークとボトムが交互にマーク付けされない不具合解消

    Args:
        df (DataFrame): ローソク足の情報が格納されたデータフレーム

    Returns:
        DataFrame: ジグザグ情報が書き込まれたデータフレーム
    """
    df["zigzag"] = False

    # ピークとボトムのどちらが最初に見つからるかをチェックする
    peak = find_peak(df, 0)
    bottom = find_bottom(df, 0)

    def mark_peak(peak, bottom):
        # 経過時間
        dx = peak["index"] - bottom["index"]
        # Y軸のΔ
        dy = peak["box_max"] - bottom["box_min"] if dx != 0 else 0
        # 速度を計算
        velocity = dy / dx if dx != 0 else 0
        # マーク付けを行うデータのインデックス取得
        i = peak["index"]
        # インデックスの位置にマーク付けを行う
        df.loc[i, "zigzag"] = True
        df.loc[i, "zigzag-kind"] = "peak"
        df.loc[i, "zigzag-from"] = bottom["index"]
        df.loc[i, "zigzag-velocity"] = velocity
        df.loc[i, "zigzag-delta"] = dy
        df.loc[i, "zigzag-peak-price"] = peak["box_max"]

    def mark_bottom(bottom, peak):
        # 経過時間
        dx = bottom["index"] - peak["index"]
        # Y軸のΔ
        dy = bottom["box_min"] - peak["box_max"] if dx != 0 else 0
        # 速度を計算
        velocity = dy / dx if dx != 0 else 0
        # マーク付けを行うデータのインデックス取得
        i = bottom["index"]
        # インデックスの位置にマーク付けを行う
        df.loc[i, "zigzag"] = True
        df.loc[i, "zigzag-kind"] = "bottom"
        df.loc[i, "zigzag-from"] = peak["index"]
        df.loc[i, "zigzag-velocity"] = velocity
        df.loc[i, "zigzag-delta"] = dy
        df.loc[i, "zigzag-bottom-price"] = bottom["box_min"]

    # 仮のジグザグを用意
    first = {
        "index": 0,
        "box_max": calc_box_max(df, 0),
        "box_min": calc_box_min(df, 0),
    }

    row_index = 0
    last_bottom = None
    # ボトムが最初に見つかったかチェックする
    if bottom["index"] < peak["index"]:
        row_index = bottom["start"]
        mark_bottom(bottom, first)  # インデックス0を仮のピークとする
        last_bottom = bottom
    else:
        # インデックス0を仮のボトムとする
        last_bottom = first

    # ピークとボトムを順番に探してマーク付けする
    while row_index + 1 < len(df):
        # ピークを探す
        peak = find_peak(df, row_index)
        # ボトムを探す
        bottom = find_bottom(df, peak["start"])

        # ピークとボトムのマーク付け
        mark_peak(peak, last_bottom)
        mark_bottom(bottom, peak)

        # 次の探索開始位置を設定
        row_index = bottom["start"]
        last_bottom = bottom

    return df


def find_peak(df: DataFrame, start: int) -> dict[str:Any]:
    """高値更新が止まったポイントを探す

    Args:
        df (DataFrame): ローソク足の情報が格納されたデータフレーム
        start (int): 検索を開始するローソク足のインデックス番号

    Returns:
        dict[str:Any]: 高値更新が止まったポイントの情報が格納された辞書データ
    """
    if len(df) <= start:
        raise Exception("Program error")

    peak_index = start
    if len(df) <= peak_index + 1:
        return {"index": peak_index, "start": peak_index, "box_min": calc_box_min(df, peak_index), "box_max": calc_box_max(df, peak_index)}

    last_index = peak_index
    for i in range(peak_index + 1, len(df)):
        last_index = i

        # 高値更新されているか確認
        if is_updated_high(df, peak_index, i):
            # 高値更新された場合
            peak_index = i
            continue

        prev = i - 1
        # ローソク足の包含関係を確認
        if contains(df, prev, i):
            # 前回のローソク足に包含されている場合
            continue
        elif is_updated_high(df, prev, i) and not is_updated_low(df, prev, i):
            # 前回のローソク足の高値を更新した場合 (peakの更新はなし、安値の更新はなし)
            continue
        elif is_updated_low(df, prev, i):
            # 前回のローソク足の安値を更新した場合
            if is_updated_high(df, prev, i):
                # 安値と高値(peakの更新はなし)両方更新した場合

                if is_positive(df, i):
                    # ローソク足が陽線の場合
                    continue  # 高値更新を優先する (処理継続)
                elif is_negative(df, i):
                    # ローソク足が陰線の場合
                    break  # 安値更新を優先する (処理終了)
                else:
                    # 十字線の場合
                    # プログラムのミスまたは検討不足な問題(包含関係ではないので十字線はあり得ない)
                    raise Exception("Program error")
            else:
                # 安値だけ更新した場合
                break
        else:
            # プログラムのミスまたは検討不足な問題(包含関係ではないので十字線はあり得ない)
            raise Exception("Program error")

    return {"index": peak_index, "start": last_index, "box_min": calc_box_min(df, peak_index), "box_max": calc_box_max(df, peak_index)}


def find_bottom(df: DataFrame, start: int) -> dict:
    """安値更新が止まったポイントを探す

    Args:
        df (DataFrame): ローソク足の情報が格納されたデータフレーム
        start (int): 検索を開始するローソク足のインデックス番号

    Returns:
        dict[str:Any]: 安値更新が止まったポイントの情報が格納された辞書データ
    """
    if len(df) <= start:
        raise Exception("Program error")

    bottom_index = start
    if len(df) <= bottom_index + 1:
        return {"index": bottom_index, "start": bottom_index, "box_min": calc_box_min(df, bottom_index), "box_max": calc_box_max(df, bottom_index)}

    last_index = bottom_index
    for i in range(bottom_index + 1, len(df)):
        last_index = i

        # 安値更新されているか確認
        if is_updated_low(df, bottom_index, i):
            # 安値更新された場合
            bottom_index = i
            continue

        prev = i - 1
        # ローソク足の包含関係を確認
        if contains(df, prev, i):
            # 前回のローソク足に包含されている場合
            continue
        elif is_updated_low(df, prev, i) and not is_updated_high(df, prev, i):
            # 前回のローソク足の安値を更新した場合 (bottomの更新はなし、高値の更新はなし)
            continue
        elif is_updated_high(df, prev, i):
            # 前回のローソク足の高値を更新した場合
            if is_updated_low(df, prev, i):
                # 高値と安値(bottomの更新はなし)両方更新した場合

                if is_negative(df, i):
                    # ローソク足が陰線の場合
                    continue  # 安値更新を優先する (処理継続)
                elif is_positive(df, i):
                    # ローソク足が陽線の場合
                    break  # 高値更新を優先する (処理終了)
                else:
                    # 十字線の場合
                    # プログラムのミスまたは検討不足な問題(包含関係ではないので十字線はあり得ない)
                    raise Exception("Program error")
            else:
                # 安値だけ更新した場合
                break
        else:
            # プログラムのミスまたは検討不足な問題(包含関係ではないので十字線はあり得ない)
            raise Exception("Program error")

    return {"index": bottom_index, "start": last_index, "box_min": calc_box_min(df, bottom_index), "box_max": calc_box_max(df, bottom_index)}


def calc_box_min(df, i) -> float:
    """ローソク足の実体の安値を計算する

    Args:
        df (DataFrame): ローソク足の情報が格納されたデータフレーム
        i (int): ローソク足のインデックス番号

    Returns:
        float: ローソク足の実体の安値
    """
    open = df.loc[i, "open"].astype(float)
    close = df.loc[i, "close"].astype(float)
    return min(open, close)


def calc_box_max(df, i) -> float:
    """ローソク足の実体の高値を計算する

    Args:
        df (DataFrame): ローソク足の情報が格納されたデータフレーム
        i (int): ローソク足のインデックス番号

    Returns:
        float: ローソク足の実体の高値
    """
    open = df.loc[i, "open"].astype(float)
    close = df.loc[i, "close"].astype(float)
    return max(open, close)


def is_updated_high(df, src_index, dst_index) -> bool:
    """高値更新が行われたかを検査する

    Args:
        df (DataFrame): ローソク足の情報が格納されたデータフレーム
        src (int): 過去のローソク足のインデックス番号
        dst (int): 未来のローソク足のインデックス番号

    Returns:
        bool: 高値更新が行われたか否かのフラグ値
    """
    return calc_box_max(df, src_index) < calc_box_max(df, dst_index)


def is_updated_low(df, src_index, dst_index):
    """安値更新が行われたかを検査する

    Args:
        df (DataFrame): ローソク足の情報が格納されたデータフレーム
        src (int): 過去のローソク足のインデックス番号
        dst (int): 未来のローソク足のインデックス番号

    Returns:
        bool: 安値更新が行われたか否かのフラグ値
    """
    return calc_box_min(df, dst_index) < calc_box_min(df, src_index)


def is_positive(df, i):
    """ローソク足が陽線か検査する

    Args:
        df (DataFrame): ローソク足の情報が格納されたデータフレーム
        i (int): ローソク足のインデックス番号

    Returns:
        bool: 陽線か否かのフラグ値
    """
    open = df.loc[i, "open"]
    close = df.loc[i, "close"]
    return open < close


def is_negative(df, i):
    """ローソク足が陰線か検査する

    Args:
        df (DataFrame): ローソク足の情報が格納されたデータフレーム
        i (int): ローソク足のインデックス番号

    Returns:
        bool: 陰線か否かのフラグ値
    """
    open = df.loc[i, "open"]
    close = df.loc[i, "close"]
    return close < open


def contains(df, src_index, dst_index):
    """未来のローソク足が過去のローソク足に包含されているか検査する

    Args:
        df (DataFrame): ローソク足の情報が格納されたデータフレーム
        src_index (int): 過去のローソク足のインデックス番号
        dst_index (int): 未来のローソク足のインデックス番号

    Returns:
        bool: 未来のローソク足が過去のローソク足に包含されているか否かのフラグ値
    """
    return calc_box_min(df, src_index) <= calc_box_min(df, dst_index) and calc_box_max(df, dst_index) <= calc_box_max(df, src_index)
