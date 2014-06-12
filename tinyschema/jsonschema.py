# -*- coding:utf-8 -*-
from tinyschema.inspection import (
    type_of,
    subschema_of
)


def parse_required(schema_cls):
    required = []
    for k in schema_cls.fieldnames:
        field = getattr(schema_cls, k)
        if field.options.get("required", False):
            required.append(k)
    return required


def parse_properties(schema_cls):
    D = {}
    for name in schema_cls.fieldnames:
        field = getattr(schema_cls, name)
        D[name] = _parse_property(name, field)
    return D


def _parse_property(name, field):
    type_ = type_of(field)
    if type_ == "atom":
        return {"type": field.options.get("type", "string")}
    elif type_ == "object":
        subschema = subschema_of(field)
        return as_jsonschema(subschema)
    elif type_ == "array":
        subschema = subschema_of(field)
        return {"type": "array", "items": as_jsonschema(subschema)}
    else:
        raise Exception("e")


def as_jsonschema(schema_cls):
    type_ = type_of(schema_cls)
    properties = parse_properties(schema_cls)
    required = parse_required(schema_cls)
    D = {
        "title": schema_cls.__name__,
        "type": type_,
        "required": required,
        "properties": properties,
    }
    return D
