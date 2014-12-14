# -*- coding:utf-8 -*-
import logging
logger = logging.getLogger(__name__)
import re
from functools import partial
from collections import (
    defaultdict,
    OrderedDict
)
from .langhelpers import gensym
from .compat import (
    text_,
    string_types,
    FileNotFoundError
)
import gettext
import translationstring
import os.path
here = os.path.abspath(os.path.dirname(__file__))
translation = None


def create_translator(languages=None):
    try:
        translation = gettext.translation("tinyschema", os.path.join(here, "locales"), languages=languages, codeset="utf8")
    except FileNotFoundError:
        logger.warn("languages %s is not found", languages)
        translation = None
    return translationstring.Translator(translation)


def set_translator(languages=None):
    global translator
    translator = create_translator(languages)


def get_translator():
    return translator

translator = None
set_translator(None)
_ = translationstring.TranslationStringFactory('tinyschema')


class ValidationError(Exception):
    def __init__(self, error=None, name=None, names=None, message=None):
        self.name = name
        self.error = error
        self.names = names or [name]
        self.message = message


class Failure(Exception):
    def __init__(self, errors):
        self.errors = errors

    def __str__(self):
        return "<Failure errors={!r}>".format(self.errors)


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

    def bind(self, *new_convertors, **options):
        convertors = self.convertors[:]
        convertors.extend(new_convertors)
        new_options = self.options.copy()
        new_options.update(options)
        return self.__class__(self.value, convertors, new_options)

    def validate(self):
        try:
            value = self.value
            for cnv in self.convertors:
                value = cnv(value, self.options)
            return value
        except Break as e:
            return e.value
        except ValidationError as e:
            e.name = self.name
            raise
        except Exception as e:
            raise ValidationError(e, name=self.name)

    def renewal(self, value):
        self.value = value


class _Container(object):
    def __init__(self, schema, value, convertors, options):
        if isinstance(value, schema):
            self.value = value
        else:
            self.value = schema.fromdict(value)
        self.schema = schema
        self.convertors = convertors
        self.options = options

    def __getattr__(self, k):
        try:
            return getattr(self.value, k)
        except AttributeError:
            return self.options[k]

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
                self.value.append(schema.fromdict(v))
        self.schema = schema
        self.convertors = convertors
        self.options = options

    def __getattr__(self, k):
        return self.options[k]

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
    def __init__(self, func, *args, **options):
        self.func = func
        self.args = list(args)
        self.options = options

    def partial(self, post=None, pre=None, **options_):
        convertors = self.args[:]
        if pre:
            convertors.insert(0, pre)
        if post:
            convertors.append(post)
        options = self.options.copy()
        options.update(options_)
        return PartialApplicationLike(self.func, *convertors, **options)

    def __call__(self, value, **options):
        new_options = self.options.copy()
        new_options.update(options)
        return self.func(value, self.args, new_options)


def column(func, *args, **kwargs):
    v = func(*args, **kwargs)
    v._column_counter = gensym()
    return v


def as_schema(cls):
    xs = []
    s = set()
    for c in cls.__mro__:
        for name, attr in c.__dict__.items():
            if hasattr(attr, "_column_counter"):
                if name not in s:
                    xs.append((attr._column_counter, name))
                    s.add(name)

    cls.fieldnames = [name for (_, name) in sorted(xs, key=lambda xs: xs[0])]

    # iter
    if not hasattr(cls, "__iter__"):
        def __iter__(self):
            for name in self.fieldnames:
                yield getattr(self, name)
        cls.__iter__ = __iter__

    if not hasattr(cls, "fromdict"):
        @classmethod
        def fromdict(cls, params):
            kwargs = {}
            for name in cls.fieldnames:
                if name in params:
                    kwargs[name] = params.pop(name)
            ob = cls(**kwargs)
            ob._kwargs = kwargs
            return ob
        cls.fromdict = fromdict

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
                    if e.message is not None:
                        if isinstance(e.message, translationstring.TranslationString):
                            errors[e.name].append(get_translator()(e.message))
                        else:
                            errors[e.name].append(e.message)
                    else:
                        errors[e.name].append(e.error)
            if errors:
                raise Failure(errors=errors)
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


class SchemaMeta(type):
    def __new__(self, name, bases, attrs):
        cls = super(SchemaMeta, self).__new__(self, name, bases, attrs)
        return as_schema(cls)

Schema = SchemaMeta("Schema", (object, ), {})


# field validation
class Any(object):
    def __init__(self, validators):
        self.validators = validators

    def __call__(self, val, options):
        errors = []
        for v in self.validators:
            try:
                val = v(val, options)
                return val
            except Exception:
                errors.append((_("${val} is not validation suceeed.", mapping={"val": val})))
        e = errors[0]
        raise ValidationError(error=e, message=e.message)


