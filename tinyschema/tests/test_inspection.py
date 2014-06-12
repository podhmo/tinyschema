# -*- coding:utf-8 -*-
import pytest
from .schemas import (
    Point,
    Pair,
    Plot
)

candidates = [
    (Point, "object"),
    (Pair, "object"),
    (Plot, "object"),
    (Point.x, "atom"),
    (Pair.l, "object"),
    (Plot.ps, "array")
]


@pytest.mark.parametrize("target, detected", candidates)
def test_object(target, detected):
    from tinyschema.inspection import type_of
    assert type_of(target) == detected
