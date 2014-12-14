# -*- coding:utf-8 -*-
import tinyschema as t


class Point(t.Schema):
    x = t.column(t.IntegerField, label=u"x-coordinate", class_="hidden")
    y = t.column(t.IntegerField)
    z = t.column(t.IntegerField, required=False)

pt = Point(x=10, y=20)
print(pt.x.name)   # => x
print(pt.x.label)  # => x-coordinate
print(pt.x.value)  # => 10

print(pt.x.class_)  # => "hidden"


params = {"x": "10", "y": "20", "foo": "foo"}
pt = Point.fromdict(params)
# print(pt.validate())  # => OrderedDict([('x', 10), ('y', 20), ('z', None)])

params = {"x": "aa"}
pt = Point.fromdict(params)
# pt.validate()
# tinyschema.Failure: <Failure errors=defaultdict(<class 'list'>, {'y': ['required'], 'x': ['aa is not int']})>


class Signal(t.Schema):
    color = t.column(t.TextField, t.OneOf(["red", "blue", "yellow"]))

# success version
signal = Signal(color="red")
data = signal.validate()
print(data["color"])  # => "red"

# failure version
try:
    signal2 = Signal(color="green")
    data = signal2.validate()
except t.Failure as e:
    print(e)
   # <Failure errors=defaultdict(<class 'list'>, {'color': ['green is not in red, blue, yellow']})>

class Pair(t.Schema):
    l = t.column(t.Container(Point), class_="left")
    r = t.column(t.Container(Point), class_="right")

params = {
    "l": {"x": "10", "y": "20", "foo": "foo"},
    "r": {"x": "100", "y": "20"},
}

pair = Pair.fromdict(params)
import pprint
pprint.pprint(pair.validate())
# {'l': OrderedDict([('x', 10), ('y', 20), ('z', None)]),
#  'r': OrderedDict([('x', 100), ('y', 20), ('z', None)])}


class PointList(t.Schema):
    points = t.column(t.Collection(Point))

params = {
    "points": [{"x": "10", "y": "20"}, {"x": "20", "y": "20"}, {"x": "30", "y": "20"}, ]
}

plist = PointList.fromdict(params)
import pprint
pprint.pprint(plist.validate())

# {'points': [OrderedDict([('x', 10), ('y', 20), ('z', None)]),
#             OrderedDict([('x', 20), ('y', 20), ('z', None)]),
#             OrderedDict([('x', 30), ('y', 20), ('z', None)])]}


from tinyschema.datavalidation import ValidationObject, multi, Invalid, single, share


class PointValidation(ValidationObject):
    def __init__(self, limit):
        self.limit = limit

    @multi(["x", "z"])
    def equals(self, x, z):
        if x != z:
            raise Invalid("not equal")

    @share(single("x"), single("y"), single("z"))
    def limit(self, value):
        if value > self.limit:
            raise Invalid("too large")

validate = PointValidation(limit=100)
print(validate(Point(x=10, y=20)))  # => OrderedDict([('x', 10), ('y', 20), ('z', None)])
print(validate(Point(x=10, y=20, z=10)))  # => OrderedDict([('x', 10), ('y', 20), ('z', 10)])
# print(validate(Point(x=10, y=20, z=1000)))
# tinyschema.Failure: <Failure errors=defaultdict(<class 'list'>, {'z': ['too large'], 'x': ['not equal']})>
# print(validate(Point(x="aa")))
# tinyschema.Failure: <Failure errors=defaultdict(<class 'list'>, {'x': ['aa is not int'], 'y': ['required']})>

from tinyschema.datavalidation import collection


class PointListValidation(ValidationObject):
    @collection("points")
    class sub:
        @share(single("x"), single("y"))
        def positive(self, v):
            if v < 0:
                raise Invalid("oops")
params = {
    "points": [{"x": "10", "y": "20"}, {"x": "20", "y": "-20"}, {"x": "30", "y": "20"}, ]
}

try:
    PointListValidation()(PointList.fromdict(params))
except t.Failure as e:
    import json
    print("error: {}".format(json.dumps(e.errors, ensure_ascii=False)))


from tinyschema.datavalidation import container


class PairValidation(ValidationObject):
    @container("l")
    class sub:
        @share(single("x"), single("y"))
        def positive(self, v):
            if v < 0:
                raise Invalid("not positive")

params = {
    "l": {"x": "10", "y": "-20", "foo": "foo"},
    "r": {"x": "100", "y": "20"},
}

PairValidation()(Pair.fromdict(params))
