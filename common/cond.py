"""検索条件モジュール
"""

import re
import pandas as pd
from pandas import DataFrame
from error import BadCmdException


class Cond:
    """検索条件のベースクラス
    """

    def match(self, df: DataFrame, index: int) -> bool:
        return False


class CondEqual(Cond):
    """同値比較の検索条件クラス

    検索条件として、`a == b`式を評価する
    """

    def __init__(self, cmd: str):
        # コマンドが'XXX==YYY'の形式になっているかチェックする
        res = re.findall(r"^([^=<>\s]+)\s*==\s*([^=<>\s]+)$", cmd)
        if len(res) != 1:
            # 予期しない形式のコマンドが指定された場合
            raise BadCmdException(f"invalid command: {cmd}")
        self.column = res[0][0]
        self.value = res[0][1]

    def match(self, df: DataFrame, index: int) -> bool:
        if self.column not in df.columns:
            return False
        if len(df) <= index:
            return False
        return str(df.loc[index, self.column]) == self.value  # 文字列と数値の判別ができないため文字列として比較する

    def __repr__(self):
        class_name = self.__class__.__name__
        return f"{class_name}({self.column}=={self.value})"


class CondNotEqual(Cond):
    """非同値比較の検索条件クラス

    検索条件として、`a != b`式を評価する
    """

    def __init__(self, cmd: str):
        # コマンドが'XXX==YYY'の形式になっているかチェックする
        res = re.findall(r"^([^=<>\s]+)\s*!=\s*([^=<>\s]+)$", cmd)
        if len(res) != 1:
            # 予期しない形式のコマンドが指定された場合
            raise BadCmdException(f"invalid command: {cmd}")
        self.column = res[0][0]
        self.value = res[0][1]

    def match(self, df: DataFrame, index: int) -> bool:
        if self.column not in df.columns:
            return False
        if len(df) <= index:
            return False
        return str(df.loc[index, self.column]) != self.value  # 文字列と数値の判別ができないため文字列として比較する

    def __repr__(self):
        class_name = self.__class__.__name__
        return f"{class_name}({self.column}!={self.value})"


class CondFlag(Cond):
    """数値フラグの検索条件クラス

    検索条件として、指定列名の数値を評価する。

    評価方法
      - 0またはNone,null,NaNの場合はFalseを返却する
      - それ以外はTrueを返却する
    """

    def __init__(self, cmd: str):
        res = re.findall(r"^[^=<>]+$", cmd)
        if len(res) != 1:
            raise BadCmdException(f"invalid command: {cmd}")
        self.column = res[0]

    def match(self, df: DataFrame, index: int) -> bool:
        if self.column not in df.columns:
            return False
        if len(df) <= index:
            return False
        value = df.loc[index, self.column]
        if pd.isna(value):
            return False
        if value == 0 or str(value).lower() == "false":
            return False
        return True

    def __repr__(self):
        class_name = self.__class__.__name__
        return f"{class_name}({self.column})"


class CondAny(Cond):
    """全ての条件にマッチする検索条件クラス

    次の条件に一致するまで、全ての条件を一致として扱う。

    `{max_count}`修飾子が指定されている場合、max_count以内に次の条件が一致すれば条件にマッチしたとして扱う。
    """

    def __init__(self, cmd: str, next_cmd: Cond):
        self.cmd = cmd
        self.next_cmd = next_cmd
        if self.next_cmd is None:
            raise ValueError("next_cmd is None")
        res = re.findall(r"^\*\{(\d+)\}$", cmd)
        if len(res) != 1:
            raise BadCmdException(f"invalid command: {cmd}")
        self.max_count = int(res[0][0])
        if self.max_count <= 0:
            raise ValueError(f"invalid max_count: {self.max_count}")

    def match(self, df: DataFrame, index: int) -> bool:
        if len(df) <= index:
            return False
        is_next_matched = False
        for idx in range(index, index + self.max_count):
            is_next_matched = self.next_cmd.match(df, idx)
            if is_next_matched:
                break
        return is_next_matched

    def __repr__(self):
        class_name = self.__class__.__name__
        return f"{class_name}(*{{{self.max_count}}})"


