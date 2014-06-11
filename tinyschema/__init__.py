# -*- coding:utf-8 -*-
import logging
logger = logging.getLogger(__name__)
from functools import partial
from collections import (
    defaultdict,
    OrderedDict
)
from .langhelpers import gensym
from .compat import (
    text_,
    text_type,
    string_types,
    xrange,
    is_nonstr_iter,
    )


class ValidationError(Exception):
    def __init__(self, name, error):
        self.name = name
        self.error = error


class ErrorRaised(Exception):
    def __init__(self, errors):
        self.errors = errors


class Break(Exception):
    def __init__(self, value):
        self.value = value


class _Field(object):
    def __init__(self, value, convertors, options):
        self.value = value
        self.convertors = convertors
        self.options = options

    def __getattr__(self, name):
        try:
            return self.options[name]
        except KeyError as e:
            raise AttributeError(e)

    def validate(self):
        try:
            value = self.value
            for cnv in self.convertors:
                value = cnv(value, self.options)
            return value
        except Break as e:
            return e.value
        except Exception as e:
            raise ValidationError(self.name, e)

    def renewal(self, value):
        self.value = value


class _Container(object):
    def __init__(self, schema, value, convertors, options):
        if isinstance(value, schema):
            self.value = value
        else:
            self.value = schema(**value)
        self.schema = schema
        self.convertors = convertors
        self.options = options

    def __getattr__(self, k):
        return getattr(self.value, k)

    def __repr__(self):
        return "<Container {!r}>".format(self.value.__class__)

    def renewal(self, value):
        pass


class _Collection(object):
    def __init__(self, schema, values, convertors, options):
        self.value = []
        for v in values:
            if isinstance(v, schema):
                self.value.append(v)
            else:
                self.value.append(schema(**v))
        self.schema = schema
        self.convertors = convertors
        self.options = options

    def __getitem__(self, i):
        return self.value[i]

    def __repr__(self):
        return "<Collection {!r}>".format(self.value.__class__)

    def renewal(self, value):
        pass

    def __iter__(self):
        return iter(self.value)

    def __len__(self):
        return len(self.value)

    def validate(self):
        return [v.validate() for v in self.value]


class PartialApplicationLike(object):
    def __init__(self, fn, *args, **kwargs):
        self.fn = fn
        self.args = list(args)
        self.kwargs = kwargs

    def partial(self, pre=None, post=None, **kwargs_):
        args = self.args[:]
        if pre:
            args.insert(0, pre)
        if post:
            args.append(post)
        kwargs = self.kwargs.copy()
        kwargs.update(kwargs_)
        return PartialApplicationLike(self.fn, *args, **kwargs)

    def __call__(self, value, **kwargs):
        new_kwargs = self.kwargs.copy()
        new_kwargs.update(kwargs)
        return self.fn(value, self.args, new_kwargs)


def column(fn, *args, **kwargs):
    v = fn(*args, **kwargs)
    v._column_counter = gensym()
    return v


def as_schema(cls):
    xs = []
    for name, attr in cls.__dict__.items():
        if hasattr(attr, "_column_counter"):
            xs.append((attr._column_counter, name))
    cls.fieldnames = [name for (_, name) in sorted(xs, key=lambda xs: xs[0])]

    # iter
    if not hasattr(cls, "__iter__"):
        def __iter__(self):
            for name in self.fieldnames:
                yield getattr(self, name)
        cls.__iter__ = __iter__

    # validate
    if not hasattr(cls, "_validate"):
        def _validate(self):
            errors = defaultdict(list)
            values = OrderedDict()
            for name in self.fieldnames:
                try:
                    current = getattr(self, name)
                    current.raw = current.value  # xxx
                    validated = current.validate()
                    values[name] = validated
                    current.renewal(validated)
                except ValidationError as e:
                    errors[e.name].append(e.error)
            if errors:
                raise ErrorRaised(errors=errors)
            return values
        cls._validate = _validate

    if not hasattr(cls, "validate"):
        def validate(self):
            return self._validate()
        cls.validate = validate

    # init
    template = """\
def __init__(self, {kwargs}):
    cls = self.__class__
    {body}
    """
    kwargs = ", ".join(["{}=None".format(name) for name in cls.fieldnames])
    body = "\n    ".join("self.{x} = getattr(cls, '{x}')({x}, name='{x}')".format(x=name) for name in cls.fieldnames)
    exec(template.format(kwargs=kwargs, body=body))
    cls.__init__ = locals()["__init__"]
    return cls


# validator
class Any(object):
    def __init__(self, validators):
        self.validators = validators

    def __call__(self, val, options):
        errors = []
        for v in self.validators:
            try:
                val = v(val, options)
                return val
            except Exception as e:
                errors.append(e)
        raise ValidationError(error=errors[0])

import re


class Regex(object):
    def __init__(self, rx):
        if isinstance(rx, string_types):
            self.rx = re.compile(rx)
        else:
            self.rx = rx

    def __call__(self, val, options):
        if self.rx.match(val) is None:
            raise ValueError(self.rx.pattern)
        return val

EMAIL_RE = "(?i)^[A-Z0-9._%!#$%&'*+-/=?^_`{|}~()]+@[A-Z0-9]+([.-][A-Z0-9]+)*\.[A-Z]{2,22}$"
EMail = partial(Regex, EMAIL_RE)


class Range(object):
    def __init__(self, min, max):
        self.min = min
        self.max = max

    def __call__(self, val, options):
        if min > self.val:
            raise ValueError(self.min)
        if max < self.val:
            raise ValueError(self.max)
        return val


class Length(object):
    def __init__(self, min=None, max=None):
        self.min = min
        self.max = max

    def __call__(self, val, options):
        if min and min > self.val:
            raise ValueError(self.min)
        if max and max < self.val:
            raise ValueError(self.max)
        return val


class OneOf(object):
    def __init__(self, choices):
        self.choices = choices

    def __call__(self, val, options):
        if val not in self.choices:
            raise ValueError(self.choices)
        return val


class ContainsOnly(object):
    def __init__(self, choices):
        self.choices = choices

    def __call__(self, val, options):
        if not set(val).issubset(self.choices):
            raise ValueError(self.choices)
        return val

URL_REGEX = r"""(?i)\b((?:[a-z][\w-]+:(?:/{1,3}|[a-z0-9%])|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’]))""" # "emacs!

URL = Regex(URL_REGEX)


def reject_None(val, options):
    if options.get("required", True):
        return val
    raise Break(None)


def parse_int(val, options):
    return int(val)


def parse_bool(val, options):
    return bool(val)


def parse_text(val, options):
    return text_(val)


def positive(val, option):
    assert val >= 0
    return val


# SchemaFactory

def Container(schema):
    return PartialApplicationLike(partial(_Container, schema)).partial


def Collection(schema):
    return PartialApplicationLike(partial(_Collection, schema)).partial

Field = PartialApplicationLike(_Field, reject_None).partial
IntegerField = Field(post=parse_int).partial
BooleanField = Field(post=parse_bool).partial
TextField = Field(post=parse_text).partial

PositiveIntegerField = IntegerField(post=positive).partial
