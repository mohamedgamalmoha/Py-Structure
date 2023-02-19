import time
import weakref
from typing import Any, Callable

from .utilities import _get_cls_methods_to_property


class Timer:
    """Timer used to calculate time during execution, used as decorator.

    .param:
        elapsed: float   -> total time consumed
        _timer: Callable -> timer function
        _start: float    -> started time
    """

    elapsed: float = 0.0
    _timer: Callable = time.perf_counter
    _start: float = None

    @property
    def started(self) -> bool:
        """Check whether the timer is started or not."""
        return self._start is not None

    @property
    def stopped(self) -> bool:
        """Check whether the timer is stopped or not."""
        return self.started and self.elapsed > 0.0

    @property
    def current_time(self) -> float:
        """Total time till the current invoking."""
        return self.elapsed + self._timer() - self._start

    def start(self) -> None:
        """Start the timer"""
        if self.started:
            raise RuntimeError('Already started')
        self._start = self._timer()

    def stop(self) -> None:
        """Stop the timer"""
        if self._start is None:
            raise RuntimeError('Not started')
        end = self._timer()
        self.elapsed += end - self._start
        self._start = None

    def reset(self) -> None:
        """Reset the timer"""
        self.elapsed = 0.0
        self._start = None

    def __enter__(self):
        """Start the timer when a context manager is invoked"""
        self.start()
        return self

    def __exit__(self, *args) -> None:
        """Stop the timer after context manager is terminated"""
        self.stop()


class Counter:
    """Count the number of invoking objects"""

    _count: int = 0

    def __init__(self, func: Callable) -> None:
        """Initialize the class with a given function / callable objects"""
        self._func = func

    @property
    def counted(self) -> bool:
        """Check whether it is invoked before not."""
        return self._count > 0

    def reset(self) -> None:
        """Rest the count numbers"""
        self._count = 0

    def run(self, *args, **kwargs) -> Any:
        """Execute the object with given args & kwargs"""
        self._count += 1
        return self._func(*args, **kwargs)

    def get_func(self) -> Callable:
        """Get real function"""
        return self._func

    def __call__(self, *args, **kwargs) -> Any:
        """Invoking the function """
        return self.run(*args, **kwargs)

    def __enter__(self, *args, **kwargs) -> None:
        """Count the number of invoking in a context manager"""
        # rest the counter in case of it is invoked before
        if self.counted:
            self.reset()

    def __exit__(self, *args) -> None:
        """Leaving the context manager """


class Cache(type):
    """Cache returns a cached reference to a previous instance created with the same arguments (if any). """

    def __init__(cls, *args, **kwargs):
        super().__init__(*args, **kwargs)
        cls.__cache = weakref.WeakValueDictionary()

    def __call__(cls, *args, **kwargs):
        if args in cls.__cache:
            return cls.__cache.get(args)
        obj = super().__call__(*args, **kwargs)
        cls.__cache.update({args: obj})
        return obj


class lazyproperty:
    """Lazy attribute, worked as a decorator"""

    def __init__(self, func):
        self.func = func

    def __get__(self, instance, cls):
        if instance is None:
            return self
        value = self.func(instance)
        setattr(instance, self.func.__name__, value)
        return value


class LazyCLass(type):
    """Change all attributes of class to be a lazy one."""

    def __new__(mcs, name: str, bases: tuple, namespace: dict) -> Any:
        cls = super().__new__(mcs, name, bases, namespace)
        for name, method in _get_cls_methods_to_property(cls):
            setattr(cls, name, lazyproperty(method))
        return cls
