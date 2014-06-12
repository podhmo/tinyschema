# -*- coding:utf-8 -*-
import tinyschema as t


@t.as_schema
class Point(object):
    x = t.column(t.IntegerField, label=u"横")
    y = t.column(t.IntegerField)
    z = t.column(t.IntegerField, required=False)

pt = Point(x=10, y=20)

assert (pt.x.name) == "x"
assert (pt.x.label) == "横"


@t.add_validator("equals")
def equals(x, y):
    if x != y:
        raise ValueError("not equal")


pt2 = t.lookup("equals", ["x", "y"])(pt)
try:
    pt2.validate()
except t.ErrorRaised as e:
    print(e)


@t.as_schema
class Signal(object):
    color = t.column(t.TextField, t.OneOf(["red", "blue", "yellow"]))


color0 = Signal(color="red")
data = color0.validate()
assert data == {"color": "red"}

try:
    color1 = Signal(color="green")
    data = color1.validate()
except t.ErrorRaised as e:
    print(e)


@t.as_schema
class Pair(object):
    l = t.column(t.Container(Point), class_="left")
    r = t.column(t.Container(Point), class_="right")


pair = Pair(l=Point(x=10, y=200), r=Point(x=50, y=200))

for f in pair:
    print(u"<div class='{class_}'>({x}, {y})</div>".format(x=f.x.value, y=f.y.value, class_=f.options["class_"]))
# <div class='left'>(10, 200)</div>
# <div class='right'>(50, 200)</div>


