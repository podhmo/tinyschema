# -*- coding:utf-8 -*-
from tinyschema import as_schema, PositiveIntegerField, column


@as_schema
class Point(object):
    x = column(PositiveIntegerField)
    y = column(PositiveIntegerField)
    z = column(PositiveIntegerField, required=False)

pt = Point(x=10, y=20, z=30)

print(pt.x.name)
print(pt.z.options)
pt.z.options["required"] = True
