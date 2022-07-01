
def base_example():
    from py_structure.base import Structure
    from py_structure.fields import String, RangeNumber, Float

    class Stock(Structure):
        name = String()
        shares = RangeNumber(min_val=5, max_val=20)
        price = Float()

    stock = Stock(name='product', shares=10, price=4.5)
    print(stock)


def decorators_example():
    from py_structure.decorators import debug_cls, timer_cls

    class Employee:
        def __init__(self, name, email, salary, url):
            self.name = name
            self.email = email
            self.salary = salary
            self.url = url

    @debug_cls
    class Employee1(Employee):
        pass

    @timer_cls
    class Employee2(Employee):
        pass

    employee = Employee1(name='align', email='mohamed@gmala.com', salary=4000, url='http://google.com')
    print(employee.name)
    employee.name = 'mohamed'
    print(employee.name, '\n')

    employee = Employee2(name='align', email='mohamed@gmala.com', salary=4000, url='http://google.com')
    print(employee.name)
    employee.name = 'mohamed'
    print(employee.name)


def fields_example():
    from py_structure.fields import Float, RangeNumber, Email, URL, typeassert, strucassert

    @typeassert(name=str, shares=RangeNumber(min_val=5, max_val=20), price=Float)
    class Stock:
        pass

    @strucassert(name=str, salary=RangeNumber(min_val=4000, max_val=10000), email=Email(), url=URL())
    class Employee:
        pass

    stock = Stock(name='product', shares=10, price=4.5, new_arg=410)
    print(stock)

    employee = Employee(name='mohamed', email="employee@gmail.com", url="http://google.com", salary=5000)
    print(employee)


def modes_example():
    from py_structure.modes import PrintMode, LogMode
    from py_structure.decorators import debug_cls

    class Employee:
        def __init__(self, name, email, salary, url):
            self.name = name
            self.email = email
            self.salary = salary
            self.url = url

    @debug_cls(model=PrintMode)
    class Employee1(Employee):
        pass

    @debug_cls(model=LogMode)
    class Employee2(Employee):
        pass

    employee = Employee1(name='align', email='mohamed@gmala.com', salary=4000, url='http://google.com')
    print(employee.name)
    employee.name = 'mohamed'
    print(employee.name, '\n')

    employee = Employee2(name='align', email='mohamed@gmala.com', salary=4000, url='http://google.com')
    print(employee.name)
    employee.name = 'mohamed'
    print(employee.name)


def multi_dispatch_example():
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
    try:
        s.bar(2, 'hello')  # will throw an error
    except TypeError:
        print('Warning!! function parameters types is not matched the annotations')


def protocols_example():
    from py_structure.protocols import Singleton

    class UniqueObj(metaclass=Singleton):
        def __init__(self, info):
            self.info = info

    a = UniqueObj('hello')
    b = UniqueObj('hello again')

    print(a is b)
    print(a == b)

    print(a.info)
    print(b.info)


def tools_example():
    from py_structure.tools import Counter, Timer

    @Counter
    def countdown(n):
        while n > 0:
            n -= 1

    def countdown2(n):
        while n > 0:
            n -= 1
            yield n

    c = Counter(func=countdown2)
    with c:
        for _ in range(100):
            c(5)
    print(c._count)

    c2 = Counter(func=countdown2)
    for _ in range(100):
        c2(5)
    print(c2._count)

    # Testing timer
    with Timer() as t:
        for _ in countdown2(100_000_000):
            if t.current_time > 0.5:
                print('it breaks')
                break
    print(t.elapsed)


def utilities_example():
    from py_structure.utilities import flatten

    nested_lst = [1, 4, 5, [4, [5, 8], 2], 6, 8]
    flatten_lst = [i for i in flatten(nested_lst)]

    print(nested_lst)
    print(flatten_lst)


def main():
    import argparse
    from inspect import currentframe, isfunction

    parser = argparse.ArgumentParser(description='Test Modules')
    parser.add_argument('--func', type=str,  help='Function name to run')
    args = parser.parse_args()
    name = args.func

    methods = {k: v for k, v in currentframe().f_globals.items() if isfunction(v)}
    method = methods.get(f'{name}_example')

    if method is not None:
        method()
    elif str(name).strip().lower() == 'all':
        for nm, mth in methods.items():
            if nm.endswith('_example'):
                print(f'{nm.replace("_", " ").capitalize()} is currently running')
                mth()
                print('###############\n')
    else:
        print('Invalid function name.\nIn case you need to run all test cases type "all" ')


if __name__ == '__main__':
    main()
