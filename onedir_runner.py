#!/usr/bin/python2



"""
Usage:
    onedir_runner.py server start [-v | --verbose] [-t | --testing]
    onedir_runner.py server setup [(--root=<path> --user=<db> --password=<pw>)]
    onedir_runner.py server useradd <username> <password> [(-a | --admin)]
    onedir_runner.py client signup
    onedir_runner.py client changePW
    onedir_runner.py admin

Options:
    -h --help
    -v --verbose    Verbose Mode
    -t --testing    Testing mode (User: admin, Pw: admin)
    -a --admin      Is a admin
    --root=<path>   Path the server root folder
    --user=<db>     Path to the user database (a admin)
    --password=<pw> The user's password
"""

import os
import sys
import json
import logging
from docopt import docopt
from getpass import getpass
from shutil import rmtree
from pyftpdlib.servers import FTPServer
# from OneDir.Server.sql.sql_manager import TableAdder, TableManager
# from OneDir.Server.ftpserver.hash_chars import gen_hash,ls gen_salt
# from OneDir.Server.ftpserver.onedir_lib import authorizer, handler, container
from OneDirServer.sql_manager import TableAdder, TableManager
from OneDirServer.hash_chars import gen_hash, gen_salt
from OneDirServer.server_lib import authorizer, handler, container
from OneDirListener.client import OneDirAdminClient
from OneDirListener.client import OneDirFtpClient
import socket

__author__ = 'Justin'

class GuidedSetup(object):
    def __init__(self):
        self.yes = ['y', 'ye', 'yes']
        self.no = ['n', 'no']
        self.opt_yes = '[Y/n]:'
        self.opt_no = '[y/N]:'
        self.setup()

    def default_root_dir(self):
        print 'The default server directory is: %s/OneDirServer' % os.path.expanduser('~')
        ret = False
        while True:
            rep = raw_input('Wold you like to use this:%s ' % self.opt_yes)
            rep = rep.lower()
            rep = rep.strip(' ')
            if rep in self.yes + self.no + ['']:
                ret = rep in self.yes + ['']
                break
            else:
                prompt = 'Input not understood: please enter yes or no.'
                print prompt
        return ret

    def default_admin(self):
        print 'The default admin is: Username - admin; Password - admin'
        ret = False
        while True:
            rep = raw_input('Wold you like to use this:%s ' % self.opt_no)
            rep = rep.lower()
            rep = rep.strip(' ')
            if rep in self.yes + self.no + ['']:
                ret = rep in self.yes
                break
            else:
                prompt = 'Input not understood: please enter yes or no.'
                print prompt
        return ret

    def setup_root(self):
        for i in range(3):
            root_dir = raw_input('Please enter path to where you want the server file to go: ')
            if os.path.isdir(root_dir):
                try:
                    os.rmdir(root_dir)
                    os.mkdir(root_dir)
                    return root_dir
                except OSError:
                    print 'Sorry, not an empty directory. Try again.'
            else:
                try:
                    os.mkdir(root_dir)
                    return root_dir
                except OSError:
                    print 'Sorry, path not valid. Try again.'
            if i == 2:
                print 'Too many tries. Aborting.'
                sys.exit(1)

    def setup_admin_username(self):
        while True:
            username = raw_input('Please select an admin username: ')
            while True:
                rep = raw_input('You selected %s is this correct?%s' % (username, self.opt_yes))
                rep = rep.lower()
                rep = rep.strip(' ')
                if rep in self.yes + ['']:
                    return username
                elif rep in self.no:
                    break
                else:
                    prompt = 'Input not understood: please enter yes or no.'
                    print prompt

    def setup_admin_password(self, username):
        while True:
            first = getpass('Please select a password for %s: ' % username)
            second = getpass('Confirm password: ')
            if first == second:
                return first
            else:
                print 'Sorry passwords did not match. Try again.'

    def setup(self):
        check_warning()
        if self.default_root_dir():
            root_dir = '%s/OneDirServer' % os.path.expanduser('~')
        else:
            root_dir = self.setup_root()
        root_check(root_dir)
        if self.default_admin():
            admin = 'admin'
            password = 'admin'
        else:
            admin = self.setup_admin_username()
            password = self.setup_admin_password(admin)
        quick_setup(root_dir, admin, password)


