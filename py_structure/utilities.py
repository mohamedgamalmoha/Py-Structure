from functools import reduce
from collections import Iterable
from typing import List, Tuple, Type, Any, Callable, Generator
from inspect import Signature, Parameter, signature, isfunction, ismethod, getmembers


def _get_cls_method_args(cls, func_name: str) -> Tuple[str]:
    """Get class function arguments for a given class (Child Only, Parents excluded)"""
    _signature = signature(getattr(cls, func_name))
    return tuple(arg.name for arg in _signature.parameters.values())


def _get_all_cls_method_args(cls: Type, func_name: str) -> Tuple[str]:
    """Get all function arguments for a given class (Parents Included)"""
    if not hasattr(cls, '__mro__'):
        return ()
    result = (_get_cls_method_args(cl, func_name) for cl in cls.__mro__)  # getting all __init__ function for parent classes
    return tuple(set(reduce(lambda z, y: z + y,  result)))  # flatting the result


def _get_cls_init_args(cls: Type) -> Tuple[str]:
    """Get init function arguments for a given class (Child Only, Parents excluded)"""
    return tuple(name for name in _get_cls_method_args(cls, "__init__") if name not in ('self', 'args', 'kwargs'))


def _get_all_cls_init_args(cls: Type) -> Tuple[str]:
    """Get init function arguments for a given class (Parents Included)"""
    return _get_all_cls_method_args(cls, '__init__')


def _make_signature(names: List[str]) -> Signature:
    """Create a signature with given names"""
    return Signature(tuple(Parameter(name, Parameter.POSITIONAL_OR_KEYWORD) for name in names))


def _get_cls_methods(cls: type) -> List[Tuple[str, Any]]:
    """Get all class functions or methods"""
    return getmembers(cls, lambda i: isfunction(i) or ismethod(i))


def is_default_init(func: Callable) -> bool:
    """Check if the given function is default init function - object.__init__ -"""
    return signature(func) == signature(object.__init__)


def flatten(items: Iterable, ignore_types: Tuple[type] = (str, bytes)) -> Generator:
    """Flatting nested iterables into a single generator"""

    for x in items:
        if isinstance(x, Iterable) and not isinstance(x, ignore_types):
            yield from flatten(x)
        else:
            yield x


def sort_list_by_another(sortable: list, base: list) -> list:
    sortable.sort(key=dict(zip(sortable, base)).get)
    return sortable
