from sql_manager import TableAdder, TableManager
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
table_name = 'users'


class MyHandler(FTPHandler):
    def on_login(self, username):
        """
        This is where we could handle checking for changes between the two systems
        """
        pass

    def on_logout(self, username):
        """
        This can remove the instance of the user that was created during validate in MyAuthorize
        """
        pass

    # TODO the following are meant to be overwritten as needed.  I am adding them all, but do not have use for them yet

    def on_connect(self):
        """
        I don't know yet
        """
        pass

    def on_disconnect(self):
        """
        I don't know yet
        """
        pass

    def on_login_failed(self, username, password):
        """
        I don't know yet
        """
        pass

    def on_file_sent(self, the_file):
        """
        I don't know yet
        """
        pass

    def on_file_received(self, the_file):
        """
        I don't know yet
        """
        pass

    def on_incomplete_file_sent(self, the_file):
        """
        I don't know yet
        """
        pass

    def on_incomplete_file_received(self, the_file):
        """
        I don't know yet
        """
        pass


class MyAuthorizer(DummyAuthorizer):
    def validate_authentication(self, username, password, handler):
        """
        Overriding the systems checks in place of our own. So that we can use table management.
        """
        tm = TableManager(test_db, table_name)
        user_list = tm.pull()
        user_names = [un[0] for un in user_list]
        if username in user_names:
            user_index = user_names.index(username)
            if user_list[user_index][1] == password:
                super(MyAuthorizer, self).add_user(username, password, '.', perm='elradfmwM')
        super(MyAuthorizer, self).validate_authentication(username, password, handler)


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
    try:
        t = TableAdder(test_db, table_name)
        t.add_column('username', 'text')
        t.add_column('password', 'text')
        t.commit()
        del t
        t = TableManager(test_db, table_name)
        t.quick_push(['user', '12345'])
        t.quick_push(['user2', 'abcd'])
        del t
    except NameError:
        pass

