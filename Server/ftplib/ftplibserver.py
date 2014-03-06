import os
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer

"""
This needs to be run as Root

Note this is almost exactly the sample code from the pyftpdlib website

I noticed that I had problems with this running them out of virtual machines with port forwarding
It would connect on port 20/21 but with certain requests it would pick to send back information on a 
different port.  Without knowing that port ahead of time the infomation would be set to the host machine
and cause the program to fail. 

"""

def main():
    authorizer = DummyAuthorizer()
    authorizer.add_user('user', '12345', '.', perm='elradfmwM')
    authorizer.add_anonymous(os.getcwd())
    handler = FTPHandler
    handler.authorizer = authorizer
    handler.banner = "pyftpdlib based ftpd ready."
    address = ('', 21)
    server = FTPServer(address, handler)
    server.max_cons = 256
    server.max_cons_per_ip = 5
    server.serve_forever()

if __name__ == '__main__':
    main()

