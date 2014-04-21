import os
from nose.tools import raises
from sql_manager import SqlManager, TableAdder
from extra.testhelper.helpers import n_eq, n_ok

__author__ = 'Justin Jansen'
__status__ = 'Testing'
__date__ = '03/09/14'


"""
Precondition: All test for SqlManager
"""

db_name = 'Test.db'
existing_table_name = 'abc'


def setup_module():
    """
    Makes a database for testing in.
    """
    sql = SqlManager(db_name)
    command = 'CREATE TABLE %s (col_one text);' % existing_table_name
    sql.connect()
    sql._no_fetch_command(command)
    sql.disconnect()


@raises(NameError)
def test_ta_exists():
    """
    Checks it can find a table that exists
    """
    TableAdder(db_name, existing_table_name)


def test_ta_not_exists():
    """
    Checks that it raise a name error if the table does not exists
    """
    table_name = 'def'
    t = TableAdder(db_name, table_name)
    actual = t.done
    del t
    n_ok(not actual, message='Table not added yet')


def test_ta_add_column():
    """
    Checks that the column is added
    """
    table_name = 'def'
    expected = 'test_column'
    t = TableAdder(db_name, table_name)
    t.add_column(expected)
    actual = t.table_columns[0][0]
    n_eq(expected, actual, t, 'add_column', message='table still not added')


@raises(ValueError)
def test_ta_add_column_bad_type():
    """
    Checks that it rejects unknown types
    """
    table_name = 'def'
    t = TableAdder(db_name, table_name)
    t.add_column('the_name', 'the_type')


def test_ta_commit():
    """
    Checks that the table is added to the database
    @precondition: SqlManager all test - Pass
    """
    table_name = 'def'
    t = TableAdder(db_name, table_name)
    t.add_column('text_column')
    t.add_column('int_column', 'integer')
    t.commit()
    s = SqlManager(db_name)
    actual = table_name in s.tables
    n_ok(actual, t, 'commit', message='finally table added')


def teardown_module():
    """
    Deletes the testing database.
    """
    if os.path.isfile(db_name):
        os.remove(db_name)
