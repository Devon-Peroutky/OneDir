__author__ = 'Justin Jansen'
__status__ = 'Prototype'
__date__ = '03/07/14'

from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer

from sql.sql_manager import TableAdder, TableManager


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

test_db = 'Users.db'
table_name = 'users'

authorizer = None
handler = None

class MyHandler(FTPHandler):
    def on_login(self, username):
        """
        This is where we could handle checking for changes between the two systems
        """
        print username, 'login'

    def on_logout(self, username):
        """
        This can remove the instance of the user that was created during validate in MyAuthorize
        """
        # authorizer.remove_user(username)
        print username, 'logout'

    # TODO the following are meant to be overwritten as needed.  I am adding them all, but do not have use for them yet

    def on_connect(self):
        """
        I don't know yet
        """
        print 'connect'

    def on_disconnect(self):
        """
        I don't know yet
        """
        print 'disconnect'

    def on_login_failed(self, username, password):
        """
        I don't know yet
        """
        print username, 'failed login'

    def on_file_sent(self, the_file):
        """
        I don't know yet
        """
        print 'file sent'

    def on_file_received(self, the_file):
        """
        I don't know yet
        """
        print 'file received'

    def on_incomplete_file_sent(self, the_file):
        """
        I don't know yet
        """
        print 'incomplete file sent'

    def on_incomplete_file_received(self, the_file):
        """
        I don't know yet
        """
        print 'incomplete file received'


class MyAuthorizer(DummyAuthorizer):  # TODO remove prints
    def validate_authentication(self, username, password, handler):
        """
        Overriding the systems checks in place of our own. So that we can use table management.
        """
        tm = TableManager(test_db, table_name)
        user_list = tm.pull_where('username', str(username), '=')
        user_list = user_list[0]
        if user_list:
            if user_list[1] == password:
                try:
                    super(MyAuthorizer, self).add_user(username, password, user_list[2], perm='elradfmwM')
                except ValueError:
                    print 'I need a better solution then this'
        super(MyAuthorizer, self).validate_authentication(username, password, handler)


def main():
    global authorizer
    global handler
    authorizer = MyAuthorizer()
    handler = MyHandler
    handler.authorizer = authorizer
    handler.banner = "Welcome to back to OneDir"
    address = ('', 21)
    server = FTPServer(address, handler)
    server.max_cons = 256
    server.max_cons_per_ip = 5
    server.serve_forever()

if __name__ == '__main__':
    main()
