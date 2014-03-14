__author__ = 'Justin Jansen'
__status__ = 'Prototype'
__date__ = '03/11/14'

import subprocess
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import *
from pyftpdlib.servers import FTPServer

"""
This is a demo of defining commnads that don't already exist in pyftpdlib

I defined two commands:
    'justin' is a NOOP command for just reporting type things
    
    'uptime' is more important, it is running the bash command "uptime" and sending it back to the client
         The terminal command uptime, tells you how long the operating system has been on. 

This has one user:
    Username: admin
    Password: admin
    Premissions: all

Like the other server it runs on port 21
"""


proto_cmds['JUSTIN'] = {
                            'auth': True,
                            'help': 'Syntax: JUSTIN',
                            'perm': None,
                            'arg': False
                       } 

proto_cmds['UPTIME'] = {
                            'auth': True,
                            'help': 'Syntax: UPTIME',
                            'perm': 'l',
                            'arg' : False
                       }



class MyHandler(FTPHandler):
    def ftp_JUSTIN(self, line):
        self.respond('200 Command Justin added Successfully') 

    def ftp_UPTIME(self, line):
        command = ['uptime']
        process = subprocess.Popen(command, stdout=subprocess.PIPE)
        value = process.communicate()[0]
        self.push_dtp_data(value, isproducer=True, cmd="UPTIME")
        return line


def main():
    auth = DummyAuthorizer()
    auth.add_user('admin', 'admin', '.', perm='elradfmwM')
    handler = MyHandler
    handler.authorizer = auth
    handler.banner = "Just testing right now"
    address = ('', 21)
    server = FTPServer(address, handler)
    server.max_cons = 256
    server.max_cons_per_ip = 5
    server.serve_forever()


if __name__ == '__main__':
    main()
