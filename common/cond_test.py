"""検索条件モジュール
"""

# flake8: noqa

from pandas import DataFrame
from cond import make_conds, make_cond, CondEqual, CondNotEqual, CondFlag, CondAny, CondSet, search_results_generator
from error import BadCmdException
import pytest


def test_CondEqual_init():
    with pytest.raises(BadCmdException):
        CondEqual("")
    with pytest.raises(BadCmdException):
        CondEqual("param-1")
    with pytest.raises(BadCmdException):
        CondEqual("param-1=xx")
    with pytest.raises(BadCmdException):
        CondEqual("param-1!=xx")

    cond = CondEqual("param-1==data1")  # 例外がスローされないことを確認する
    assert cond.column == "param-1" and cond.value == "data1"  # 正規表現の抽出が正しく行われていることを確認する

    cond = CondEqual("param-1:abc==data2")  # 例外がスローされないことを確認する
    assert cond.column == "param-1:abc" and cond.value == "data2"  # 正規表現の抽出が正しく行われていることを確認する

    cond = CondEqual("param-1 == 123")  # 例外がスローされないことを確認する
    assert cond.column == "param-1" and cond.value == "123"  # 正規表現の抽出が正しく行われていることを確認する

    cond = CondEqual("param-1 == 123.5")  # 例外がスローされないことを確認する
    assert cond.column == "param-1" and cond.value == "123.5"  # 正規表現の抽出が正しく行われていることを確認する


def test_CondNotEqual_init():
    with pytest.raises(BadCmdException):
        CondNotEqual("")
    with pytest.raises(BadCmdException):
        CondNotEqual("param-1")
    with pytest.raises(BadCmdException):
        CondNotEqual("param-1=xx")
    with pytest.raises(BadCmdException):
        CondNotEqual("param-1==xx")

    cond = CondNotEqual("param-1!=data1")  # 例外がスローされないことを確認する
    assert cond.column == "param-1" and cond.value == "data1"  # 正規表現の抽出が正しく行われていることを確認する

    cond = CondNotEqual("param-1:abc!=data2")  # 例外がスローされないことを確認する
    assert cond.column == "param-1:abc" and cond.value == "data2"  # 正規表現の抽出が正しく行われていることを確認する

    cond = CondNotEqual("param-1 != 123")  # 例外がスローされないことを確認する
    assert cond.column == "param-1" and cond.value == "123"  # 正規表現の抽出が正しく行われていることを確認する

    cond = CondNotEqual("param-1 != 123.5")  # 例外がスローされないことを確認する
    assert cond.column == "param-1" and cond.value == "123.5"  # 正規表現の抽出が正しく行われていることを確認する


def test_CondFlag_init():
    with pytest.raises(BadCmdException):
        CondFlag("")
    with pytest.raises(BadCmdException):
        CondFlag("param-1==123")
    with pytest.raises(BadCmdException):
        CondFlag("param-1=123")
    with pytest.raises(BadCmdException):
        CondFlag("param-1<123")
    with pytest.raises(BadCmdException):
        CondFlag("param-1<=123")
    with pytest.raises(BadCmdException):
        CondFlag("param-1>123")
    with pytest.raises(BadCmdException):
        CondFlag("param-1>=123")

    CondFlag("param-1")


def test_CondAny_init():
    with pytest.raises(ValueError):
        CondAny("", None)
    with pytest.raises(BadCmdException):
        CondAny("", CondFlag("param-1"))
    with pytest.raises(BadCmdException):
        CondAny("*", CondFlag("param-1"))
    with pytest.raises(BadCmdException):
        CondAny("*{}", CondFlag("param-1"))
    with pytest.raises(ValueError):
        CondAny("*{0}", CondFlag("param-1"))
    with pytest.raises(BadCmdException):
        CondAny("*{-1}", CondFlag("param-1"))

    cond = CondAny("*{1}", CondFlag("param-1"))
    assert cond.max_count == 1