class CondSet(Cond):
    """論理式で複数条件を結合する検索条件クラス

    and, or, ()が利用可能。
    """

    def __init__(self, cmd: str):
        if "*" in cmd:
            raise ValueError("'*' is not supported")

        # 前処理 (両端のスペース除去)
        cmd = cmd.strip()
        # 前処理 (==の前後のスペースを除去)
        cmd = re.sub(r"\s*==\s*", "==", cmd)
        # 前処理 (!=の前後のスペースを除去)
        cmd = re.sub(r"\s*!=\s*", "!=", cmd)

        # 文字列チェック (論理演算子で文字列が始まっていないかチェック)
        if cmd.startswith("and") or cmd.startswith("or"):
            raise BadCmdException(f"invalid cmd: {cmd}")
        # 文字列チェック (論理演算子で文字列が終わっていないかチェック)
        if cmd.endswith("and") or cmd.endswith("or"):
            raise BadCmdException(f"invalid cmd: {cmd}")

        # 論理式を分解する
        logical_exprs_pattern = r'\b(?!and\b)(?!or\b)[\w=\-:\!]+'
        logical_exprs = re.findall(logical_exprs_pattern, cmd)

        if len(logical_exprs) == 0:
            raise BadCmdException(f"invalid cmd: {cmd}")

        conds: list[Cond] = []
        for lexpr in logical_exprs:
            conds.append(make_cond(lexpr, None))  # *はサポートしないため、next_cmdは不要

        max_count = 100
        if max_count <= len(conds):
            raise BadCmdException(f"Too many conds: count={len(conds)}, max={max_count}")
        counter = iter(range(max_count))
        expr = re.sub(logical_exprs_pattern, lambda m: f"cond[{next(counter)}]", cmd)

        self.cmd = cmd
        self.conds = conds
        self.expr = expr

    def match(self, df: DataFrame, index: any) -> bool:
        cond = [cond.match(df, index) for cond in self.conds]  # noqa: F841 evalでcond変数を利用するため警告除外
        return eval(self.expr)

    def __repr__(self):
        class_name = self.__class__.__name__
        return f"{class_name}({self.conds}, expr='{self.expr}')"


def make_cond(cmd: str, next_cmd: Cond) -> Cond:
    """条件クラスを生成するファクトリー関数

    Args:
      cmd (str): 検索条件文字列
      next_cmd (Cond): 次に評価される検索条件クラス
    """
    if 0 < len(re.findall(r"\b(and|or)\b", cmd)):
        return CondSet(cmd)
    elif 1 == len(re.findall(r"^(?:[^=<>\s]+)\s*==\s*(?:[^=<>\s]+)$", cmd)):
        return CondEqual(cmd)
    elif 1 == len(re.findall(r"^(?:[^=<>\s]+)\s*!=\s*(?:[^=<>\s]+)$", cmd)):
        return CondNotEqual(cmd)
    elif 1 == len(re.findall(r"^\*(?:\{\d+\})*$", cmd)):
        return CondAny(cmd, next_cmd)
    elif 1 == len(re.findall(r"^[^=<>\{\}\*]+$", cmd)):
        return CondFlag(cmd)
    else:
        raise BadCmdException(f"\'{cmd}\'")


def make_conds(cmds: str) -> list[Cond]:
    """条件クラスを生成するファクトリー関数

    Args:
      cmd (str): `>`で連結された検索条件文字列
    """

    # 前処理 (==の前後のスペースを除去)
    cmds = re.sub(r"\s*==\s*", "==", cmds)
    # 前処理 (!=の前後のスペースを除去)
    cmds = re.sub(r"\s*!=\s*", "!=", cmds)

    conds: list[Cond] = []

    # '>'で文字列を分割する
    last_cond: Cond = None

    # 後ろの条件から条件クラスを生成する
    for cmd in reversed([cmd.strip() for cmd in cmds.split(">")]):
        cond = make_cond(cmd, last_cond)
        conds.append(cond)
        last_cond = cond

    # 条件クラスの一覧を逆順にする
    conds.reverse()

    return conds


def search_results_generator(df: DataFrame, cmds: str):
    # 検索条件オブジェクトの作成
    conds = make_conds(cmds)
    if len(conds) <= 0:
        raise BadCmdException(f"invalid cmd: {cmds}")

    # ジグザグフラグがTrueの箇所のインデックスを取得
    indexes = df.index[df['zigzag']].tolist()
    if len(indexes) <= 0:
        return

    # 先頭行から最終行にかけて条件に一致する行を探す
    for i, start_index in enumerate(indexes):
        # 条件と比較するインデックス一覧を取得
        match_target_indexes = indexes[i:i + len(conds)]

        # 比較対象の行数が残っているかを確認する
        if len(match_target_indexes) != len(conds):
            break

        # 全条件と比較対象行を比較する
        is_matched = False
        for k, match_target_index in enumerate(match_target_indexes):
            is_matched = conds[k].match(df, match_target_index)
            if not is_matched:
                break

        # 全条件に比較対象行がマッチしたか
        if not is_matched:
            # 条件にマッチしなかった場合
            continue

        yield (start_index, indexes[i + len(conds) - 1])
