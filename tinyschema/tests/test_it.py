# -*- coding:utf-8 -*-
import pytest
from tinyschema import(
    as_schema,
    PositiveIntegerField,
    column,
    Container,
    Collection,
)


@as_schema
class Point(object):
    x = column(PositiveIntegerField)
    y = column(PositiveIntegerField)
    z = column(PositiveIntegerField, required=False)


@as_schema
class Pair(object):
    l = column(Container(Point))
    r = column(Container(Point))


@as_schema
class Plot(object):
    ps = column(Collection(Point))


def test_point__name():
    pt = Point(x="10", y="20", z=None)
    assert pt.x.name == "x"


def test_point__value():
    pt = Point(x="10", y="20", z=None)
    assert pt.x.value == "10"


def test_point__validation():
    pt = Point(x="10", y="20", z=None)
    data = pt.validate()
    assert data["x"] == 10
    assert pt.x.raw == "10"


def test_point__validation_failure():
    from tinyschema import ErrorRaised
    pt = Point(x="10", y="20", z=None)
    pt.z.options["required"] = True

    with pytest.raises(ErrorRaised):
        pt.validate()


def test_point_validator__failure():
    from tinyschema import ErrorRaised, lookup
    pt = Point(x="10", y="20", z=None)
    pt.validate()
    validator = lookup("equals", ["x", "y"])
    pt = validator(pt)

    with pytest.raises(ErrorRaised):
        pt.validate()


def test_point_validator__success():
    from tinyschema import lookup
    pt = Point(x="20", y="20", z=None)
    pt.validate()
    validator = lookup("equals", ["x", "y"])
    pt = validator(pt)

    data = pt.validate()
    assert data["x"] == 20


def test_point_validator__skip():
    from tinyschema import lookup
    pt = Point(x="10", y="20", z=None)
    pt.validate()
    validator = lookup("equals", ["z", "y"])
    pt = validator(pt)

    data = pt.validate()
    assert data["x"] == 10


def test_pair__name():
    pair = Pair(l=Point(x="10", y="20"),
                r=Point(x="10", y="20"))

    assert pair.l.x.name == "x"
    assert pair.r.x.name == "x"


def test_pair__value():
    pair = Pair(l=Point(x="10", y="20"),
                r=Point(x="100", y="200"))

    assert pair.l.x.value == "10"
    assert pair.r.x.value == "100"


def test_pair__value2():
    pair = Pair(l=dict(x="10", y="20"),
                r=dict(x="100", y="200"))

    assert pair.l.x.value == "10"
    assert pair.r.x.value == "100"


def test_pair__validation():
    pair = Pair(l=dict(x="10", y="20"),
                r=dict(x="100", y="200"))
    data = pair.validate()

    assert data["l"]["x"] == 10
    assert pair.l.x.raw == "10"
    assert data["r"]["x"] == 100
    assert pair.r.x.raw == "100"


def test_pair__validation_failure():
    from tinyschema import ErrorRaised
    pair = Pair(l=dict(x="10", y="20"),
                r=dict(x="100", y="200"))
    pair.l.z.options["required"] = True

    with pytest.raises(ErrorRaised):
        pair.validate()


def test_plot__name():
    plot = Plot(ps=[{"x": "10", "y": "20"}])
    assert plot.ps[0].x.name == "x"


def test_plot__value():
    plot = Plot(ps=[{"x": "10", "y": "20"}])
    assert plot.ps[0].x.value == "10"


def test_plot__value2():
    plot = Plot(ps=[Point(**{"x": "10", "y": "20"})])
    assert plot.ps[0].x.value == "10"


def test_plot__validation():
    plot = Plot(ps=[Point(**{"x": "10", "y": "20"})])
    data = plot.validate()

    assert data["ps"][0]["x"] == 10


def test_plot__validation2():
    from tinyschema import ErrorRaised
    plot = Plot(ps=[Point(**{"x": "10", "y": "20"})])
    plot.ps[0].z.options["required"] = True

    with pytest.raises(ErrorRaised):
        plot.validate()

