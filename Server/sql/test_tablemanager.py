import os
from nose.tools import with_setup, raises
from extra.testhelper.helpers import n_eq, n_ok
from sql_manager import SqlManager, TableAdder, TableManager
from mock import patch

__author__ = 'Justin Jansen'
__status__ = 'Testing'
__date__ = '03/09/14'

"""
Precondition: All test for SqlManager passed
Precondition: All tests for TableAdder passed
"""

db_name = 'Test.db'
table_name = 'abc'
column_map = [('text_col', 'text'), ('int_col', 'integer')]


def setup_module():
    t = TableAdder(db_name, table_name)
    for val in column_map:
        t.add_column(val[0], val[1])
    t.commit()


def teardown_module():
    if os.path.isfile(db_name):
        os.remove(db_name)


def restore_setup():
    teardown_module()
    setup_module()


def test_tm_exists():
    """
    Tries to connect to a table that exists
    """
    t = TableManager(db_name, table_name)
    check_name = [val[0] for val in column_map]
    check_type = [val[1] for val in column_map]
    actual = check_name == t.table_col_names and check_type == t.table_col_type
    n_ok(actual, message='Checks table loaded correctly')


@raises(NameError)
def test_tm_not_exists():
    """
    Tries to connect to a table that does not exist
    """
    TableManager(db_name, 'not a table')


def test_tm_with_enter():
    """
    Checks that with enter is being called
    """
    with patch('Server.sql.sql_manager.TableManager.__enter__') as enter_mock:
        with TableManager(db_name, table_name):
            assert enter_mock.called


def test_tm_with_exit():
    """
    Checks that with exit is called when there are no errors
    """
    with patch('Server.sql.sql_manager.TableManager.__exit__') as exit_mock:
        with TableManager(db_name, table_name):
            pass
        assert exit_mock.called


def test_tm_with_exit_error():
    """
    Test that with exit will be called even if there is an error
    """
    with patch('Server.sql.sql_manager.TableManager.__exit__') as exit_mock:
        with TableManager(db_name, table_name) as t:
            t.push([i for i in range(10)])
        assert exit_mock.called


def test_tm_good_quick_push():
    """
    @precondition: test_tm_with_enter passed
    @precondition: test_tm_with_exit passed
    @precondition: test_tm_with_exit_error passed
    Checks that data is being written with a good push
    """
    expected = ['abc', 1]
    with TableManager(db_name, table_name) as t:
        t.quick_push(expected)
    s = SqlManager(db_name)
    s.connect()
    values = s._fetch_command('SELECT * FROM ' + table_name + ';')
    s.disconnect()
    values = values[0]
    actual = []
    expected = ['abc', 1]
    for val in values:
        if type(val) == int:
            val = int(val)
        else:
            val = str(val)
        actual += [val]
    message = 'Expected: ' + str(expected) + '\n' + 'Actual' + str(actual)
    n_eq(expected, actual, message=message)


@raises(ValueError)
def test_tm_bad_quick_push():
    """
    @precondition: test_tm_with_enter passed
    @precondition: test_tm_with_exit passed
    @precondition: test_tm_with_exit_error passed
    Checks that the push is rejected when the data is wrong
    """
    with TableManager(db_name, table_name) as t:
        t.quick_push([i for i in range(5)])


def test_tm_clear_table():
    """
    @precondition: test_tm_with_enter passed
    @precondition: test_tm_with_exit passed
    @precondition: test_tm_with_exit_error passed
    Tries to clear the table of all data
    """
    with TableManager(db_name, table_name) as t:
        t.clear_table()
    s = SqlManager(db_name)
    command = 'SELECT * FROM ' + table_name + ';'
    s.connect()
    data = s._fetch_command(command)
    s.disconnect()
    actual = False
    if len(data) == 0:
        actual = True
    n_ok(actual, message=actual)


