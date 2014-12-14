# -*- coding:utf-8 -*-
def setup_module(m):
    from tinyschema import set_translator, get_translator
    prev = get_translator()
    set_translator(languages=["ja"])
    this = get_translator()
    assert id(prev) != id(this)


def teardown_module(m):
    from tinyschema import set_translator
    set_translator(languages=None)


def test_positive():
    from tinyschema import Failure, Schema, column, PositiveIntegerField
    import pytest

    class S(Schema):
        value = column(PositiveIntegerField)

    with pytest.raises(Failure) as e:
        S(value=-10).validate()
    assert "小さいです" in e.value.errors["value"][0]
