# -*- coding:utf-8 -*-
# integrate with client side
from tinyschema.tests.schemas import (
    Point,
    Pair,
    Plot,
)
from tinyschema.jsonschema import as_jsonschema
from pprint import pprint

pprint(as_jsonschema(Point))
pprint(as_jsonschema(Pair))
pprint(as_jsonschema(Plot))
