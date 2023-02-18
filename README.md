# Py-Structure
**The package allows static typing during execution time.<br>**
It is built based on meta-programming and uses pure python functionality, no package is required to be installed.<br>
It also supports different tools and functions such as multi dispatch, decorators, ... etc.<br>
The package is currently in beta version. A lot of work including testing needs to be done to be released.

# How to use it

-----------------------------------------------
## Struct Examples
### Simplest way using typeassert
```python
from py_structure.fields import Range, Float, typeassert

@typeassert(name=str, shares=Range(min_val=5, max_val=20), price=Float)
class Stock:
    ...
```

It is a lite way to construct a class similar to Structure, but it has some limitations showed in warnings.
<p style='color:red'>Warnings & Notes:</p>

- Inheritance is supported, but using same decorator for children is not applicable.
```python
from py_structure.fields import Range, String, Email, URL, typeassert

@typeassert(name=String, salary=Range(min_val=4000, max_val=10000), email=Email(), url=URL())
class Employee:
    ...

# Working example
class UpdatedEmployee(Employee):
    ...

# None Working example, throws RecursionError: maximum recursion depth exceeded
@typeassert(permission=str)
class UpdatedEmployee2(Employee):
    ...
```

- It doesn't support default values of descriptors, use Structure class from base instead.
- In case the __init__ function is constructed in the class, it needs to support multi args and kwargs.
```python
def __init__(self, *args, **kwargs):
    ...
```

### Another simple way using strucassert
typeassert decorator to guarantee static typing, descriptors and built in types are allowed.<br>
```python
from py_structure.fields import Range, Email, URL, typeassert

@strucassert(name=str, salary=Range(min_val=4000, max_val=10000), email=Email(), url=URL())
class Employee:
    ...
```

<p style='color:red'>Warnings & Notes:</p>

- Inheritance is supported, but using same decorator for children is not applicable. 
- It supports default values of descriptors.

### More Complex way to instruct detailed structure 
```python
from py_structure.base import Structure
from py_structure.fields import Range, String, Float, Email, URL

class Stock(Structure):
    name = String()
    shares = Range(min_val=5, max_val=20)
    price = Float()
    
 class Employee(Structure):
    name = String(init=False, default='none')
    salary = Range(min_val=4000, max_val=10000, init=False, default=5000)
    email = Email()
    url = URL()
```

<p style='color:red'>Warnings & Notes:</p>

- Inheritance is supported. 
- It supports default values of descriptors.
- It supports different methods

```python
# creating instance from previous example
employee = Employee("employee@gmail.com", "http://google.com")

# names of all fields
print(employee.get_fields_name())

# descriptor of all fields
print(employee.get_all_fields())
# name & descriptor zipped together

print(employee.get_all_fields_name())
# frozen fields as descriptor
print(employee.get_frozen_fields())  
```

Base Structure i useful for representing different data types

-----------------------------------------------

## Multi-Dispatch Examples
Metaclass that allows multiple dispatch of methods with different annotations.<br>
When the method is called, the class invokes the method which has annotations that 
follow the parameter types. In case of the parameters\` types don't follow any methods` annotations, an error will be thrown.

```python
from py_structure.multi_dispatch import MultiMethodMeta

class Spam(metaclass=MultiMethodMeta):
    def bar(self, x: int, y: int):
        print('Bar 1:', x, y)

    def bar(self, s: str, n: int = 0):
        print('Bar 2:', s, n)

s = Spam()
s.bar(2, 3)
s.bar('hello')  
s.bar('hello', 5)
s.bar(2, 'hello')  # will throw an error
 ```
-----------------------------------------------
## Protocols & Patterns

Different protocols and patterns were implemented for a variety of use.<br>

### Descriptor
It is used for constructing fields that used in structure.

```python
from py_tructure.fileds import( 
    Typed,
    Int, Float, Decimal, Positive, Negative, Range, Binary, Hex, Oct,
    PositiveInt, NegativeInt, PositiveFloat, NegativeFloat, PositiveDecimal, NegativeDecimal,
    String, SizedString, RegexString, Email, URL, Slug,
    DateTime,
    Choice
    )
```

### FrozenDescriptor
It is used for constructing frozen fields that used in structure.<br>
The frozen descriptor ensures that the value wouldn't be changed during execution time.<br>
Corresponding to keyword **static** in other languages.

```python
from py_structure.fields import typeassert
from py_structure.protocols import FrozenDescriptor

class FrozenString(FrozenDescriptor):
    """ Frozen String Field """
    typ: type = str

    def __set__(self, instance, value):
        if not isinstance(value, self.typ):
            raise TypeError("Invalid Type, It should be String")
        super(FrozenString, self).__set__(instance, value)

        
@typeassert(name=FrozenString)
class Employee:
    ...
```

### Singleton
A Singleton pattern allows creating just one instance of a class during the execution time.

```python
from py_structure.protocols import Singleton

class UniqueClass(metaclass=Singleton):
    ...

a = UniqueClass()
b = UniqueClass()

print(a is b)
print(a == b)
```

### Proxy
Proxy protocol allows to provide the replacement for another object. Through using different classes to represent the functionalities of another one.
```python
from py_structure.protocols import Proxy

class First: 
    def __init__(self, name: str):
        self.name = name 

a = First('a') 
p = Proxy(a) 

print(p.name)
```

-----------------------------------------------
## Tools
Different tools and context managers were implemented for a variety of use.<br>

### Timer
Timer used to calculate time during execution, used as decorator and context manager
```python
from py_structure.tools import Timer

TIME_LIMIT = 0.5

def countdown(n):
    while n > 0:
        n -= 1
        yield n

with Timer() as t:
    for _ in countdown(100_000_000):
        if t.current_time > TIME_LIMIT:
            print(f'Can`t exceed the time limit ({TIME_LIMIT})')
            break
            
print(t.elapsed)
```

### Counter
Count the number of invoking objects, used as decorator and context manager
```python
from py_structure.tools import Counter

c = Counter(func=countdown)

with c:
    for _ in range(100):
        c(5)

print(c._count)
```

### Cache 
It returns a cached reference to a previous instance created with the same arguments (if any).

```python
from py_structure.tools import Cache

class CachedCls(metaclass=Cache):
    def __init__(self, name: str):
        self.name = name

a = CachedCls('a')
b = CachedCls('b')
```

### Lazy Attribute
Turn attribute into lazy ones, useful for highly computational invoking, used as a decorator or metaclass

```python
from py_structure.tools import lazyproperty

class Compute:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        
    @lazyproperty
    def mult(self):
        print('Multiply x & y')
        return self.x * self.y
    
    @lazyproperty
    def div(self):
        print('Divide x by y')
        return self.x / self.y
    
c = Compute(10, 5)
print(c.mult())
print(c.div())

```
The ``LazyCLass`` could be used to turn all methods into lazy ones,instead of manually writing decorators for all methods ``Compute(metaclass=LazyCLass)``

-----------------------------------------------
## Utilities

### Flatten 
Flatt nested iterable into one sequence, used as normal function
```python
from py_structure.utilities import flatten

nested_lst = [1, 4, 5, [4, [5, 8], 2], 6, 8]
flatten_lst = [i for i in flatten(nested_lst)]

print(nested_lst)
print(flatten_lst)
```

### Dependency Sort
Sort an iterable based on another
```python
from py_structure.utilities import sort_list_by_another

base = [1, 2, 4, 3, 5]
lst = [10, 12, 7, 11, 9]

print(sort_list_by_another(lst, base))
```
