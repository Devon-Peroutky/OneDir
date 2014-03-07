import os
import sqlite3 as lite
from sql_manager import SqlManager
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer

"""
This needs to be run as Root
"""

"""
Commands:
Read permissions:
"e" = change directory (CWD, CDUP commands)
"l" = list files (LIST, NLST, STAT, MLSD, MLST, SIZE commands)
"r" = retrieve file from the server (RETR command)

Write permissions
"a" = append data to an existing file (APPE command)
"d" = delete file or directory (DELE, RMD commands)
"f" = rename file or directory (RNFR, RNTO commands)
"m" = create directory (MKD command)
"w" = store a file to the server (STOR, STOU commands)
"M" = change mode/permission (SITE CHMOD command) New in 0.7.0

"""

test_db = 'Test.db'
class MyHandler(FTPHandler):
    def on_login(self, username):
        print 'This is where we could handle checking for changes between the two systems'



class MyAuthorizer(DummyAuthorizer):
    def validate_authentication(self, username, password, handler):
        # Connect to database and check for username and password, if exists add the user. 
        # This does not actually check for the password, or work the way I want it too..
        # More of just a proof
        s = SqlManager(test_db)
        s.connect()
        user_list = s.pull('users', None)
        s.disconnect()
        user_names = [un[0] for un in user_list] 
        if username in user_names:
            i = user_names.index(username)
            if user_list[0][1] == password:
                super(MyAuthorizer, self).add_user(username, password, '.', perm='elradfmwM')
        super(MyAuthorizer, self).validate_authentication(username, password, handler)
        # Still to do delete this after connection is closed   
 
    def has_user(self, username):
        return super(MyAuthorizer, self).has_user(username)

def main():
    authorizer = MyAuthorizer()
    handler = MyHandler
    handler.authorizer = authorizer
    handler.banner = "Welcome to back to OneDir... I don't like that name"
    address = ('', 21)
    server = FTPServer(address, handler)
    server.max_cons = 256
    server.max_cons_per_ip = 5
    server.serve_forever()

if __name__ == '__main__':
    s = SqlManager(test_db)
    data = [('username', 'text'),('password', 'text')]
    s.connect()
    try:  # Table already exists
        s.add_new_table('users', data)
        s.push('users', ['user', '12345'])
        s.push('users', ['another', 'abc'])
    except lite.OperationalError:
        pass
    s.disconnect()
    main()

