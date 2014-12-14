# -*- coding:utf-8 -*-
import pytest
from .schemas import (
    Point,
    Pair,
    Plot
)


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
    from tinyschema import Failure
    pt = Point(x="10", y="20", z=None)
    pt.z.options["required"] = True

    with pytest.raises(Failure):
        pt.validate()


@pytest.skip("1")
def test_point_validator__failure():
    from tinyschema import Failure, lookup
    pt = Point(x="10", y="20", z=None)
    pt.validate()
    validator = lookup("equals", ["x", "y"])
    pt = validator(pt)

    with pytest.raises(Failure):
        pt.validate()


@pytest.skip("2")
def test_point_validator__success():
    from tinyschema import lookup
    pt = Point(x="20", y="20", z=None)
    pt.validate()
    validator = lookup("equals", ["x", "y"])
    pt = validator(pt)

    data = pt.validate()
    assert data["x"] == 20


@pytest.skip("3")
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


def test_pair__label():
    pair = Pair(l=dict(x="10", y="20"),
                r=dict(x="100", y="200"))

    assert pair.l.label == "l"
    assert pair.r.label == "r"


def test_pair__validation():
    pair = Pair(l=dict(x="10", y="20"),
                r=dict(x="100", y="200"))
    data = pair.validate()

    assert data["l"]["x"] == 10
    assert pair.l.x.raw == "10"
    assert data["r"]["x"] == 100
    assert pair.r.x.raw == "100"


def test_pair__validation_failure():
    from tinyschema import Failure
    pair = Pair(l=dict(x="10", y="20"),
                r=dict(x="100", y="200"))
    pair.l.z.options["required"] = True

    with pytest.raises(Failure):
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
    from tinyschema import Failure
    plot = Plot(ps=[Point(**{"x": "10", "y": "20"})])
    plot.ps[0].z.options["required"] = True

    with pytest.raises(Failure):
        plot.validate()
