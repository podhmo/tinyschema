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




@t.as_schema
class Signal(object):
    color = t.column(t.TextField, t.OneOf(["red", "blue", "yellow"]))


color0 = Signal(color="red")
data = color0.validate()
assert data == {"color": "red"}

try:
    color1 = Signal(color="green")
    data = color1.validate()
except t.ErrorRaised:
    print("error")




@t.as_schema
class Pair(object):
    l = t.column(t.Container(Point), class_="left")
    r = t.column(t.Container(Point), class_="right")


pair = Pair(l=Point(x=10, y=200), r=Point(x=50, y=200))

for f in pair:
    print(u"<div>({x}, {y})</div>".format(x=f.x.value, y=f.y.valueq))
# <div>(10, 200)</div>
# <div>(50, 200)</div>