def test_CondSet_init():
    with pytest.raises(BadCmdException):
        CondSet("")
    with pytest.raises(BadCmdException):
        CondSet("param-1 == def and")
    with pytest.raises(BadCmdException):
        CondSet("param-1 == def or")
    with pytest.raises(BadCmdException):
        CondSet("and param-1 == def")
    with pytest.raises(BadCmdException):
        CondSet("or param-1 == def")
    with pytest.raises(BadCmdException):
        CondSet("param-1 == def and ")
    with pytest.raises(BadCmdException):
        CondSet("param-1 == def or ")
    with pytest.raises(BadCmdException):
        CondSet(" and param-1 == def")
    with pytest.raises(BadCmdException):
        CondSet(" or param-1 == def")
    with pytest.raises(ValueError):
        CondSet("*{1}")

    cond = CondSet("param-1==abc")
    assert isinstance(cond.conds[0], CondEqual)
    assert cond.expr == "cond[0]"
    assert cond.conds[0].column == "param-1" and cond.conds[0].value == "abc"

    cond = CondSet("param-1:abc == def and param-2:abc")
    assert isinstance(cond.conds[0], CondEqual)
    assert isinstance(cond.conds[1], CondFlag)
    assert cond.expr == "cond[0] and cond[1]"
    assert cond.conds[0].column == "param-1:abc" and cond.conds[0].value == "def"
    assert cond.conds[1].column == "param-2:abc"

    cond = CondSet("param-1:abc == def or param-2:abc")
    assert isinstance(cond.conds[0], CondEqual)
    assert isinstance(cond.conds[1], CondFlag)
    assert cond.expr == "cond[0] or cond[1]"
    assert cond.conds[0].column == "param-1:abc" and cond.conds[0].value == "def"
    assert cond.conds[1].column == "param-2:abc"

    cond = CondSet("param-1:abc == def and (param-2:abc or param-3:def == abc)")
    assert isinstance(cond.conds[0], CondEqual)
    assert isinstance(cond.conds[1], CondFlag)
    assert isinstance(cond.conds[2], CondEqual)
    assert cond.expr == "cond[0] and (cond[1] or cond[2])"
    assert cond.conds[0].column == "param-1:abc" and cond.conds[0].value == "def"
    assert cond.conds[1].column == "param-2:abc"
    assert cond.conds[2].column == "param-3:def" and cond.conds[2].value == "abc"

    cond = CondSet("param-1:abc == def and (param-2:abc or param-3:def == abc or param-4:ghi != edf or param-5)")
    assert isinstance(cond.conds[0], CondEqual)
    assert isinstance(cond.conds[1], CondFlag)
    assert isinstance(cond.conds[2], CondEqual)
    assert isinstance(cond.conds[3], CondNotEqual)
    assert isinstance(cond.conds[4], CondFlag)
    assert cond.expr == "cond[0] and (cond[1] or cond[2] or cond[3] or cond[4])"
    assert cond.conds[0].column == "param-1:abc" and cond.conds[0].value == "def"
    assert cond.conds[1].column == "param-2:abc"
    assert cond.conds[2].column == "param-3:def" and cond.conds[2].value == "abc"
    assert cond.conds[3].column == "param-4:ghi" and cond.conds[3].value == "edf"
    assert cond.conds[4].column == "param-5"


def test_CondEqual_match():
    df = DataFrame()
    assert not CondEqual("param-1==data1").match(df, 0)

    df = DataFrame({
        "param-1": []
    })
    assert not CondEqual("param-1==data1").match(df, 0)

    df = DataFrame({
        "param-1": ["data1"]
    })
    assert CondEqual("param-1==data1").match(df, 0)

    df = DataFrame({
        "param-1": ["data1", "data2"]
    })
    assert not CondEqual("param-1==data1").match(df, 1)

    df = DataFrame({
        "param-1": [1]
    })
    assert not CondEqual("param-1==data1").match(df, 0)

    df = DataFrame({
        "param-1": [1]
    })
    assert CondEqual("param-1==1").match(df, 0)

    df = DataFrame({
        "param-1": [True]
    })
    assert CondEqual("param-1==True").match(df, 0)


def test_CondNotEqual_match():
    df = DataFrame()
    assert not CondNotEqual("param-1!=data1").match(df, 0)

    df = DataFrame({
        "param-1": []
    })
    assert not CondNotEqual("param-1!=data1").match(df, 0)

    df = DataFrame({
        "param-1": ["data2"]
    })
    assert CondNotEqual("param-1!=data1").match(df, 0)

    df = DataFrame({
        "param-1": ["data1"]
    })
    assert not CondNotEqual("param-1!=data1").match(df, 0)

    df = DataFrame({
        "param-1": [1]
    })
    assert CondNotEqual("param-1!=2").match(df, 0)

    df = DataFrame({
        "param-1": [True]
    })
    assert CondNotEqual("param-1!=False").match(df, 0)


def test_CondFlag_match():
    df = DataFrame()
    assert not CondFlag("param-1").match(df, 0)

    df = DataFrame({
        "param-1": []
    })
    assert not CondFlag("param-1").match(df, 0)

    df = DataFrame({
        "param-1": [0]
    })
    assert not CondFlag("param-1").match(df, 0)

    df = DataFrame({
        "param-1": [0.0]
    })
    assert not CondFlag("param-1").match(df, 0)

    df = DataFrame({
        "param-1": [False]
    })
    assert not CondFlag("param-1").match(df, 0)

    df = DataFrame({
        "param-1": [144]
    })
    assert CondFlag("param-1").match(df, 0)

    df = DataFrame({
        "param-1": [0.12]
    })
    assert CondFlag("param-1").match(df, 0)

    df = DataFrame({
        "param-1": [144.0]
    })
    assert CondFlag("param-1").match(df, 0)

    df = DataFrame({
        "param-1": [True]
    })
    assert CondFlag("param-1").match(df, 0)