def test_tm_sorted_good_push():
    """
    @precondition: test_tm_with_enter passed
    @precondition: test_tm_with_exit passed
    @precondition: test_tm_with_exit_error passed
    Tries to push a list where the columns are already in order with good info
    """
    push = [('text_col', 'one'), ('int_col', 1)]
    with TableManager(db_name, table_name) as t:
        t.push(push)
    s = SqlManager(db_name)
    command = 'SELECT * FROM ' + table_name + ';'
    s.connect()
    data = s._fetch_command(command)
    s.disconnect()
    data = data[0]
    expected = [str(val[1]) for val in push]
    actual = [str(val) for val in data]
    n_eq(expected, actual)


def test_tm_unsorted_good_push():
    """
    @precondition: test_tm_with_enter passed
    @precondition: test_tm_with_exit passed
    @precondition: test_tm_with_exit_error passed
    Tries to sort the list of good info and then push it.
    Also does type conversion
    """
    push = [('int_col', '1'), ('text_col', 'one')]
    with TableManager(db_name, table_name) as t:
        t.push(push)
    s = SqlManager(db_name)
    command = 'SELECT * FROM ' + table_name + ';'
    s.connect()
    data = s._fetch_command(command)
    s.disconnect()
    data = data[1]
    expected = [str(val[1]) for val in push][::-1]
    actual = [str(val) for val in data]
    n_eq(expected, actual)


@raises(ValueError)
def test_tm_push_bad_info():
    """
    @precondition: test_tm_with_enter passed
    @precondition: test_tm_with_exit passed
    @precondition: test_tm_with_exit_error passed
    I am not sure that value error is right
    Tries to push non matching data to the db
    """
    push = [('not a column', 'raise error'), ('text_col', 'one')]
    with TableManager(db_name, table_name) as t:
        t.push(push)


def test_tm_easy_pull():
    """
    @precondition: test_tm_quick_push passed
    @precondition: test_tm_with_enter passed
    @precondition: test_tm_with_exit passed
    @precondition: test_tm_with_exit_error passed
    Tries to pull all the columns where every type is text
    """
    testing_table = 'def'
    ta = TableAdder(db_name, testing_table)
    ta.add_column('col_one')
    ta.add_column('col_two')
    ta.commit()
    push = ['one', 'two']
    expected = ('one', 'two')
    with TableManager(db_name, testing_table) as t:
        t.quick_push(push)
        actual = t.pull()[0]
    n_eq(expected, actual)


# @with_setup(restore_setup)
def test_tm_medium_pull():
    """
    Tries to pull all the columns were there are different types
    """
    push = ['one', 1]
    with TableManager(db_name, table_name) as t:
        t.quick_push(push)
        expected = ('one', 1)
        actual = t.pull()[0]
    n_eq(expected, actual)


def test_hard_pull():
    """
    @precondition: test_tm_quick_push passed
    @precondition: test_tm_with_enter passed
    @precondition: test_tm_with_exit passed
    @precondition: test_tm_with_exit_error passed
    Tries to some of the columns and have different types
    """
    testing_table = 'ghi'
    ta = TableAdder(db_name, testing_table)
    ta.add_column('col_one')
    ta.add_column('col_two', 'integer')
    ta.add_column('col_three')
    ta.add_column('col_four')
    ta.commit()
    push = ['one', 2, 'three', 'four']
    cl = ['col_one', 'col_two']
    expected = ('one', 2)
    with TableManager(db_name, testing_table) as t:
        t.quick_push(push)
        actual = t.pull(cl)[0]
    n_eq(expected, actual)


def test_pull_where():
    """
    This one test should cover all operators
    @precondition: test_tm_quick_push passed
    @precondition: test_tm_with_enter passed
    @precondition: test_tm_with_exit passed
    @precondition: test_tm_with_exit_error passed
    """
    with TableManager(db_name, table_name) as t:
        t.clear_table()
        for i in range(9):
            text = 'one_%d' % i
            t.quick_push([text, i])
        expected = []
        for i in range(5, 9):
            text = 'one_%d' % i
            expected += [(text, i)]
        value = column_map[1][0]
        compare_to = 5
        op = '>='
        actual = t.pull_where(value, compare_to, op)
    n_eq(expected, actual)


