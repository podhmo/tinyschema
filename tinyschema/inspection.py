# -*- coding:utf-8 -*-
from . import (
    _Field,
    _Collection,
    _Container
)


type_dict = {
    _Field: "atom",
    _Collection: "array",
    _Container: "object"
}


def subschema_of(field):
    # PartialApplicationLike(partial(_Container, schema), required=True).partial
    return field.func.args[0]


def original_of(fn):
    if hasattr(fn, "func"):
        return original_of(fn.func)
    return fn


def type_of(cls):
    if not hasattr(cls, "__mro__"):
        return type_dict[original_of(cls)]
    mro = cls.__mro__
    if mro[1] is object:
        return "object"
    else:
        raise Exception(cls)