def test_CondAny_match():
    df = DataFrame()
    assert not CondAny("*{1}", CondFlag("param-1")).match(df, 0)

    df = DataFrame({
        "param-1": []
    })
    assert not CondAny("*{1}", CondFlag("param-1")).match(df, 0)

    df = DataFrame({
        "param-1": [False, True]
    })
    assert not CondAny("*{1}", CondFlag("param-1")).match(df, 0)

    df = DataFrame({
        "param-1": [False, True]
    })
    assert CondAny("*{2}", CondFlag("param-1")).match(df, 0)

    df = DataFrame({
        "param-1": [False, False]
    })
    assert not CondAny("*{3}", CondFlag("param-1")).match(df, 0)

def test_CondSet_match():
    df = DataFrame()
    assert not CondSet("param-1==data1 and param-2==data2").match(df, 0)

    df = DataFrame({
        "param-1": ["data1-1", "data1-2", "data1-3"],
        "param-2": ["data2-1", "data2-2", "data2-3"],
        "param-3": ["data3-1", "data3-2", "data3-3"],
    })
    assert CondSet("param-1==data1-1 and param-2==data2-1").match(df, 0)
    assert not CondSet("param-1==data1-1 and param-2==data2-2").match(df, 0)
    assert not CondSet("param-1==data1-2 and param-2==data2-1").match(df, 0)
    assert not CondSet("param-1==data1-2 and param-2==data2-2").match(df, 0)

    assert CondSet("param-1==data1-1 or param-2==data2-1").match(df, 0)
    assert CondSet("param-1==data1-1 or param-2==data2-2").match(df, 0)
    assert CondSet("param-1==data1-2 or param-2==data2-1").match(df, 0)
    assert not CondSet("param-1==data1-2 or param-2==data2-2").match(df, 0)

    assert CondSet("param-1==data1-1 and (param-2==data2-1 or param-3==data3-1)").match(df, 0)
    assert CondSet("param-1==data1-1 and (param-2==data2-2 or param-3==data3-1)").match(df, 0)
    assert CondSet("param-1==data1-1 and (param-2==data2-1 or param-3==data3-2)").match(df, 0)
    assert not CondSet("param-1==data1-1 and (param-2==data2-2 or param-3==data3-2)").match(df, 0)
    assert not CondSet("param-1==data1-2 and (param-2==data2-1 or param-3==data3-1)").match(df, 0)

def test_make_cond():
    cond = make_cond("param-1 and param-2", None)
    assert isinstance(cond, CondSet)
    cond = make_cond("param-1==abc", None)
    assert isinstance(cond, CondEqual)
    cond = make_cond("param-1 == abc", None)
    assert isinstance(cond, CondEqual)
    cond = make_cond("param-1!=abc", None)
    assert isinstance(cond, CondNotEqual)
    cond = make_cond("param-1 != abc", None)
    assert isinstance(cond, CondNotEqual)
    cond = make_cond("param-1", None)
    assert isinstance(cond, CondFlag)
    cond = make_cond("*{1}", CondFlag("abc"))
    assert isinstance(cond, CondAny)

def test_make_conds():
    conds = make_conds("aaa==123")
    assert len(conds) == 1
    assert isinstance(conds[0], CondEqual)

    conds = make_conds("aaa == 123")
    assert len(conds) == 1
    assert isinstance(conds[0], CondEqual)

    conds = make_conds("aaa")
    assert len(conds) == 1
    assert isinstance(conds[0], CondFlag)

    conds = make_conds("aaa and a == b")
    assert len(conds) == 1
    assert isinstance(conds[0], CondSet)
    assert len(conds[0].conds) == 2
    assert isinstance(conds[0].conds[0], CondFlag)
    assert isinstance(conds[0].conds[1], CondEqual)

    conds = make_conds("aaa==123 > aaa")
    assert len(conds) == 2
    assert isinstance(conds[0], CondEqual)
    assert isinstance(conds[1], CondFlag)

    conds = make_conds("aaa > aaa==123")
    assert len(conds) == 2
    assert isinstance(conds[0], CondFlag)
    assert isinstance(conds[1], CondEqual)

    conds = make_conds("aaa==123 and bbb or ccc!=123 > aaa==123")
    assert len(conds) == 2
    assert isinstance(conds[0], CondSet)
    assert isinstance(conds[1], CondEqual)
    assert len(conds[0].conds) == 3
    assert isinstance(conds[0].conds[0], CondEqual)
    assert isinstance(conds[0].conds[1], CondFlag)
    assert isinstance(conds[0].conds[2], CondNotEqual)

def test_search_results_generator():
    df = DataFrame({
        "zigzag": [True, True, True, True, True, False, True, True, True],
        "param-1": [True, True, False, True, True, False, True, True, False],
        "param-2": [False, True, True, False, False, False, True, True, True]
    })

    results = []
    for m in search_results_generator(df, "param-1 or param-2 > param-1 and param-2 > param-1 or param-2"):
        results.append(m)

    assert results == [(0, 2), (4, 7), (6, 8)]