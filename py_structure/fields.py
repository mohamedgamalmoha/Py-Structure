import re
import inspect
from datetime import datetime
from functools import partial
from decimal import Decimal as Dec
from collections import OrderedDict
from abc import ABC, abstractmethod
from typing import Any, Tuple, Pattern

# from .decorators import debug
from .base import Structure
from .protocols import Descriptor
from .utilities import _get_all_cls_init_args, _get_cls_init_args, is_default_init

# need to be modified
from .decorators import debug
from .modes import NoneMode


class Typed(ABC, Descriptor):
    typ: type = type

    def get_type(self) -> type:
        return self.typ

    def get_type_error_message(self) -> str:
        return f"In {self.__class__.__name__} class, Type of {self.name} should be {self.typ.__name__}"

    def get_value_error_message(self) -> str:
        return f"Invalid value of {self.name}"

    def __set__(self, instance, value) -> Any:
        if not isinstance(value, self.typ):
            raise TypeError(self.get_type_error_message())
        super(Typed, self).__set__(instance, value)


class Int(Typed):
    typ = int


class Float(Typed):
    typ = float


class Decimal(Typed):
    typ = Dec


class Binary(Typed):
    typ = bin


class Hex(Typed):
    typ = hex


class Oct(Typed):
    typ = oct


class Complex(Typed):
    typ = complex


class Signed(ABC, Descriptor):

    @abstractmethod
    def condition(self, value: Any) -> bool:
        """Checking the sign of value """
        pass

    def get_value_error_message(self) -> str:
        return f"Value of {self.name} should be {self.__name__.lower()}"

    def __set__(self, instance, value) -> None:
        if not self.condition(value):
            raise ValueError(self.get_value_error_message())
        super(Signed, self).__set__(instance, value)


class Positive(Signed):

    def condition(self, value: Any) -> bool:
        return value > 0


class Negative(Signed):

    def condition(self, value: Any) -> bool:
        return value < 0


class RangeNumber(Descriptor):

    def __init__(self, name: str = None,  *args, min_val: int = 1, max_val: int = 10, **kwargs):
        pair = (min_val, max_val)

        if any(map(lambda num: not str(num).isnumeric(), pair)):
            raise ValueError(f"Values of range`s limits should be numeric instead of ({min_val}, {max_val})")

        if any(map(lambda num: not isinstance(num, int), pair)):
            raise TypeError(f"Value should be typed integer instead of ({type(min_val)}, {type(max_val)})")

        self.max_val = max(pair)
        self.min_val = min(pair)

        super(RangeNumber, self).__init__(name,  *args, **kwargs)

    def __set__(self, instance, value) -> Any:
        if value not in range(self.min_val, self.max_val):
            raise ValueError(f"Value should be within range ({self.min_val}, {self.max_val}) not {value}")
        super(RangeNumber, self).__set__(instance, value)

    def get_range_limits(self) -> Tuple[int, int]:
        """Get range limit"""
        return self.min_val, self.max_val


class String(Typed):
    typ = str


class SizedString(String):

    def __init__(self, *args, max_len: int, **kwargs):
        self.max_len = max_len
        super(SizedString, self).__init__(*args, **kwargs)

    def __set__(self, instance, value) -> Any:
        if len(value) > self.max_len:
            raise ValueError(f"Value`s length is greater than max length ({self.max_len})")
        super(SizedString, self).__set__(instance, value)


class RegexString(String):

    def get_value_error_message(self) -> str:
        return f"Value of {self.name} does not match the pattern"

    def __init__(self, *args, pattern: Pattern = None, full_match: bool = False, **kwargs):
        self.pattern = pattern
        self.full_match = full_match

        super(RegexString, self).__init__(*args, **kwargs)

    def __set__(self, instance, value) -> Any:
        super(RegexString, self).__set__(instance, value)
        re_method = re.fullmatch if self.full_match else re.match
        if re_method(self.pattern, value) is None:
            raise ValueError(self.get_value_error_message())


class Email(RegexString):
    def __init__(self, *args, **kwargs):
        pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        super(Email, self).__init__(*args, pattern=pattern, full_match=True, **kwargs)


class URL(RegexString):
    def __init__(self, *args, **kwargs):
        pattern = re.compile(r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))")
        super(URL, self).__init__(*args, pattern=pattern, full_match=True, **kwargs)


class Slug(RegexString):

    def __init__(self, *args, **kwargs):
        pattern = re.compile(r"^ [a - z0 - 9] + (?:-[a-z0-9]+) *$")
        super(Slug, self).__init__(*args, pattern=pattern, full_match=True, **kwargs)


class DateTime(Typed):
    typ = datetime


class Duration(DateTime):

    def __init__(self, name: str = None, *args, start_date: datetime, end_date: datetime, **kwargs):
        pair = (start_date, end_date)

        if any(map(lambda num: not isinstance(num, datetime), pair)):
            raise TypeError(f"Value should be typed integer instead of ({type(start_date)}, {type(end_date)})")

        self.start_date = start_date
        self.end_date = end_date

        super(Duration, self).__init__(name, *args, **kwargs)

    def __set__(self, instance, value: datetime) -> Any:
        if not self.start_date < value < self.end_date:
            raise ValueError(f"Value should be within range ({self.start_date}, {self.end_date}) not {value}")
        super(Duration, self).__set__(instance, value)

    def get_range_limits(self) -> Tuple[datetime, datetime]:
        """Get range limit"""
        return self.start_date, self.end_date


class Choice(Descriptor):

    def __init__(self, *args, choices: tuple = (), **kwargs):
        self.choices = choices
        super(Choice, self).__init__(*args, **kwargs)

    def __set__(self, instance, value: datetime) -> Any:
        if value not in self.choices:
            raise ValueError(f'Expected {value!r} to be one of {self.choices!r}')
        super(Choice, self).__set__(instance, value)


