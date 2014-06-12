# -*- coding:utf-8 -*-
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
    l = column(Container(Point), label="l")
    r = column(Container(Point), label="r")


@as_schema
class Plot(object):
    ps = column(Collection(Point))
