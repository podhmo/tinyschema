import pytest


def _getTarget():
    from tinyschema import Schema
    return Schema


def _makeOne(*args, **kwargs):
    import tinyschema as t

    class S(_getTarget()):
        x = t.column(t.IntegerField, t.positive, x="yyy")
    return S(*args, **kwargs)


def test_any_field_required_None__is_first_converter():
    from tinyschema import reject_None
    s = _makeOne(x="yyy")
    assert s.x.convertors[0] == reject_None


def test_option_access_after_initialized():
    s = _makeOne(x="yyy")
    assert s.x.x == "yyy"


def test_option_access_after_bind():
    s = _makeOne(x="yyy")
    s.x = s.x.bind(x="zzz")
    assert s.x.x == "zzz"


def test_converter_access_after_initialized():
    import tinyschema as t
    s = _makeOne(x=10)
    assert t.positive in s.x.convertors


def test_converter_access_after_bind():
    import tinyschema as t
    s = _makeOne(x=10)
    s.x = s.x.bind(t.OneOf(["a", "b", "c"]))
    assert t.positive in s.x.convertors
    assert any(isinstance(e, t.OneOf) for e in s.x.convertors)


def test_schema_validation__success():
    s = _makeOne(x="10")
    result = s.validate()
    assert result == {"x": 10}


def test_schema_validation__failure():
    import tinyschema as t
    s = _makeOne(x="aa")

    with pytest.raises(t.Failure) as e:
        s.validate()
    assert bool(e.value.errors) is True