def typeassert(cls=None, **fields):
    """Type assert decorator to guarantee static typing, descriptors and built in types are allowed.
    It is a lite way to construct a class similar to Structure from bas, but it has some limitations showed in warnings.

    Usage Example:
        @typeassert(name=str, shares=RangeNumber(min_val=5, max_val=20), price=Float)
        class Stock:
            pass
        stock = Stock(name='product', shares=10, price=40.5)

    Warnings:
        - Inheritance is supported, but using same decorator for children is not applicable.
            Ex:
                @typeassert(name=String, salary=RangeNumber(min_val=4000, max_val=10000), email=Email(), url=URL())
                class Employee:
                    pass
            Ex1:
                # Working example
                class UpdatedEmployee(Employee):
                    pass
            Ex2:
                # None Working example, throws RecursionError: maximum recursion depth exceeded
                @typeassert(permission=str)
                class UpdatedEmployee2(Employee):
                    pass

        - It doesn't support default values of descriptors, use Structure class from base instead.
        - In case the __init__ function is constructed in the class, it needs to support multi args and kwargs.
            Ex:
                def __init__(self, *args, *kwargs):
                    pass
    """
    # in case of the class is none, call it again with same args
    if cls is None:
        return partial(typeassert, **fields)

    # iterate throw kwargs to set teh name an attr and descriptor to its value
    # similar to:  self.name = Descriptor()
    descriptors_fields = OrderedDict()
    for name, val in fields.items():
        # get init args from child cls and its parent
        cls_parents_args = list(_get_all_cls_init_args(val))  # child args
        cls_args = list(_get_cls_init_args(val))  # parent args
        cls_args.extend(cls_parents_args)  # concatenating both of them

        # get value of init args
        init_values = {arg: getattr(val, arg, None) for arg in cls_args}
        # filter args in case of its value was none
        init_filtered_values = {k: v for k, v in init_values.items() if v is not None}

        # checking if the value is descriptor
        if issubclass(type(val), Descriptor) or issubclass(val, Descriptor):
            if not callable(val):
                # initialize descriptor class with init function args
                val = val.__class__(name=name, **init_filtered_values)
            else:
                # initialize descriptor class with name attribute only
                val = val(name=name)
            descriptors_fields.update({name: val})
        # checking if the value is typed as type - built in types -
        elif isinstance(val, type):
            # creating a class of Typed descriptor with setting its typ to val
            typ_cls = type(f"Custom{val.__name__.capitalize()}", (Typed, ), {'typ': val})
            val = typ_cls(name=name)
            descriptors_fields.update({name: val})

        # setting the value to main class
        setattr(cls, name, val)

    # setting fields and descriptors
    setattr(cls, 'fields', descriptors_fields.keys())
    setattr(cls, '__descriptors', descriptors_fields.values())

    # auto __init__ func generator
    def auto_init(self, *args, **kwargs) -> None:
        # checking the length of key arguments
        len_diff = len(kwargs) - len(descriptors_fields)
        if len_diff < 0:
            raise TypeError(f'Not enough key arguments, needs at least {abs(len_diff)} key arguments')

        # checking if all descriptors values is passed
        if any(map(lambda i: i not in kwargs, descriptors_fields.keys())):
            raise ValueError('Invalid arguments, some of them are not passed')

        # assigning values for descriptor attributes
        # similar to: self.name = val
        for nm, vl in kwargs.items():
            setattr(self, nm, vl)

        # calling __post_init__ function after __init__
        if hasattr(self, '__post_init__'):
            # run __post_init__ in debug mode
            post_init = debug(getattr(self, '__post_init__'), model=NoneMode)  # need to be fixed
            post_init.__call__(cls, *args, **kwargs)

    auto_init.__name__ = '__init__'

    # switching between __init__ function with __post_init__
    cls_init = getattr(cls, '__init__', None)
    # checking if the __init__ function is constructed or changed from the default one
    if not is_default_init(cls_init):
        setattr(cls, '__post_init__', cls_init)
    # updating functions with new ones
    setattr(cls, '__init__', auto_init)
    setattr(cls, '__repr__', Structure.__repr__)
    return cls


def strucassert(cls=None, **fields):
    """ Generate Structure Class.
        Inheritance is supported, but using same decorator for children is not applicable.
        It supports default values of descriptors.
    """

    if cls is None:
        return partial(strucassert, **fields)

    def update_kwargs(kwargs: dict) -> dict:
        """Updating descriptors of kwargs."""
        for k, v in kwargs.items():
            if inspect.isclass(v) and issubclass(v, Descriptor):
                # field=String -=> field=String()
                kwargs[k] = v()
            elif isinstance(v, type):
                # field=str -=> field=Typed(typ=str)
                new_typ_cls = type(f"Custom{v.__name__.capitalize()}", (Typed,), {'typ': v})
                kwargs[k] = new_typ_cls(name=k)
        return kwargs

    old_dict = dict(cls.__dict__)
    new_attrs = update_kwargs(fields)
    mro = (*cls.__mro__,)

    if Structure in cls.__mro__:
        # In case of being structure class in parents - hierarchy inheritance -.
        # getting all descriptors attrs
        old_attrs = {k: v for k, v in old_dict.items() if issubclass(v.__class__, Descriptor)}
        old_dict.update({**old_attrs, **new_attrs})
    else:
        # In case of being structure class not in parents
        mro = (Structure, *mro)
        old_dict.update(new_attrs)

    return type(cls.__name__, mro, old_dict)
