import gc
import inspect
from nose.tools import eq_, ok_

__author__ = 'Justin Jansen'
__version__ = '0.0.8'
__status__ = 'Development'
__date__ = '02/26/14'

# TODO switch this to kwargs
# TODO because i decided to switch to kwargs... i am not going to write the docs right now


def n_eq(expected, actual, class_object=None, method_name=None, message=None):
    """
    Just like the nose test eq_ method, except that it populates the output of failed tests with more information
    @param expected: expected results
    @param actual: actual results
    @param class_object: a string of the file name if a function and instance of the object if class
    @param method_name: the function or method name
    @param message: any other information that you want
    @return: A nicely formatted string with the test case docstring,
    the class method docstring, actual and expected result plus a message
    """
    output = '\n\n'
    frame = _get_frame()
    obj = _get_object(frame)
    output += "Test Case Docstring:\n" + _convert(inspect.getdoc(obj))
    if class_object and method_name:
        if type(class_object) == str:
            imp = "__import__('" + class_object + "', globals=globals())"
            x = eval(imp)
            output += "Function Docstring:\n" + _convert(inspect.getdoc(eval("x." + method_name)))
            del x
        else:
            output += 'Method Docstring:\n' + _convert(inspect.getdoc(eval("class_object." + method_name)))
    output += "Results:\n"
    output += "\t Expected: " + str(expected)
    output += "\n\t Actual: " + str(actual)
    if message:
        output += "\n\nMore Info:\n\t" + str(message)
    return eq_(expected, actual, output)


def n_ok(expected, class_object=None, method_name=None, message=None):
    """
    Just like nose test okay method but with more info
    @param expected: the expected results
    @param class_object: a string of the file name if a function and instance of the object if class
    @param method_name: the function or method name
    @param message: any other information that you want
    @return: A nicely formatted string with the test case docstring,
    the class method docstring, actual and expected result plus a message
    """
    output = '\n\n'
    frame = _get_frame()
    obj = _get_object(frame)
    output += "Test Case Docstring:\n" + _convert(inspect.getdoc(obj))
    if class_object and method_name:
        if type(class_object) == str:
            imp = "__import__('" + class_object + "', globals=globals())"
            x = eval(imp)
            output += "Function Docstring:\n" + _convert(inspect.getdoc(eval("x." + method_name)))
            del x
        else:
            output += 'Method Docstring:\n' + _convert(inspect.getdoc(eval("class_object." + method_name)))
    if message:
        output += "\n\nMore Info:\n\t" + str(message)
    return ok_(expected, output)


def _convert(to_convert):
    return '\t' + '\n\t'.join(str(to_convert).split('\n')) + '\n\n'


def _get_frame():
    methods = ['n_eq', 'n_ok', 'runTest']
    this_frame = inspect.currentframe()
    comp = None
    while not comp in methods:
        this_frame = this_frame.f_back
        comp = str(inspect.getframeinfo(this_frame)[2])
    return this_frame.f_back


def _get_object(frame):
    obj = None
    for o in gc.get_objects():
        if inspect.isfunction(o) and o.func_code is frame.f_code:
            obj = o
            break
    return obj


