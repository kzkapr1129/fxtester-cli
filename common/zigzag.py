from pandas import DataFrame
from pandas import Series
import json


def mark_zigzag(df: DataFrame):
    df['zigzag'] = None
    mark_zigzag_peak_to_bottom(df)
    mark_zigzag_bottom_to_peak(df)
    return df


def mark_zigzag_peak_to_bottom(df):
    row_index = 0
    while row_index < len(df):
        # 高値更新が止まった場所を探す
        peak = find_peak(df, row_index)
        # 安値更新が止まった場所を探す
        bottom = find_bottom(df, peak['start'])

        if bottom['index'] <= peak['index']:
            # グラフが高値更新しかしていない場合、`peakIndex == bottomIndex`となる可能性がある。
            # この場合は検出なしとして処理する
            break

        # 経過時間
        x = bottom['index'] - peak['index']
        # Y軸のΔ
        y = bottom['box_min'] - peak['box_max']
        # 速度を計算
        velocity = y / x

        df.loc[peak['index'], 'zigzag'] = json.dumps({
            "kind": "peak",
            "to": bottom['index'],
            "velocity": velocity,
            "delta": y,
        })

        row_index = bottom['index'] + 1


def mark_zigzag_bottom_to_peak(df):
    row_index = 0
    while row_index < len(df):
        # 安値更新が止まった場所を探す
        bottom = find_bottom(df, row_index)
        # 高値更新が止まった場所を探す
        peak = find_peak(df, bottom['start'])

        if peak['index'] <= bottom['index']:
            # グラフが安値更新しかしていない場合、`peakIndex == bottomIndex`となる可能性がある。
            # この場合は検出なしとして処理する
            break

        # 経過時間
        x = peak['index'] - bottom['index']
        # Y軸のΔ
        y = peak['box_max'] - bottom['box_min']
        # 速度を計算
        velocity = y / x

        df.loc[bottom['index'], 'zigzag'] = json.dumps({
            "kind": "bottom",
            "to": peak['index'],
            "velocity": velocity,
            "delta": y,
        })

        row_index = peak['index'] + 1


def find_peak(df: DataFrame, start: int) -> dict:
    if len(df) <= start:
        raise Exception("Program error")

    peak_index = start
    if len(df) <= peak_index + 1:
        return {
            "index": peak_index,
            "start": peak_index,
            "box_min": calc_box_min(df, peak_index),
            "box_max": calc_box_max(df, peak_index)
        }

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

    return {
        "index": peak_index,
        "start": last_index,
        "box_min": calc_box_min(df, peak_index),
        "box_max": calc_box_max(df, peak_index)
    }


def find_bottom(df: DataFrame, start: int) -> dict:
    if len(df) <= start:
        raise Exception("Program error")

    bottom_index = start
    if len(df) <= bottom_index + 1:
        return {
            "index": bottom_index,
            "start": bottom_index,
            "box_min": calc_box_min(df, bottom_index),
            "box_max": calc_box_max(df, bottom_index)
        }

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

    return {
        "index": bottom_index,
        "start": last_index,
        "box_min": calc_box_min(df, bottom_index),
        "box_max": calc_box_max(df, bottom_index)
    }


def calc_box_min(df, i):
    open = df.loc[i, 'open']
    close = df.loc[i, 'close']
    return min(open, close)


def calc_box_max(df, i):
    open = df.loc[i, 'open']
    close = df.loc[i, 'close']
    return max(open, close)


def is_updated_high(df, src_index, dst_index):
    return calc_box_max(df, src_index) < calc_box_max(df, dst_index)


def is_updated_low(df, src_index, dst_index):
    return calc_box_min(df, dst_index) < calc_box_min(df, src_index)


def is_positive(df, i):
    open = df.loc[i, 'open']
    close = df.loc[i, 'close']
    return open < close


def is_negative(df, i):
    open = df.loc[i, 'open']
    close = df.loc[i, 'close']
    return close < open


def contains(df, src_index, dst_index):
    return calc_box_min(df, src_index) <= calc_box_min(df, dst_index) and calc_box_max(df, dst_index) <= calc_box_max(df, src_index)