def check_warning():
    if os.path.isfile('conf.json'):
        print 'Config file detected. Proceeding may override current server settings.'
        while True:
            rep = raw_input('Do you wish to proceed?[y/N]')
            rep = rep.lower()
            rep = rep.strip(' ')
            if rep in ['y', 'ye', 'yes']:
                return
            elif rep in ['n', 'no', '']:
                sys.exit(1)
            else:
                prompt = 'Input not understood: please enter yes or no.'
                print prompt
    return


def root_check(root_dir):
    if not os.path.exists(root_dir):
        try:
            os.mkdir(root_dir)
        except OSError:
            print 'Invalid path to directory.'
            print 'Aborting.'
            sys.exit(1)
    else:
        try:
            os.rmdir(root_dir)
            os.mkdir(root_dir)
        except OSError:
            print 'Root dir not empty. The root dir must be empty to continue.'
            while True:
                rep = raw_input('Do you wish to delete the contents?[y/N]:')
                if rep in ['y', 'ye', 'yes']:
                    rmtree(root_dir)
                    os.mkdir(root_dir)
                elif rep in ['n', 'no', '']:
                    print 'Aborting.'
                    sys.exit(1)
                else:
                    prompt = 'Input not understood: please enter yes or no.'
                    print prompt


def prompt_setup(root_dir, admin, password):
    check_warning()
    root_check(root_dir)
    quick_setup(root_dir, admin, password)


def quick_setup(root_dir, admin, password):
    here = os.getcwd()
    template = {'root': root_dir, 'user_db': '%s/users.db' % here, 'user_table': 'users',
                'user_logs': '%s/user_logs.db' % here}
    with open('conf.json', 'w') as w:
        json.dump(template, w)
    ta = TableAdder(template['user_db'], template['user_table'])
    cols = ['name', 'status', 'password', 'salt', 'welcome', 'goodbye']
    for col in cols:
        if col == 'status':
            ta.add_column(col, 'integer')
        else:
            ta.add_column(col)
    ta.commit()
    del ta
    server_user_add(admin, password, True)
    print 'Setup completed successfully. Exiting.'
    sys.exit(0)

def server_user_add(username, password, is_admin=False):
    if not os.path.isfile('conf.json'):
        print 'Conf file not found, please run setup.'
        sys.exit(1)
    if is_admin:
        status = 1
    else:
        status = 0
    with open('conf.json') as jd:
        template = json.load(jd)
    with TableManager(str(template['user_db']), str(template['user_table'])) as tm:
        salt = gen_salt()
        password = gen_hash(password, salt)
        row = [username, status, password, salt, 'welcome', 'goodbye']
        tm.quick_push(row)
    ta = TableAdder(template['user_logs'], username)
    cols = ['time', 'ip', 'cmd', 'line', 'arg']
    for col in cols:
        ta.add_column(col)
    ta.commit()
    del ta


def server_start(is_verbose=False):
    if not os.path.isfile('conf.json'):
        print 'Conf file not found, please run setup.'
        sys.exit(1)
    with open('conf.json') as jd:
        template = json.load(jd)
    container.set_acc_db(str(template['user_db']), str(template['user_table']))
    container.set_shares_db(str(template['user_logs']))
    container.set_root_dir(str(template['root']))
    container.set_log_file(str(template['root']) + '/pyftpd.log')
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
    if not is_verbose:
        logging.basicConfig(filename=container.get_log_file(), level=logging.INFO)
    server.serve_forever()


