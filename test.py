import unittest
import warnings


class BaseTest(unittest.TestCase):

    def setUp(self) -> None:
        warnings.simplefilter('ignore', category=DeprecationWarning)


class TestFields(BaseTest):

    def test_simple_fields(self):
        from py_structure.fields import (
            Int, Float,
            String,
            typeassert
        )

        @typeassert(name=String(), identifier=Int(), price=Float())
        class Stock:
            ...

        stock = Stock(name='first product', identifier=1, price=4.5)

        with self.assertRaises(TypeError):
            stock.name = 12
            stock.identifier = '12'
            stock.price = 4

    def test_complex_fields(self):
        from py_structure import PositiveInt
        from py_structure.fields import (
            Range,
            SizedString, Email, URL,
            Choice,
            typeassert
        )

        @typeassert(name=str, identifier=SizedString(max_len=5), email=Email(),  url=URL(),
                    salary=Range(min_val=4000, max_val=10000), role=Choice(choices=('manager', 'worker')))
        class Employee:
            ...

        employee = Employee(name='Student', identifier='12345', email='employee@gmail.com', url='https://google.com',
                            salary=5000, role='manager')

        with self.assertRaises(ValueError):
            employee.identifier = '123'
            employee.salary = 2000

        @typeassert(name=SizedString(max_len=10), class_num=PositiveInt())
        class Student:
            ...

        student = Student(name='Student', class_num=10)

        with self.assertRaises(ValueError):
            student.class_num = -10

    def test_field_range(self):
        from py_structure.fields import (
            Int,
            Range,
            typeassert
        )

        class IntRange(Int, Range):
            ...

        @typeassert(name=str, score=IntRange(min_val=1, max_val=100))
        class StudentScore:
            ...

        student = StudentScore(name='student', score=90)

        with self.assertRaises(ValueError):
            student.score = 150

    def test_field_duration_date_time(self):
        from datetime import datetime, timedelta
        from py_structure import DurationDateTime
        from py_structure.fields import typeassert

        now = datetime.now()
        end = now + timedelta(hours=2)

        @typeassert(name=str, duration=DurationDateTime(min_val=now, max_val=end))
        class Task:
            ...

        task = Task(name='Task 1', duration=now+timedelta(hours=1))

        with self.assertRaises(ValueError):
            task.duration = now + timedelta(hours=4)


class TestProtocols(BaseTest):

    def test_singleton(self):
        from py_structure.protocols import Singleton

        class UniqueObj(metaclass=Singleton):
            def __init__(self, info):
                self.info = info

        a = UniqueObj('hello')
        b = UniqueObj('hello again')

        self.assertEqual(a.info, b.info)
        self.assertEqual(a, b)

    def test_proxy(self):
        from py_structure.protocols import Proxy

        class Obj:
            def __init__(self, info):
                self.info = info

        obj = Obj('Nice')
        proxy_obj = Proxy(obj)

        self.assertEqual(obj.info, proxy_obj.info)
        proxy_obj.info = 'New'
        self.assertEqual(obj.info, proxy_obj.info)


class TestTools(BaseTest):

    def setUp(self) -> None:
        super().setUp()

        def countdown(n):
            while n > 0:
                n -= 1
                yield n

        self.countdown = countdown

    def test_timer(self):
        from py_structure.tools import Timer

        TIME_BREAK = 0.50000

        with Timer() as t:
            for _ in self.countdown(100_000_000):
                # break if the time exceeds 0.5
                if t.current_time >= TIME_BREAK:
                    break

        self.assertAlmostEqual(t.elapsed, TIME_BREAK, places=4)

    def test_counter(self):
        from py_structure.tools import Counter

        EXECUTION_COUNT = 100

        c1 = Counter(func=self.countdown)
        with c1:
            for _ in range(EXECUTION_COUNT):
                c1(5)

        c2 = Counter(func=self.countdown)
        for _ in range(EXECUTION_COUNT):
            c2(5)

        self.assertEquals(c1._count, c2._count)

    def test_cache(self):
        from py_structure.tools import Cache

        class CashedObj(metaclass=Cache):
            def __init__(self, name):
                self.name = name

        obj_1 = CashedObj('First')
        obj_2 = CashedObj('Second')
        obj_3 = CashedObj('Second')

        self.assertNotEqual(obj_1, obj_2)
        self.assertNotEqual(obj_1, obj_3)
        self.assertEqual(obj_2, obj_3)

    def test_lazyproperty(self):
        import math
        import time
        from py_structure.tools import lazyproperty

        class Point:

            def __init__(self, x, y):
                self.x = x
                self.y = y

            @lazyproperty
            def factorial_x(self):
                return math.factorial(self.x)

            @lazyproperty
            def factorial_y(self):
                return math.factorial(self.y)

        p = Point(x=4, y=5)
        start = time.perf_counter()
        f1 = p.factorial_x
        middle = time.perf_counter()
        f2 = p.factorial_x
        end = time.perf_counter()

        self.assertEqual(f1, f2)
        self.assertTrue(middle - start > end - middle)

    def test_lazyclass(self):
        import math
        import time
        from py_structure.tools import LazyCLass

        class Circle(metaclass=LazyCLass):

            def __init__(self, radius):
                self.radius = radius

            def area(self):
                return math.pi * self.radius ** 2

            def perimeter(self):
                return 2 * math.pi * self.radius

        c = Circle(radius=4.0)
        start = time.perf_counter()
        a1 = c.area
        middle = time.perf_counter()
        a2 = c.area
        end = time.perf_counter()

        self.assertEqual(a1, a2)
        self.assertTrue(middle - start > end - middle)


class TestMultiDispatcher(BaseTest):

    def test_dispatcher(self):
        import time
        from py_structure.multi_dispatch import MultiMethodMeta

        class Date(metaclass=MultiMethodMeta):

            def __init__(self, year: int, month: int, day: int):
                self.year = year
                self.month = month
                self.day = day

            def __init__(self):
                t = time.localtime()
                self.__init__(t.tm_year, t.tm_mon, t.tm_mday)

            def __eq__(self, other):
                return self.year == other.year and self.month == other.month and self.day == other.day

        now = time.localtime()
        obj_1 = Date(now.tm_year, now.tm_mon, now.tm_mday)
        obj_2 = Date()

        self.assertEquals(obj_1, obj_2)


class TestUtilities(BaseTest):

    def test_flatten(self):
        from py_structure.utilities import flatten

        lst = (0, 1, 2, 3, 4, 5)
        nested_lst = (0, (1, 2), (3, (4, 5)))
        flatten_lst = tuple(i for i in flatten(nested_lst))

        self.assertEqual(flatten_lst, lst)

    def test_sort_list_by_another(self):
        from py_structure.utilities import sort_list_by_another

        X = ["a", "b", "c", "d", "e", "f", "g", "h", "i"]
        Sorted_X = ['a', 'd', 'h', 'b', 'c', 'e', 'i', 'f', 'g']
        Y = [0, 1, 1, 0, 1, 2, 2, 0, 1]

        sort_list_by_another(X, Y)

        self.assertEqual(X, Sorted_X)


class TestDecorators(BaseTest):

    def test_decorators_with_modes(self):
        from py_structure.modes import LogMode
        from py_structure.decorators import timer_cls

        @timer_cls(model=LogMode)
        class Employee:

            def __init__(self, name):
                self.name = name

            def get_name(self):
                return self.name

            def set_name(self, value):
                self.name = value
                return self.name

        employee = Employee(name='name')
        employee.get_name()
        employee.set_name('new name')
        employee.get_name()


if __name__ == '__main__':
    unittest.main()
