"""
Py Structure Library
----------------------------

Data Structure library to represent custom fields throw descriptors protocol.
It allows to generate static types for objects in both initialization & during execution time.

:copyright: (c) 2022 Mohamed Gamal Mohamed.
:license: BSD 3-clause. See LICENSE for more details.
"""

from .base import StructureMeta, Structure
from .multi_dispatch import MultiMethodMeta
from .utilities import flatten, sort_list_by_another
from .tools import Timer, Counter, Cache, LazyCLass, lazyproperty
from .protocols import Descriptor, FrozenDescriptor, Validator, FrozenValidator, Singleton
from .fields import (
    Typed,
    Int, Float, Decimal, Positive, Negative, Range, Binary, Hex, Oct, Complex,
    String, SizedString, RegexString, Email, URL, Slug,
    DateTime,
    Choice,
    typeassert, strucassert
)


__title__ = 'Py Structure'
__version__ = '1.0.0'
__author__ = 'Mohamed Gamal Mohamed'
__contact__ = 'moha.gamal@nu.edu.eg'
__myrepo__ = 'https://github.com/mohamedgamalmoha'
__gitrepo__ = ''
__license__ = 'BSD 3-clause'
__copyright__ = 'Copyright 2022'

__all__ = [
    # Base Construction
    'Structure', 'StructureMeta',
    # Protocols
    'Descriptor', 'FrozenDescriptor', 'Validator', 'FrozenValidator', 'Singleton',
    # Num Fields
    'Typed', 'Int', 'Float', 'Decimal', 'Positive', 'Negative', 'Range', 'Binary', 'Hex', 'Oct', 'Complex',
    # Range Fields
    'IntRange', 'FloatRange', 'DecimalRange', 'BinaryRange', 'HexRange', 'OctRange', 'ComplexRange',
    # Str Fields
    'String', 'RegexString', 'SizedString', 'Email', 'URL', 'Slug',
    # Date / Time Fields
    'DateTime', 'DurationDateTime',
    # Mix Fields
    'PositiveInt', 'NegativeInt', 'PositiveFloat', 'NegativeFloat', 'PositiveDecimal', 'NegativeDecimal',
    # Multi Fields
    'Choice',
    # Decorator
    'typeassert', 'strucassert',
    # Multiple Dispatch with Function Annotations
    'MultiMethodMeta',
    # Tools
    'Timer', 'Counter', 'Cache',  'lazyproperty', 'LazyCLass',
    # Utilities
    flatten, sort_list_by_another
]


class PositiveInt(Int, Positive):
    """Positive Int Number"""


class NegativeInt(Int, Negative):
    """Negative Int Number"""


class PositiveFloat(Float, Positive):
    """Positive Float Number"""


class NegativeFloat(Float, Negative):
    """Negative Float Number"""


class PositiveDecimal(Decimal, Positive):
    """Positive Decimal Number"""


class NegativeDecimal(Decimal, Negative):
    """Negative Decimal Number"""


class IntRange(Int, Range):
    """Int Range Field"""


class FloatRange(Float, Range):
    """Float Range Field"""


class DecimalRange(Decimal, Range):
    """Decimal Range Field"""


class BinaryRange(Binary, Range):
    """Binary Range Field"""


class HexRange(Hex, Range):
    """Hex Range Field"""


class OctRange(Oct, Range):
    """Oct Range Field"""


class ComplexRange(Complex, Range):
    """Complex Range Field"""


class DurationDateTime(DateTime, Range):
    """Duration DateTime Field"""
