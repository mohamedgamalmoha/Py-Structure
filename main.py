from py_structure.base import Structure
from py_structure.fields import String, Int, Float, RangeNumber, Email, URL, typeassert, strucassert
from py_structure.modes import PrintMode
from py_structure.decorators import timer, timer_cls, debug_cls


@typeassert(name=str, shares=RangeNumber(min_val=5, max_val=20), price=Float)
class Stock:
    ...


# @timer_cls(model=PrintMode)
class Stock2(Structure):
    name = String()
    shares = RangeNumber(min_val=5, max_val=20)
    price = Float()


@typeassert(new_arg=int)
class Stock3(Stock):
    pass


class Employee(Structure):
    name = String(init=False, default='none')
    salary = RangeNumber(min_val=4000, max_val=10000, init=False, default=5000)
    email = Email()
    url = URL()


@typeassert(name=String, salary=RangeNumber(min_val=4000, max_val=10000), email=Email(), url=URL())
class Employee2:
    pass


@strucassert(name=str, salary=RangeNumber(min_val=4000, max_val=10000), email=Email(), url=URL())
class Employee3:
    ...


@strucassert(other=String)
class Employee4(Employee3):
    pass


class UpdatedEmployee(Employee2):
    pass


class UpdatedEmployee2(UpdatedEmployee):
    pass


@debug_cls
class Normal:
    name = String(name='name')
    email = Email(name='email')
    salary = RangeNumber(name='salary', min_val=4000, max_val=10000)
    url = URL()

    def __init__(self, name, email, salary, url):
        self.name = name
        self.email = email
        self.salary = salary
        self.url = url


@timer
def main():
    stock = Stock(name='product', shares=10, price=4.5)
    stock2 = Stock2(name='product', shares=10, price=4.5)
    stock3 = Stock3(name='product', shares=10, price=4.5, new_arg=410)
    print(stock3.new_arg)

    employee = Employee("employee@gmail.com", "http://google.com")
    employee2 = Employee2(name='mohamed', email="employee@gmail.com", url="http://google.com", salary=5000)
    employee3 = Employee4(name='mohamed', email="employee@gmail.com", url="http://google.com", salary=5000, other='yes')

    print(employee3.name)
    print(f"{employee3.other=}")
    print(getattr(employee3, '__descriptors', None))

    norm = Normal(name='mohamed', email="employee@gmail.com",  salary=5000, url="http://google.com")
    print(norm.name)
    print(norm.email)
    print(norm.url)


if __name__ == '__main__':
    main()
