import os
import sqlite3 as lite
from sql_manager import SqlManager
from extra.testhelper.helpers import n_eq, n_ok

__author__ = 'Justin Jansen'
__status__ = 'Testing'
__date__ = '03/08/14'

"""
All tests here are passing.
Feel free to add whatever you want.

Coverage will be ran when test table managers is completed
"""


class SetupError(Exception):
    """
    If setup module fails this will be raised and it will stop the tests
    from being run.
    """
    pass


db_name = 'Testing.db'
table_name = 'abc'


def setup_module():
    """
    Creates a simple table and adds enough information to run following tests
    """
    failed = False
    con = None
    try:
        con = lite.connect(db_name)
        cur = con.cursor()
        command = 'CREATE TABLE %s (col_one text, col_two text, col_three text);' % table_name
        cur.execute(command)
        con.commit()
        command = 'INSERT INTO %s VALUES("one", "two", "three");' % table_name
        cur.execute(command)
        con.commit()
    except lite.DatabaseError, e:
        print e.message
        failed = True
    finally:
        if con:
            con.close()
    if failed:
        raise SetupError('')


def test_sm_connect_new_db():
    """
    Tries to connect to a db that does not exists
    """
    db = 'test_2.db'
    s = SqlManager(db)
    actual = os.path.isfile(db)
    if actual:
        os.remove(db)
    del s
    n_ok(actual, message='test_2.db was not created')


def test_sm_connect_existing_db():
    """
    Tries to connect to a db that already exists
    """
    s = SqlManager(db_name)
    s.connect()
    actual = s.con is None
    s.disconnect()
    n_ok(not actual, s, 'connect')


def test_sm_disconnect():
    """
    Checks that the db is disconnecting properly
    """
    s = SqlManager(db_name)
    s.connect()
    s.disconnect()
    actual = s.con is None
    n_ok(actual, s, 'disconnect')


def test_sm_pull_tables():
    """
    Checks that pull tables is retrieving all the tables
    """
    s = SqlManager(db_name)
    actual = s.tables[0]
    expected = table_name
    n_eq(expected, actual, s, '_pull_tables')


def test_sm_fetch_command():
    """
    Checks that the db can run a fetch command
    """
    command = 'SELECT * FROM %s;' % table_name
    s = SqlManager(db_name)
    s.connect()
    data = s._fetch_command(command)[0]
    s.disconnect()
    actual = [str(col) for col in data]
    expected = ['one', 'two', 'three']
    n_eq(expected, actual, s, '_fetch_command')


def test_sm_no_fetch_command():
    """
    Checks that the table can run a no fetch command
    """
    expected = ['a', 'b', 'c']
    command = 'INSERT INTO %s VALUES(%s);' % (table_name, str(expected)[1:-1])
    s = SqlManager(db_name)
    s.connect()
    s._no_fetch_command(command)
    s.disconnect()
    con = lite.connect(db_name)
    cur = con.cursor()
    command = 'SELECT * FROM %s;' % table_name
    cur.execute(command)
    fetched = cur.fetchall()
    fetched = fetched[1]
    actual = [str(col) for col in fetched]
    n_eq(expected, actual, s, '_no_fetch_command', message='Good chance that I did not setup test right')


def teardown_module():
    """
    Deletes the table after tests have been completed
    """
    if os.path.isfile(db_name):
        os.remove(db_name)