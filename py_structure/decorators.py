import time
from functools import wraps, partial
from typing import Callable, Any, Type

from .modes import BaseMode, PrintMode
from .utilities import _get_cls_methods


def timer(func: Callable = None, prefix: str = None, model: BaseMode = PrintMode, run_model: bool = True) -> Any:
    """Calculate execution time for a function"""

    if func is None:
        return partial(timer, prefix=prefix, model=model, run_model=run_model)

    @wraps(func)
    def wrap_func(*args, **kwargs):
        t1 = time.perf_counter()
        result = func(*args, **kwargs)
        t2 = time.process_time()
        if run_model:
            mod = model.__call__()
            mod.case_info(msg=f'{prefix} Function {func.__name__}\t Executed in {(t2 - t1):.4f}s')
        return result
    return wrap_func


def debug(func: Callable = None, *, prefix: str = '',  model: BaseMode = PrintMode, run_model: bool = True) -> Any:
    """Execute function in debug mode. When it throws an error, it ignores and print the error"""

    if func is None:
        return partial(debug, prefix=prefix, model=model, run_model=run_model)

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            if run_model:
                mode = model.__call__()
                mode.case_info(f'{prefix} Function {func.__name__} \t Invoked Successfully')
        except Exception as e:
            if run_model:
                mode = model.__call__()
                mode.case_info(f'{prefix} Function {func.__name__} \t Invoked Unsuccessfully  \t Error: {e}')
        else:
            return result
    return wrapper


def decorate_func(main_func: Callable = None, decorated_fuc=None, model: BaseMode = PrintMode,
                  run_model: bool = True) -> Any:
    """Calculate execution time for a function"""

    if main_func is None:
        return partial(timer, decorated_fuc=decorated_fuc, model=model, run_model=run_model)

    @wraps(decorated_fuc)
    def wrap_func(*args, **kwargs):
        model().case_info(f'Function {main_func.__name__} \t is currently invoked')
        result = main_func(*args, **kwargs)
        model().case_info(f'Function {decorated_fuc.__name__} \t is currently invoked')
        decorated_fuc()
        return result
    return wrap_func


def decorate_cls(cls: Type = None, func: Callable = debug, model: BaseMode = PrintMode,
                 run_model: bool = True, *args, **kwargs) -> Any:
    """Decorate all class` methods with certain function"""

    if cls is None:
        return partial(decorate_cls, func=func, *args, **kwargs)
    for name, method in _get_cls_methods(cls):
        setattr(cls, name, func(method, model=model, run_model=run_model, *args, **kwargs))
    return cls


def debug_cls(cls: Type = None, *, prefix: str = '', model: BaseMode = PrintMode, run_model: bool = True) -> Any:
    """Execute classes` methods in debug mode. When it throws an error, it ignores and print the error.
    It does not work with class method & staticmethod
    """
    if cls is None:
        return partial(timer_cls, prefix=prefix, model=model, run_model=run_model)

    return decorate_cls(cls, func=debug, prefix=f"{prefix}Class {cls.__name__}:\t",  model=model, run_model=run_model)


def timer_cls(cls: Type = None, prefix: str = None, model: BaseMode = PrintMode, run_model: bool = True) -> Any:
    """Calculate exception time for all class` methods"""
    if cls is None:
        return partial(timer_cls, prefix=prefix, model=model, run_model=run_model)

    return decorate_cls(cls, func=timer, prefix=prefix or f"Class { cls.__name__}:\t", model=model, run_model=run_model)


def static_type(func:  Callable = None, model: BaseMode = PrintMode, run_model: bool = True) -> Any:
    """Validating function`s argument to follow the annotation.
    Sported with function that have kwargs only.
    """

    if func is None:
        return partial(static_type, model=model, run_model=run_model)

    @wraps(func)
    def wrapper(**kwargs):
        annotations = getattr(func, '__annotations__')

        if annotations.keys() != kwargs.keys():
            raise ValueError("Annotations and kwargs should be same length")

        for k, v in kwargs.items():
            ann_typ = annotations.get(k)
            if ann_typ is not type(v):
                raise ValueError(f"{k} type is not same as its annotation, should be {ann_typ}")

        return func(**kwargs)
    return wrapper
