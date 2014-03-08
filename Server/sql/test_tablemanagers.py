__author__ = 'Justin Jansen'
__status__ = 'Testing'
__date__ = '03/08/14'

from nose.tools import with_setup, raises
from extra.testhelper.helpers import n_eq, n_ok


class ToDoError(Exception):  # TODO delete after test have been written
    """
    For unwritten tests
    """
    pass


def setup_ta():
    raise ToDoError


def teardown_ta():
    raise ToDoError


@with_setup(setup_ta, teardown_ta)
def test_ta_exists():
    """
    Checks it can find a table that exists
    """
    raise ToDoError


@raises(NameError)
@with_setup(setup_ta, teardown_ta)
def test_ta_not_exists():
    """
    Checks that it raise a name error if the table does not exists
    """
    raise ToDoError


@with_setup(setup_ta, teardown_ta)
def test_ta_add_column():
    """
    Checks that the column is added
    """
    raise ToDoError


@with_setup(setup_ta, teardown_ta)
def test_ta_add_column_bad_type():
    """
    Checks that it rejects unknown types
    """
    raise ToDoError


@with_setup(setup_ta, teardown_ta)
def test_ta_commit():
    """
    Checks that the table is added to the database
    @precondition: SqlManager all test - Pass
    """
    raise ToDoError


def setup_tr():
    raise ToDoError


def teardown_tr():
    raise ToDoError


@with_setup(setup_tr, teardown_tr)
def test_tr_exists():
    """
    Test it can remove a table that exists
    """
    raise ToDoError


@raises(NameError)
@with_setup(setup_tr, teardown_tr)
def test_tr_not_exits():
    """
    Test that NameError is called if the table does not exists
    """
    raise ToDoError


def setup_tm():
    raise ToDoError


def teardown_tm():
    raise ToDoError


@with_setup(setup_tm, teardown_tm)
def test_tm_exists():
    """
    Tries to connect to a table that exists
    """
    raise ToDoError


@raises(NameError)
@with_setup(setup_tm, teardown_tm)
def test_tm_not_exists():
    """
    Tries to connect to a table that does not exist
    """
    raise ToDoError


@with_setup(setup_tm, teardown_tm)
def test_tm_with_enter():
    """
    Checks that with enter is being called
    """
    raise ToDoError


@with_setup(setup_tm, teardown_tm)
def test_tm_with_exit():
    """
    Checks that with exit is called when there are no errors
    """
    raise ToDoError


@with_setup(setup_tm, teardown_tm)
def test_tm_with_exit_error():
    """
    Test that with exit will be called even if there is an error
    """
    raise ToDoError


@with_setup(setup_tm, teardown_tm)
def test_get_column_info():
    """
    Check that the method retrieves the correct info, and is formatted correctly
    """
    raise ToDoError


@with_setup(setup_tm, teardown_tm)
def test_tm_good_quick_push():
    """
    Checks that data is being written with a good push
    """
    raise ToDoError


@raises(ValueError)
@with_setup(setup_tm, teardown_tm)
def test_():
    """
    Checks that the push is rejected when the data is wrong
    """
    raise ToDoError


@with_setup(setup_tm, teardown_tm)
def test_tm_sorted_good_push():
    """
    Tries to push a list where the columns are already in order with good info
    """
    raise ToDoError


@with_setup(setup_tm, teardown_tm)
def test_tm_unsorted_good_push():
    """
    Tries to sort the list of good info and then push it
    """
    raise ToDoError


@raises(ValueError)
@with_setup(setup_tm, teardown_tm)
def test_tm_push_bad_info():
    """
    I am not sure that value error is right
    Tries to push non matching data to the db
    """
    raise ToDoError


@with_setup(setup_tm, teardown_tm)
def test_tm_clear_table():
    """
    Tries to clear the table of all data
    """
    raise ToDoError


@with_setup(setup_tm, teardown_tm)
def test_tm_easy_pull():
    """
    Tries to pull all the columns where every type is text
    """
    raise ToDoError


@with_setup(setup_tm, teardown_tm)
def test_tm_medium_pull():
    """
    Tries to pull all the columns were there are different types
    """
    raise ToDoError


@with_setup(setup_tm, teardown_tm)
def test_hard_pull():
    """
    Tries to some of the columns and have different types
    """
    raise ToDoError