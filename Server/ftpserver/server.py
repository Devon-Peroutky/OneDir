#!/usr/bin/python2

import os, logging
#from hashlib import md5
#from random import choice
#from binascii import b2a_base64
#from hash_chars import hash_chars
from hash_chars import gen_hash, gen_salt
from pyftpdlib.servers import FTPServer
from OneDir.Server.sql.sql_manager import TableAdder, TableManager
from OneDir.Server.ftpserver.onedir_lib import authorizer, handler, container


__author__ = 'Justin Jansen'
__status__ = 'Development'
__date__ = '03/13/14'



def main(db_name, table_name, shares_db):
    if os.path.isfile(db_name):  # TODO remove when i have this stable
        os.remove(db_name) 
    if os.path.isfile(shares_db):
        os.remove(shares_db)
    ta = TableAdder(db_name, table_name)
    ta.add_column('name')
    ta.add_column('status', 'integer')
    ta.add_column('password')
    ta.add_column('salt')
    ta.add_column('welcome')
    ta.add_column('goodbye')
    ta.commit()
    del ta
    with TableManager(db_name, table_name) as tm:
        password = 'admin'
        #salt = ''.join(choice(hash_chars) for i in range(100))
        #split = len(salt)/2
        #password = salt[:split] + password + salt[split:]
        #password = b2a_base64(md5(password).digest()).strip()
        salt = gen_salt()
        password = 'admin'
        password = gen_hash(password, salt)
        row = ['admin', 1, password, salt, 'welcome', 'goodbye']
        tm.quick_push(row)
    ta = TableAdder(shares_db, 'admin')
    ta.add_column('time')
    ta.add_column('ip')
    ta.add_column('cmd')
    ta.add_column('line')    # comment out if switching to log based user logs
    ta.add_column('arg')  # comment out if switching to log based user logs
    ta.commit()
    container.set_acc_db(db_name, table_name)
    container.set_shares_db(shares_db)  
    #container.set_root_dir('/home/justin/OneDir/Server/ftpserver/temp')
    #container.set_log_file('/home/justin/OneDir/Server/ftpserver/temp/pyftpd.log')
    container.set_root_dir(os.getcwd() + '/temp')
    container.set_log_file(os.getcwd() + '/temp/pyftpd.log')
    auth = authorizer()
    handle = handler
    handle.user_sendfile = True
    handle.timeout = None
    handle.authorizer = auth
    handle.banner = 'this is the banner'
    address = ('', 21)
    server = FTPServer(address, handle)
    server.max_cons = 256
    server.maxcons_per_ip = 5
    #logging.basicConfig(filename=container.get_log_file(), level=logging.INFO)
    server.serve_forever()
   

if __name__ == '__main__':
    db_name = 'test_users.db'
    table_name = 'users'
    shares_db = 'shares.db'
    main(db_name, table_name, shares_db)

