# -*- coding:utf-8 -*-
import logging
logger = logging.getLogger(__name__)
import sys
from functools import partial
from collections import defaultdict
from . import Failure


def is_validator(v):
    return hasattr(v, "_v_count")


class Counter(object):
    def __init__(self):
        self.i = 0

    def __call__(self):
        self.i += 1
        return self.i

counter = Counter()


class Multi(object):
    def __init__(self, names, method, msg=None, position=None):
        self.names = names
        self.method = method
        self._v_count = counter()
        self.msg = msg
        self.position = position

    def __call__(self, parent, params):
        if all(params.get(name) is not None for name in self.names):
            return self.method(parent, *(params[name] for name in self.names))


class Matched(object):
    def __init__(self, names, method, msg=None):
        self.names = names
        self.method = method
        self._v_count = counter()
        self.msg = msg

    def __call__(self, parent, params):
        if any(params.get(name) is not None for name in self.names):
            return self.method(parent, [(name, params[name]) for name in self.names if params.get(name) is not None])


class Convert(object):
    def __init__(self, names, method, msg=None):
        self.names = names
        self.method = method
        self._v_count = counter()
        self.msg = msg

    def __call__(self, parent, params):
        if not self.names:
            return self.method(parent, params)
        else:
            if all(params.get(name) is not None for name in self.names):
                return self.method(parent, params)


class Container(object):
    def __init__(self, name, cls):
        self.names = [name]  # for common interface
        self.name = name
        self.validators = [v for v in cls.__dict__.values() if is_validator(v)]
        self.validators.sort(key=lambda o: o._v_count)
        self._v_count = counter()
        self.msg = None

        self.child = None

    def __call__(self, parent, params):
        if self.name in params:
            target = params[self.name]
            for v in self.validators:
                self.child = v
                v(parent, target)

    @property
    def position(self):
        r = [self.name]
        if self.child:
            r.append(getattr(self.child, "position") or self.child.names[0])
        return r


class Collection(object):
    def __init__(self, name, cls):
        self.names = [name]  # for common interface
        self.name = name
        self.validators = [v for v in cls.__dict__.values() if is_validator(v)]
        self.validators.sort(key=lambda o: o._v_count)
        self._v_count = counter()
        self.msg = None

        self.index = None
        self.child = None

    def __call__(self, parent, params):
        if self.name in params:
            targets = params[self.name]
            for i, target in enumerate(targets):
                for v in self.validators:
                    self.index = i
                    self.child = v
                    v(parent, target)

    @property
    def position(self):
        r = [self.name]
        if self.child:
            r.append(self.index)
            r.append(getattr(self.child, "position") or self.child.names[0])
        return r


def single(name, msg=None):
    return partial(Multi, [name], msg=msg)


def multi(names, msg=None, position=None):
    assert isinstance(names, (list, tuple))
    return partial(Multi, names, msg=msg, position=position)


def convert(names=None, msg=None):
    return partial(Convert, names, msg=msg)


def matched(names, msg=None):
    assert isinstance(names, (list, tuple))
    return partial(Matched, names, msg=msg)


def collection(name):
    return partial(Collection, name)


def container(name):
    return partial(Container, name)


def share(*factories):
    cls_env = sys._getframe(1).f_locals

    def wrapper(method):
        validations = []
        for f in factories:
            name = "{}{}".format(method.__name__, counter())
            v = f(method)
            cls_env[name] = v
            validations.append(v)
        return validations
    return wrapper


class Invalid(Exception):
    def __init__(self, msg, position=None):
        self.msg = msg
        self.position = position


class Interrupt(Exception):
    def __init__(self, msg, position=None):
        self.msg = msg
        self.position = position


class ValidationObjectMeta(type):
    def __new__(self, name, bases, attrs):
        validators = [v for v in attrs.values() if is_validator(v)]
        validators.sort(key=lambda o: o._v_count)
        attrs["validators"] = validators

        def __call__(self, ob):
            status = True
            params, errors = self.configure(ob)
            if errors:
                return self.on_failure(ob, params, errors)

            try:
                for v in self.validators:
                    try:
                        v(self, params)
                    except self.Exception as e:
                        self.catch_error(params, errors, v, e)
                        status = False
            except self.Interrupt as e:
                self.catch_error(params, errors, v, e)
                return self.on_failure(ob, params, errors)

            if status:
                return self.on_success(ob, params)
            else:
                return self.on_failure(ob, params, errors)

        attrs["__call__"] = __call__
        attrs["validate"] = __call__
        return super().__new__(self, name, bases, attrs)


class _ValidationObject(object):
    def configure(self, schema):
        try:
            return schema.validate(), defaultdict(list)
        except Failure as e:
            return {}, e.errors

    def catch_error(self, params, errors, validation, e):
        position = getattr(e, "position", None)
        if position is None:
            position = getattr(validation, "position", None) or validation.names[0]

        if validation.msg is None:
            msg = e.args[0]
        elif callable(validation.msg):
            msg = validation.msg(**params)
        else:
            msg = validation.msg

        if not isinstance(position, (list, tuple)):
            errors[position].append(msg)
        else:
            target = errors
            for i, k in enumerate(position[:-1]):
                if k not in target:
                    if isinstance(position[i + 1], int):
                        target[k] = [defaultdict(list) for i in range(position[i + 1] + 1)]
                    else:
                        target[k] = defaultdict(list)
                try:
                    target = target[k]
                except IndexError:
                    for i in range(k + 1):
                        target[i] = defaultdict(list)
            target[position[-1]].append(msg)

    def on_success(self, _, params):
        return params

    def on_failure(self, _, params, errors):
        raise Failure(errors)

ValidationObject = ValidationObjectMeta("ValidationObject", (_ValidationObject, ), {"Exception": Invalid, "Interrupt": Interrupt})