class Regex(object):
    def __init__(self, rx, msg=None):
        if isinstance(rx, string_types):
            self.rx = re.compile(rx)
            self.msg = msg
        else:
            self.rx = rx

    def __call__(self, val, options):
        if self.rx.match(val) is None:
            if self.msg:
                msg = self.msg(val)
            msg = _("invalid email ${val}", mapping={"val": val})
            raise ValidationError(message=(msg))
        return val

EMAIL_RE = "(?i)^[A-Z0-9._%!#$%&'*+-/=?^_`{|}~()]+@[A-Z0-9]+([.-][A-Z0-9]+)*\.[A-Z]{2,22}$"
EMail = partial(Regex, EMAIL_RE, lambda val: (_("${val} is not url", mapping={"val": val})))


class Range(object):
    def __init__(self, min, max):
        self.min = min
        self.max = max

    def __call__(self, val, options):
        if self.min > self.val:
            raise ValidationError(message=(_("${val} is smaller than ${min}", mapping={"val": val, "min": self.min})))
        if self.max < self.val:
            raise ValidationError(message=(_("${val} is bigger than ${max}", mapping={"val": val, "max": self.max})))
        return val


class Length(object):
    def __init__(self, min=None, max=None):
        self.min = min
        self.max = max

    def __call__(self, val, options):
        if min and min > self.val:
            raise ValidationError(message=(_("${val} is shorter than ${min}", mapping={"val": val, "min": self.min})))
        if max and max < self.val:
            raise ValidationError(message=(_("${val} is longer than ${max}", mapping={"val": val, "max": self.max})))
        return val


class OneOf(object):
    def __init__(self, choices):
        self.choices = choices

    def __call__(self, val, options):
        if val not in self.choices:
            candidates = u', '.join([text_(x) for x in self.choices])
            raise ValidationError(message=(_("${val} is not in ${candidates}", mapping={"val": val, "candidates": candidates})))
            raise ValueError(self.choices)
        return val


class Subset(object):
    def __init__(self, choices):
        self.choices = choices

    def __call__(self, val, options):
        if not set(val).issubset(self.choices):
            sval = u', '.join([text_(x) for x in val])
            candidates = u', '.join([text_(x) for x in self.choices])
            raise ValidationError(message=(_("${val} is not subset of  ${candidates}", mapping={"val": sval, "candidates": candidates})))
        return val

URL_REGEX = r"""(?i)\b((?:[a-z][\w-]+:(?:/{1,3}|[a-z0-9%])|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’]))"""  # "emacs!

URL = Regex(URL_REGEX)


def reject_None(val, options):
    if options.get("required", True):
        if val is None:
            raise ValidationError(None, message=(_("required")))
        else:
            return val
    elif val is not None:
        return val
    elif "default" in options:
        raise Break(options["default"])
    else:
        raise Break(None)


def parse_int(val, options):
    try:
        return int(val)
    except ValueError as e:
        raise ValidationError(e, message=(_("${val} is not int", mapping={"val": val})))


def parse_bool(val, options):
    try:
        return bool(val)
    except ValueError as e:
        raise ValidationError(e, message=(_("${val} is not bool", mapping={"val": val})))


def parse_float(val, options):
    try:
        return float(val)
    except ValueError as e:
        raise ValidationError(e, message=(_("${val} is not float", mapping={"val": val})))


def parse_text(val, options):
    try:
        return text_(val)
    except ValueError as e:
        raise ValidationError(e, message=(_("${val} is not text", mapping={"val": val})))


def parse_choices(val, options):
    try:
        return [(x, y) for x, y in val]
    except Exception as e:
        raise ValidationError(e, message=(_("${val} is not valid choices", mapping={"val": val})))


def positive(val, option):
    if val < 0:
        raise ValidationError(None, message=(_("${val} is smaller than zero", mapping={"val": val})))
    return val

# SchemaFactory


def Container(schema):
    return PartialApplicationLike(partial(_Container, schema), required=True, container=True).partial


def Collection(schema):
    return PartialApplicationLike(partial(_Collection, schema), required=True, container=True).partial

Field = PartialApplicationLike(_Field, pre=reject_None, required=True).partial
IntegerField = Field(post=parse_int, type="integer").partial
FloatField = Field(post=parse_float, type="number").partial
BooleanField = Field(post=parse_bool, type="boolean").partial
TextField = Field(post=parse_text, type="string").partial
ChoicesField = Field(post=parse_choices, type="choices").partial
PositiveIntegerField = IntegerField(post=positive).partial
