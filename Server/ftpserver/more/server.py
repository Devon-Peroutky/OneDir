__author__ = 'Justin Jansen'
__status__ = 'Prototype'
__date__ = '03/11/14'

from onedir_lib import OneDirAuthorizer, OneDirHandler, set_shares
from pyftpdlib.servers import FTPServer


def main():
    set_shares('SHARES SET!!!')  # TODO set this to db name
    auth = OneDirAuthorizer('Users.db', 'users')
    handler = OneDirHandler
    handler.authorizer = auth
    handler.banner = "Just testing right now"
    address = ('', 21)
    server = FTPServer(address, handler)
    server.max_cons = 256
    server.max_cons_per_ip = 5
    server.serve_forever()


if __name__ == '__main__':
    main()
