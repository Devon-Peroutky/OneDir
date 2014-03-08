__author__ = 'justin'

from extra.testhelper.helpers import n_eq, n_ok
from extra.testhelper.example_file import Foo, baz

def test_method():
    """
    Testing the method bar in Class Foo
    This will be printed
    """
    foo = Foo()
    n_eq(1,foo.bar(), foo, 'bar', 'Added info will be printed')


def test_function():
    """
    Testing baz from example file
    This will be printed
    """
    n_ok(baz(), 'example_file', 'baz', 'Added info will be printed')