import os, sys, user_commands, admin_commands, onedir_lib
from onedir_lib import OneDirAuthorizer, OneDirHandler, set_command_creator
from pyftpdlib.servers import FTPServer
sys.path.insert(0, '../sql/')
from sql_manager import TableAdder, TableManager

__author__ = 'Justin Jansen'
__status__ = 'Development'
__date__ = '03/13/14'


db_name = 'test_users.db'
table_name = 'users'


def setup_users():
    """
    Sets up a user database for testing
    Only creates one admin. 
    """
    if os.path.isfile(db_name):
        os.remove(db_name)
    ta = TableAdder(db_name, table_name)
    ta.add_column('username')
    ta.add_column('password')
    ta.add_column('dir')
    ta.add_column('perm')
    ta.add_column('login')
    ta.add_column('quit')
    ta.commit()
    del ta
    with TableManager(db_name, table_name) as tm:
        tm.quick_push(['admin', 'admin', '../../../toMirror/', 'elradfmwM', 'Welcome Admin', 'Bye Admin'])


def main():
    set_command_creator(user_commands, admin_commands)
    auth = OneDirAuthorizer(db_name, table_name)
    handler = OneDirHandler
    handler.user_sendfile = True
    handler.timeout = None
    handler.authorizer = auth
    handler.banner = "Just testing right now"
    address = ('', 21)
    server = FTPServer(address, handler)
    server.max_cons = 256
    server.max_cons_per_ip = 5
    server.serve_forever()
   

if __name__ == '__main__':
    setup_users()
    main()
