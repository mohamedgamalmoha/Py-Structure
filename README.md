# Py-Structure
**The package allows static typing during execution time.<br>**
It is built based on meta-programming and uses pure python functionality, no package is required to be installed.<br>
The package is currently in beta version. A lot of work including testing needs to be done to be released.

## How to use it
### Simplest way using typeassert
```
from py_structure.fields import RangeNumber, Float, typeassert

@typeassert(name=str, shares=RangeNumber(min_val=5, max_val=20), price=Float)
class Stock:
    ...
```

### Another simple way using strucassert
```
from py_structure.fields import RangeNumber, Email, URL, typeassert

@strucassert(name=str, salary=RangeNumber(min_val=4000, max_val=10000), email=Email(), url=URL())
class Employee:
    ...
```

### More Complex way to instruct detailed structure 
```
from py_structure.base import Structure
from py_structure.fields import RangeNumber, String, Float

class Stock(Structure):
    name = String()
    shares = RangeNumber(min_val=5, max_val=20)
    price = Float()
```

## Furthermore, checkout examples.py 
