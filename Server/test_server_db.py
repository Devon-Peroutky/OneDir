__author__ = 'Justin Jansen'
__status__ = 'Development'
__date__ = '03/07/14'

from ftplib.sql_manager import TableAdder, TableManager


def main():
    """
    Sets up a user database for testing
    """
    db_name = 'Users.db'
    table_name = 'users'
    ta = TableAdder(db_name, table_name)
    ta.add_column('username')
    ta.add_column('password')
    ta.add_column('root')
    ta.commit()
    del ta
    tm = TableManager(db_name, table_name)
    tm.quick_push(['user1', '123', '/user1'])
    tm.quick_push(['user2', 'abc', '/user2'])
    del tm


if __name__ == '__main__':
    main()
