# -*- coding:utf-8 -*-
def _callFUT(*args, **kwargs):
    from tinyschema.jsonschema import as_jsonschema
    return as_jsonschema(*args, **kwargs)


def test_simple():
    from .schemas import Point
    result = _callFUT(Point)
    assert result == {'properties': {'x': {'type': 'integer'},
                                     'y': {'type': 'integer'},
                                     'z': {'type': 'integer'}},
                      'required': ['x', 'y'],
                      'title': 'Point',
                      'type': 'object'}


def test_has_array():
    from .schemas import Plot
    result = _callFUT(Plot)
    assert result == {'properties': {'ps': {'items': {'properties': {'x': {'type': 'integer'},
                                                                     'y': {'type': 'integer'},
                                                                     'z': {'type': 'integer'}},
                                                      'required': ['x', 'y'],
                                                      'title': 'Point',
                                                      'type': 'object'},
                                            'type': 'array'}},
                      'required': ['ps'],
                      'title': 'Plot',
                      'type': 'object'}


def test_has_object():
    from .schemas import Pair
    result = _callFUT(Pair)

    assert result == {'properties': {'l': {'properties': {'x': {'type': 'integer'},
                                                          'y': {'type': 'integer'},
                                                          'z': {'type': 'integer'}},
                                           'required': ['x', 'y'],
                                           'title': 'Point',
                                           'type': 'object'},
                                     'r': {'properties': {'x': {'type': 'integer'},
                                                          'y': {'type': 'integer'},
                                                          'z': {'type': 'integer'}},
                                           'required': ['x', 'y'],
                                           'title': 'Point',
                                           'type': 'object'}},
                      'required': ['l', 'r'],
                      'title': 'Pair',
                      'type': 'object'}
