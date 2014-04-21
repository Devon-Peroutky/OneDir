import os
from nose.tools import raises
# from extra.testhelper.helpers import n_ok
# from sql_manager import SqlManager, TableAdder, TableRemover
from helpers import n_ok
from OneDirServer.sql_manager import SqlManager, TableAdder, TableRemover


__author__ = 'Justin Jansen'
__status__ = 'Testing'
__date__ = '03/09/14'

"""
Precondition: All tests for SqlManager passed
Precondition: All tests for TableAdder passed
"""

db_name = 'Test.db'
table_name = 'abc'


def setup_module():
    t = TableAdder(db_name, table_name)
    t.add_column('test_column')
    t.commit()


def test_tr_exists():
    """
    Test it can remove a table that exists
    """
    s = SqlManager(db_name)
    if not table_name in s.tables:
        raise Exception('Bad Setup')
    del s
    TableRemover(db_name, table_name)
    s = SqlManager(db_name)
    actual = table_name in s.tables
    n_ok(not actual, message='table should be gone')


@raises(NameError)
def test_tr_not_exits():
    """
    @precondition: test_tr_exists passed
    Test that NameError is called if the table does not exists
    """
    TableRemover(db_name, table_name)


def teardown_module():
    if os.path.isfile(db_name):
        os.remove(db_name)
