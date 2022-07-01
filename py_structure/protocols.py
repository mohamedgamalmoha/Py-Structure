from typing import Any

from .utilities import _get_cls_init_args


class Descriptor:
    """Descriptors let objects customize attribute lookup, storage, and deletion."""

    def __init__(self, name: str = None, default: Any = None, init: bool = True, metadata: dict = None) -> None:
        """Initialization object with value."""
        self.name = name

        if not init and default is None:
            raise ValueError("default parameter should be passed or set init to false")

        self.init = init
        self.default = default
        self.metadata = metadata

    def __get__(self, instance, owner) -> Any:
        """Get object value."""
        return instance.__dict__.get(self.name)

    def __set__(self, instance, value) -> None:
        """Set object value."""
        # If the instance class was initialized and init attr is false, then set the value to default
        is_initialized = getattr(instance, '__is_initialized', False)
        if not is_initialized and not self.init:
            value = self.default
        instance.__dict__.update({self.name: value})

    def __delete__(self, instance) -> None:
        """Delete object value."""
        del instance.__dict__[self.name]

    def __repr__(self) -> str:
        """Descriptor class representation"""
        args = ', '.join(f"{name}={getattr(self, name, None)}" for name in _get_cls_init_args(self))
        return f'{type(self).__name__}({args})'

    def get_type_error_message(self) -> str:
        """Type Error Message"""
        return f"Invalid type of {self.name}"

    def get_value_error_message(self) -> str:
        """Value Error Message"""
        return f"Invalid value of {self.name}"


class FrozenDescriptor(Descriptor):
    """Frozen descriptor to freeze the value over execution time"""

    def __set__(self, instance, value) -> Any:
        """Set a value for object for first time, raise an error if it is already initialized"""
        old_value = self.__get__(instance, instance.__class__)
        if old_value is not None:
            raise AttributeError("Value cant be changed")
        super(FrozenDescriptor, self).__set__(instance, value)

    def __delete__(self, instance) -> Any:
        """Delete the value is denied"""
        raise AttributeError("Value cant be deleted")


class ValidatorMeta(type):
    """Guarantee that child class construct a __set__ method"""

    def __new__(mcs, name: str, bases: tuple, namespace: dict) -> Any:
        if '__set__' not in namespace:
            raise NotImplementedError(f'"__set__" methods should be implemented in class {name}')
        return super().__new__(mcs, name, bases, namespace)


class Validator(Descriptor, metaclass=ValidatorMeta):
    """Guarantee that child class construct a __set__ method"""

    def __set__(self, instance, value) -> Any:
        super(Validator, self).__set__(instance, value)


class FrozenValidator(FrozenDescriptor, metaclass=ValidatorMeta):
    """Guarantee that child class construct a __set__ method"""

    def __set__(self, instance, value) -> Any:
        super(FrozenValidator, self).__set__(instance, value)


class Singleton(type):
    """Singleton protocol to create only one instance of a class during the whole lifetime of a program"""

    def __init__(cls, *args, **kwargs):
        cls.__instance = None
        super().__init__(*args, **kwargs)
        # call the post init if it is existed
        if hasattr(cls, '__post_init__'):
            cls.__post_init__(cls)

    def __call__(cls, *args, **kwargs):
        # in case of the instance is not none, return the same instance without creating new one
        if cls.__instance is not None:
            return cls.__instance
        # in case the instance is none, create new one then return it
        cls.__instance = super(Singleton, cls).__call__(*args, **kwargs)
        return cls.__instance


class Proxy:
    """Proxy protocol allows to provide the replacement for an another object.
    Through using different classes to represent the functionalities of another one."""

    def __init__(self, obj):
        """Initialize the class with given object"""
        self._obj = obj

    def __getattr__(self, name):
        """Get a value for a given key name"""
        return getattr(self._obj, name)

    def __setattr__(self, name, value):
        """Set a value for a given key name"""
        if name.startswith('_'):
            super().__setattr__(name, value)
        else:
            setattr(self._obj, name, value)

    def __delattr__(self, name):
        """Delete a value for a given key name"""
        if name.startswith('_'):
            super().__delattr__(name)
        else:
            delattr(self._obj, name)
