from typing import Any, Tuple
from collections import OrderedDict

from .protocols import Descriptor, FrozenDescriptor


def _make_init(fields_names: Tuple[str]) -> str:
    """Generate code for init function"""
    # first part of __init__ function
    code = f"def __init__(self, {', '.join(fields_names)}):\n"
    # adding fields with the rest of the code
    for field in fields_names:
        code += f"   self.{field} = {field}\n"
    return code


def _make_init_with_descriptors(fields: Tuple[Tuple[str, Descriptor]]) -> str:
    """"Generate code for init function with regarding of none initialized fields"""

    # get required initialized fields in tuple, and none required in dict
    required_fields = tuple(k for k, v in fields if v.init is True)
    none_required_fields = {k: v for k, v in fields if v.init is False}

    # generate code with required fields
    code = _make_init(required_fields)

    # add none required fields to the generated code
    for name, dec in none_required_fields.items():
        # get type default class name
        typ_name = type(dec.default).__name__
        # concatenating none required field with other code
        code += f"   self.{name} = {typ_name}('{dec.default}')\n"
    return code


class StructureMeta(type):
    """Structure Meta responsible for handling the creation of new classes"""

    descriptor: Descriptor = Descriptor

    @classmethod
    def __prepare__(mcs, name: str, bases: tuple) -> dict:
        """Actual dictionary that stores class variables"""
        # OrderedDict is used rather than the regular Dict, cause it is indexed one.
        return OrderedDict()

    @classmethod
    def is_descriptor(mcs, val) -> bool:
        """Checking whether the give class is descriptor or not"""
        return isinstance(val, mcs.descriptor) or issubclass(type(val), mcs.descriptor)

    @classmethod
    def is_structure(mcs, val) -> bool:
        """Checking whether the give class is structure or not"""
        return isinstance(val, mcs) or issubclass(val, mcs)

    @classmethod
    def is_frozen_descriptor(mcs, val) -> bool:
        """Checking whether the give class is frozen descriptor or not"""
        return FrozenDescriptor in type(val).__mro__

    def __call__(cls, *args, **kwargs):
        obj = type.__call__(cls, *args, **kwargs)
        if hasattr(obj, '__post_init__'):
            # calling __post_init__ function after initialization if it is constructed in the child class
            post_init = getattr(obj, '__post_init__')
            post_init.__call__()
        return obj

    def __new__(mcs, name: str, bases: tuple, namespace: dict) -> Any:
        # init method need to be supported ###################################
        """Handling the creation of the base structure"""
        # get descriptors name and class as pair (name, descriptor) from parent classes
        # get name space of parent classes in case of being structure
        bases_namespace = [vars(base).items() for base in bases if mcs.is_structure(base)]
        # filtering name spaces to get only descriptors
        bases_descriptors = [{k: v for k, v in base if mcs.is_descriptor(v)} for base in bases_namespace]
        # checking whether the len of bases_descriptors is zero or not
        total_namespace = bases_descriptors[0] if bases_descriptors else {}
        # update total namespaces with current namespace
        total_namespace.update(namespace.items())
        # assigning total namespace to name space
        namespace = total_namespace

        # get descriptor name and class as pair (name, descriptor class) for current class
        items = tuple(filter(lambda pair: mcs.is_descriptor(pair[1]), namespace.items()))
        # get descriptor classes only
        descriptors = tuple(descriptor for _, descriptor in items)
        # get descriptor names only as strings
        fields = tuple(_name for _name, _ in items)
        if fields:
            # initialize class with fields - descriptors` names -
            exec(_make_init_with_descriptors(items), globals(), namespace)

        for name in fields:
            # setting the attribute name of descriptor to corresponding name in parent class, for example:
            # Class NewStructure(Structure):
            #   field = Descriptor()
            # so, we are setting "Descriptor.name = field"
            setattr(namespace.get(name), 'name', name)

        cls = super().__new__(mcs, name, bases, namespace)
        setattr(cls, 'fields', fields)
        setattr(cls, '__descriptors', descriptors)
        setattr(cls, '__is_initialized', True)
        return cls


class Structure(metaclass=StructureMeta):
    """
    Base Structure for representing different data types


    Example Usage:
        class Employee(Structure):
            name = String(init=False, default='none')
            salary = RangeNumber(min_val=4000, max_val=10000, init=False, default=5000)
            email = Email()
            url = URL()

        employee = Employee("employee@gmail.com", "http://google.com")

        print(a.get_fields_name())  # names of all fields
        print(a.get_all_fields())  # descriptor of all fields
        print(a.get_all_fields_name())  # name & descriptor zipped together
        print(a.get_frozen_fields())  # frozen fields as descriptor
    """

    fields: Tuple[str]
    __descriptors = Tuple[Descriptor]

    def __post_init__(self) -> None:
        """Function runs after the initialization of the class to deliver custom behavior"""
        pass

    def __repr__(self) -> str:
        """Structure class representation"""
        args = ', '.join(repr(getattr(self, name)) for name in self.fields)
        return f'{self.__class__.__name__}({args})'

    def get_fields_name(self) -> Tuple[str]:
        """Get fields names, variables names of descriptors"""
        return self.fields

    def get_all_fields(self) -> Tuple[Descriptor]:
        """Get descriptors classes"""
        return getattr(self, '__descriptors', ())

    def get_all_fields_name(self) -> Tuple[Tuple[str, Descriptor]]:
        """Get fields name with corresponding descriptors class"""
        return tuple(zip(self.get_fields_name(), self.get_all_fields()))

    def get_frozen_fields(self) -> Tuple[Descriptor]:
        """Get frozen fields"""
        return tuple(filter(self.is_frozen_descriptor, self.get_all_fields()))

    is_descriptor = StructureMeta.is_descriptor
    is_frozen_descriptor = StructureMeta.is_frozen_descriptor
