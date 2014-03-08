__author__ = 'Justin Jansen'
__status__ = 'Development'
__date__ = '03/07/14'

from Server.sql.sql_manager import TableAdder, TableManager


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
    with TableManager(db_name, table_name) as tm:
        tm.quick_push(['admin', 'admin', '.'])
        tm.quick_push(['user1', '123', '/user1'])
        tm.quick_push(['user2', 'abc', '/user2'])


if __name__ == '__main__':
    main()
