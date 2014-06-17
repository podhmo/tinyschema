# -*- coding:utf-8 -*-
import tinyschema as t
from tinyschema.renderer import SchemaRenderer
from tinyschema.construct import (
    MapperFamily,
    Mapper,
    create_schema
)
import os.path
here = os.path.abspath(os.path.dirname(__file__))

"""
creation schema dynamically. sort of fields are select, multiselect, checkbox, radio
"""


class FieldParams(object):
    description = t.column(t.TextField)
    choices = t.column(t.ChoicesField)  # xxx
    required = t.column(t.BooleanField, default=False, required=False)


@t.as_schema
class select(FieldParams):
    pass


@t.as_schema
class multiselect(FieldParams):
    pass


@t.as_schema
class radio(FieldParams):
    pass


@t.as_schema
class checkbox(FieldParams):
    pass


def create_field(name, schema, validated):
    return t.column(t.Field,
                    post=t.OneOf([x[0] for x in validated["choices"]]),
                    name=name,
                    label=validated["description"],
                    choices=validated["choices"],
                    widget=schema.__class__.__name__,
                    required=validated["required"])


def iterator(params):
    for sub_params in params:
        name = sub_params["name"]
        typename = sub_params["type"]
        v = sub_params["values"]
        yield name, typename, v


# schema factory


mf = MapperFamily(create_schema, iterator=iterator)
mf.add("select", Mapper(select, create_field))
mf.add("multiselect", Mapper(multiselect, create_field))
mf.add("radio", Mapper(radio, create_field))
mf.add("checkbox", Mapper(checkbox, create_field))


# passed data


choices = [["0", "good"], ["1", "so-so"], ["2", "bad"]]
params = [
    {"name": "foo", "type": "select", "values": {"required": True, "choices": choices, "description": "--"}},
    {"name": "bar", "type": "radio", "values": {"required": False, "choices": choices, "description": "--"}},
    {"name": "boo", "type": "checkbox", "values": {"choices": choices, "description": "--"}}
]


# create schema


S = mf("S", params)


# rendering

# see: ./form.mako
print(SchemaRenderer("form.mako", directories=[here]).render_schema(S()))

"""
<select name="foo">
<option value="0">good</option>
<option value="1">so-so</option>
<option value="2">bad</option>
</select>

<label>good<input type="radio" name="bar" value="0"></input></label>
<label>so-so<input type="radio" name="bar" value="1"></input></label>
<label>bad<input type="radio" name="bar" value="2"></input></label>

<label>good<input type="checkbox" name="boo" value="0"></input></label>
<label>so-so<input type="checkbox" name="boo" value="1"></input></label>
<label>bad<input type="checkbox" name="boo" value="2"></input></label>
"""


# validation


try:
    # foo is required
    print(S().validate())
except t.ErrorRaised:
    print("hmm")

try:
    # 10 is not included in [0, 1, 2]
    print(S(foo="10").validate())
except t.ErrorRaised as e:
    print("hmm")

print(S(foo="0").validate())
# OrderedDict([('foo', '0'), ('bar', None), ('boo', None)])
