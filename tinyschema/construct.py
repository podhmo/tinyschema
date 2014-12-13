# -*- coding:utf-8 -*-
import logging
logger = logging.getLogger(__name__)


def iterate_params(params):
    if not hasattr(params, "keys"):
        for k, v in params:
            yield k, v
    elif "order" in params:
        for k in params["order"]:
            yield k, params[k]
    else:
        for k, v in params.items():
            yield k, v


class Mapper(object):
    def __init__(self, schema, transformer):
        self.schema = schema
        self.transformer = transformer

    def __call__(self, name, params):
        schema = self.schema(**params)
        parsed = schema.validate()
        return self.transformer(name, schema, parsed)


def default_iterator(triple_list):
    for name, typename, values in triple_list:
        yield name, typename, values


class MapperFamily(object):
    def __init__(self, aggregate, iterator=default_iterator):
        self.families = {}
        self.aggregate = aggregate
        self.iterator = iterator

    def add(self, typename, schema):
        self.families[typename] = schema

    def __call__(self, root_name, params):
        result = {}
        for name, typename, v in self.iterator(params):
            mapper = self.families[typename]
            result[name] = mapper(name, v)
        return self.aggregate(root_name, result)


# # sample

# @t.as_schema
# class FieldParams(object):
#     description = t.column(t.TextField)
#     choices = t.column(t.Field)  # xxx
#     widget = t.column(t.TextField, post=t.OneOf(["select", "checkbox", "radio", "multiselect"]))
#     required = t.column(t.BooleanField, default=False, required=False)


# def create_field(name, schema, validated):
#     return t.column(t.Field,
#                     post=t.OneOf([x[0] for x in validated["choices"]]),
#                     name=name,
#                     label=validated["description"],
#                     choices=validated["choices"],
#                     widget=validated["widget"],
#                     required=validated["required"])

import tinyschema as t


def create_schema(name, attrs):
    return t.as_schema(type(name, (object, ), attrs))
