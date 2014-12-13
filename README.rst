tinyschema
========================================

features

- schema definition
- schema validation
- data validation

schema definition
----------------------------------------

The way of schema definition is like a below sample.

.. code:: python

    import tinyschema as t

    class Point(t.Schema):
        x = t.column(t.IntegerField)
        y = t.column(t.IntegerField)
        z = t.column(t.IntegerField, required=False)

Accessing field with dot-access, like a plain python object. But a
returned object is wrapped by Field object.

Field object has these members.

- name -- name of field (system value)
- value -- value of field

So this Point schema accessing a field like a below.

.. code::

    pt = Point(x=10, y=20)

    print(pt.x.name)   # => x
    print(pt.x.value)  # => 10


addition
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

A column of Schema can store your favirote value. below example is
stored a value about css-class "hidden". and adding label option
that display expression for human (display value).

.. code:: python

    class Point(t.Schema):
        x = t.column(t.IntegerField, label=u"x-coordinate", class_="hidden")

    pt = Point(x=10, y=20)

    print(pt.x.label)  # => x-coordinate
    print(pt.x.class_) # => "hidden"


schema validation
----------------------------------------

Schema has a behavior of schema-validation. schema-validation is format checking.

- filtering expected values only.
- checking type of value.
- converting value if need.

.. code:: python

    params = {"x": "10", "y": "20", "foo": "foo"}
    pt = Point.fromdict(params)
    print(pt.validate())  # => OrderedDict([('x', 10), ('y', 20), ('z', None)])

schema-validation is run by calling validate() method. In above code,
"foo" value is not member of Point schema, so validated value does not
include a value name of foo. And a column-z has required=False option,
because of this, a passed value that doesn't have a value name of z,
converted value is None.

when schema error is found.
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

when schema validation is failure, then, ErrorRaised exception is raised.

.. code:: python

    params = {"x": "aa"}
    pt = Point.fromdict(params)
    pt.validate()
    # tinyschema.ErrorRaised: <ErrorRaised errors=defaultdict(<class 'list'>, {'y': ['required'], 'x': ['aa is not int']})>


Adding field validation
----------------------------------------

Adding field validation example is here.(using oneOf validator)

.. code:: python

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
    except t.ErrorRaised as e:
        print(e)
       # <ErrorRaised errors=defaultdict(<class 'list'>, {'color': ['green is not in red, blue, yellow']})>

default validator are below.

- Any, Regex, Email, Range, Length, OneOf, Subset, URL

default type of field.

- IntegerField, FloatField, BooleanField, TextField, ChoicesField, PositiveIntegerField


more complex structure
----------------------------------------

tinyschema support more complex structure like a dict-tree, sequence,
or combination of one.

dict-tree(using Container)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

A field of schema is also schema. below example, Pair Schema has two
members, l and r. And l and r is a Point Schema.

.. code:: python

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

    pair.l.value.x.name # => x
    pair.l.value.x.value # => 10


sequence(using Collection)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

PointList is a sequence of Point.

.. code:: python

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


data validation
----------------------------------------

data-validation is a checking about a relation of each data.

(TODO: gentle example)

.. code:: python

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

    print(validate(Point(x=10, y=20, z=1000)))
    # tinyschema.ErrorRaised: <ErrorRaised errors=defaultdict(<class 'list'>, {'z': ['too large'], 'x': ['not equal']})>

    print(validate(Point(x="aa")))
    # tinyschema.ErrorRaised: <ErrorRaised errors=defaultdict(<class 'list'>, {'x': ['aa is not int'], 'y': ['required']})>