def server_start_testing(is_verbose=False):
    user_db = 'test_users.db'
    user_table = 'users'
    shares_db = 'test_shares.db'
    username = 'admin'
    password = 'admin'
    root = os.getcwd() + '/test_server'
    if os.path.isfile(user_db):  # TODO remove when i have this stable
        os.remove(user_db)
    if os.path.isfile(shares_db):
        os.remove(shares_db)
    if os.path.isdir(root):
        rmtree(root)
    os.mkdir(root)
    ta = TableAdder(user_db, user_table)
    cols = ['name', 'status', 'password', 'salt', 'welcome', 'goodbye']
    for col in cols:
        if col == 'status':
            ta.add_column(col, 'integer')
        else:
            ta.add_column(col)
    ta.commit()
    del ta
    with TableManager(user_db, user_table) as tm:
        salt = gen_salt()
        password = gen_hash(password, salt)
        row = [username, 1, password, salt, 'welcome', 'goodbye']
        tm.quick_push(row)
    ta = TableAdder(shares_db, username)
    cols = ['time', 'ip', 'cmd', 'line', 'arg']
    for col in cols:
        ta.add_column(col)
    ta.commit()
    del ta
    container.set_acc_db(user_db, user_table)
    container.set_shares_db(shares_db)
    container.set_root_dir(root)
    container.set_log_file(root + '/pyftpd.log')
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
    if not is_verbose:
        logging.basicConfig(filename=container.get_log_file(), level=logging.INFO)
    server.serve_forever()

def admin():
    while True:
        username = raw_input("Username: ")
        pw = raw_input("Password: ")
        try:
     	    admin = OneDirAdminClient(socket.gethostbyname(socket.gethostname()), username, pw, os.getcwd())
	    break
        except:
	    print "Invalid Login Credentials"
	    continue

    input=raw_input("Simply type any admin commands you want to be executed. Type Exit() to quit and logout\n")

    while input != "Exit()":
        command = "admin."+input
	try:
	    output = eval(command)
	    print output
	except:
	    print "Not a valid command, or it was not able to execute properly."
	input=raw_input('')

def client_signup():
    """
    Prompts a new user through the creation of a non-admin account.
    """
    client = OneDirAdminClient(socket.gethostbyname(socket.gethostname()), "admin", "admin", os.getcwd())
    username = raw_input("Welcome new user! Enter in your desired username:")
    check = check_user_available(client, username)
    while not check:
        username = raw_input("Sorry, that username is taken. Please enter another username.")
        check = check_user_available(username)
    pw = raw_input("Username available! Please enter in a desired password:")
    pw_check = raw_input("Please re-enter your password:")
    while not pw == pw_check:
        pw = raw_input("Passwords do not match. Please enter a desired password:")
        pw_check = raw_input("Please re-enter your password:")
    client.user_add(username, pw, False)

def check_user_available(c, username):
    """
    Helper method to check that a desired username is not already taken.
    """
    users = c.get_user_list()
    if username not in users:
        return True
    else:
        return False

def client_changePW():
    """
    Prompts a current user through changing their password
    """
    client = OneDirAdminClient(socket.gethostbyname(socket.gethostname()), "admin", "admin", os.getcwd())
    username = raw_input("Please enter in your username:") #can be removed if there's a get_current_user() method somewhere I didn't see
    check = check_valid(client, username)
    while not check:
        username = raw_input("Entered username not valid. Please enter a valid username:")
    current_pw = "dummy" #need to access database to get user's current pw
    verify_pw = raw_input("Please enter in your current password:")
    while not current_pw == verify_pw:
        verify_pw = raw_input("Incorrect password entry. Please enter current valid password:")
    new_pw = raw_input("Enter in your desired new password:")
    verify_new_pw = raw_input("Re-enter your desired new password:")
    while not new_pw == verify_new_pw:
        print("The new passwords you entered do not match. Please enter in the same password twice to change it.")
        new_pw = raw_input("Enter in your desired new password:")
        verify_new_pw = raw_input("Re-enter your desired new password:")
    client.change_user_password(username, new_pw)

def check_valid(c, username):
    """
    Helper method to check that the entered username is a valid username.
    """
    users = c.get_user_list()
    if username in users:
        return True
    else:
        return False



if __name__ == '__main__':
    args = docopt(__doc__)
    if args['server']:
        if args['start']:
            if args['--testing']:
                server_start_testing(args['--verbose'])
            else:
                server_start(args['--verbose'])
        elif args['setup']:
            if args['--root']:
                prompt_setup(args['--root'], args['--user'], args['--password'])
            else:
                GuidedSetup()
        elif args['useradd']:
            server_user_add(args['username'], args['password'], args['--admin'])
    elif args['client']:
	if args['signup']:
	    client_signup()
	elif args['changePW']:
	    client_changePW()
	else:
	    print "Unknown arguments"
    elif args['admin']:
	admin()
