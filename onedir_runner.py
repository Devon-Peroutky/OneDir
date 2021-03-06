#!/usr/bin/python2

"""
Usage:
    onedir_runner.py server start [-v | --verbose] [-t | --testing][--port=<nu>]
    onedir_runner.py server setup [(--root=<path> --user=<db> --password=<pw>)]
    onedir_runner.py server useradd <username> <password> [(-a | --admin)]
    onedir_runner.py client start <ip> [--port=<nu>]
    onedir_runner.py client sync [-o | --once]
    onedir_runner.py client signup <ip> [--port=<nu>] [(--user=<name> --password=<pw> --root=<path>)]
    onedir_runner.py client setup <ip> [--port=<nu>][(--user=<name> --password=<pw> --root=<name>)]
    onedir_runner.py client changepw <ip> <user> [--port=<nu>]
    onedir_runner.py client deactivate <ip> [--port=<nu>]
    onedir_runner.py client admin report <ip> [--port=<nu>] [--user=<name>] [--write=<name>]
    onedir_runner.py client admin userinfo <ip> [--port=<nu>] [--user=<name>] [--write=<name>]
    onedir_runner.py client admin remove <ip> <user> [--port=<nu>]
    onedir_runner.py client admin changepw <user> <password> <ip> [--port=<nu>]
    onedir_runner.py client admin getlog <ip> [--port=<nu>]
    onedir_runner.py client admin usage <ip> [--port=<nu>] [--user=<name>]

Options:
    -h --help
    -v --verbose    Verbose Mode
    -t --testing    Testing mode (User: admin, Pw: admin)
    -a --admin      Is a admin
    -o --once       If sync is off sync once without toggling it on
    --root=<path>   Path the server root folder
    --user=<db>     Path to the user database (a admin)
    --password=<pw> The user's password
    --port=<nu>     Default = 21; Unprivileged = 1024
    --write=<name>  Right the output to file instead
"""

import os
import sys
import json
import logging
from docopt import docopt
from getpass import getpass
from shutil import rmtree
from pyftpdlib.servers import FTPServer
from OneDirListener.client import OneDirFtpClient, OneDirNoAuthClient, OneDirAdminClient
from OneDirServer.sql_manager import TableAdder, TableManager
from OneDirServer.hash_chars import gen_hash, gen_salt
from OneDirServer.server_lib import authorizer, handler, container
from OneDirListener.watch2 import ListenerContainer, main
from OneDirListener.user_signup import main as signup
from OneDirListener.user_change_pw import main as user_changepw
from uuid import getnode as get_mac

__author__ = 'Justin'
#  TODO I have added a few things to this without testing them


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
            rep = raw_input('Would you like to use this:%s ' % self.opt_yes)
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
            rep = raw_input('Would you like to use this:%s ' % self.opt_no)
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
    user_dir = '%s/%s' % (template['root'], username)  # Untested
    os.mkdir(user_dir)  # Untested


def server_start(is_verbose=False, port=None):
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
    if port:  # untested
        address = ('', 1024)
    else:
        address = ('', 21)
    server = FTPServer(address, handle)
    server.max_cons = 256
    server.maxcons_per_ip = 1000000
    if not is_verbose:
        logging.basicConfig(filename=container.get_log_file(), level=logging.INFO)
    server.serve_forever()


def server_start_testing(is_verbose=False, port=None):
    user_db = 'test_users.db'
    user_table = 'users'
    shares_db = 'test_shares.db'
    username = 'admin'
    password = 'admin'
    root = os.getcwd() + '/test_server'
    if os.path.isfile(user_db):
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
    if port:  # untested
        address = ('', port)
    else:
        address = ('', 21)
    server = FTPServer(address, handle)
    server.max_cons = 256
    server.maxcons_per_ip = 5
    if not is_verbose:
        logging.basicConfig(filename=container.get_log_file(), level=logging.INFO)
    server.serve_forever()


###{{{[start] Untested }}}###
def admin_report(ip, port, username=None, write=None):
    ad = get_admin(ip, port)
    ret = ad.report()
    if write:
        with open(write, 'w') as w:
            w.write(ret)
    else:
        for val in ret:
            print val


def admin_user_info(ip, port, username=None, write=None):
    ad = get_admin(ip, port)
    userlist = ad.get_user_list()
    if username:
        for val in userlist:
            if val[0] == username:
                if not write:
                    print val
                else:
                    with open(write, 'w') as w:
                        w.write(val)
                sys.exit(0)
        print 'User not found on server'
    else:
        if not write:
            for val in userlist:
                print val
        else:
            with open(write, 'w') as w:
                w.write(userlist)


def admin_remove(ip, port, username):
    ad = get_admin(ip, port)
    try:
        ad.user_del(username)
        #print '%s deleted sucessfully.' % username
    except Exception as e:
        print e
        print '%s was not found in database, delete failed' % username


def admin_change_password(ip, port, username, password):
    ad = get_admin(ip, port)
    try:
        ad.change_user_password(username, password)
        print '%s password is now changed' % username
    except Exception as e:
        print e
        print 'Password change failed: %s not found.' % username


def admin_getlog(ip, port):
    ad = get_admin(ip, port)
    with open(ad.get_log(), 'r') as f:
        output = f.read()
    print output

def admin_usage(ip, port, user=None):
    ad = get_admin(ip, port)
    if not user:
        ad.count_files(None)
    else:
        ad.count_files('./%s' % user)

def get_admin(ip, port):  # TODO not started
    conf = os.path.expanduser('~') + '/.onedirclient/client.json'
    jd = open(conf)
    conf = json.load(jd)
    jd.close()
    return OneDirAdminClient(ip, port, conf['username'], conf['nick'], conf['password'], conf['root_dir'])


def user_signup(ip, port=None, user=None, password=None, root=None):
    signup(ip, port, user, password, root)
    print 'User created successfully'


def user_setup(ip, port=None, user=None, password=None, root=None): # TODO IP PORT
    if not user:
        print 'TODO'
        user=raw_input("Enter your username: ")
    else:
        try:
            nick = get_mac()
            data = {"username": user, "root_dir": root, "nick": str(nick),
                "is_syncing": True, "password": password, 'last_sync': "0"}
            path = os.path.expanduser('~') + '/.onedirclient/client.json'
            conf_folder = os.path.expanduser('~') + '/.onedirclient'
            if not os.path.exists(conf_folder):
                os.mkdir(conf_folder)
            with open(path, 'w') as filename:
                json.dump(data, filename)
            watch_folder = os.path.expanduser('~') + '/OneDirFiles'
            if not os.path.exists(watch_folder):
                os.mkdir(watch_folder)
            # ftpclient = OneDirFtpClient(ip, port, user, nick, password, root)
            db = conf_folder + '/sync.db'
            ta = TableAdder(db, 'local')
            ta.add_column('time')
            ta.add_column('cmd')
            ta.add_column('line')
            ta.commit()
            # print 3
        except:
            print 'invalid credentials'


def user_deactivate(ip, port=None, username=None, password=None, root=None):
    folderpath = os.path.expanduser('~') + '/.onedirclient'
    conffile = os.path.join(folderpath, 'client.json')
    conffile = os.path.abspath(conffile)
    jd = open(conffile)
    conf = json.load(jd)
    jd.close()
    username = conf['username']
    root = conf['root_dir']
    password = conf['password']
    nick = conf['nick']
    port = 21
    f = OneDirFtpClient(ip, port, username, nick, password, root)
    f.deactivate_account()
    # os.remove(conffile)
    rmtree(folderpath)


def user_set_password(ip, username=None, port=None):  # TODO IP PORT
    # from setup file get username and password.
    # fc = OneDirClient( ... )
    # old_password = password from files.
    # if not password:
    #     while True:
    #         first = getpass('Please enter a password: ')
    #         second = getpass('Re-enter password: ')
    #         if first == second:
    #             password = first
    #             break
    #         else:
    #             print 'Sorry the passwords did not match, try again.'
    #             # fc.set_password(password, old_password)
    #             # write new password to the file.
    conffile = os.path.expanduser('~') + '/.onedirclient'
    conffile = os.path.join(conffile, 'client.json')
    conffile = os.path.abspath(conffile)
    jd = open(conffile)
    conf = json.load(jd)
    jd.close()
    root_dir = conf['root_dir']
    password = conf['password']
    nick = conf['nick']
    port = 21
    user_changepw(ip, port, username, nick, password, root_dir)


def start_client(ip, port=None):
    if not port:
        port = 21
    main(ip, port)


def switch_sync(once=False):
    # conf = os.path.abspath(__file__)
    # conf = os.path.split(conf)[0]
    # conf += '/OneDirListener/client.json'
    conf = os.path.expanduser('~')
    conf = '%s/.onedirclient/client.json' % conf
    jd = open(conf, 'r')
    data = json.load(jd)
    if data['is_syncing']:
        data['is_syncing'] = False
        print 'Syncing is now off'
    else:
        data['is_syncing'] = True
        print 'Syncing is now on'
    jd.close()
    with open(conf, 'w') as w:
        json.dump(data, w)

    ###{{{[end] Untested}}}###


if __name__ == '__main__':
    args = docopt(__doc__)
    if args['server']:
        if args['start']:
            if args['--testing']:
                server_start_testing(args['--verbose'], args['--port'])
            else:
                server_start(args['--verbose'], args['--port'])
        elif args['setup']:
            if args['--root']:
                prompt_setup(args['--root'], args['--user'], args['--password'])
            else:
                GuidedSetup()
        elif args['useradd']:
            server_user_add(args['<username>'], args['<password>'], args['--admin'])
    if args['client']:  # TODO all untested
        if args['admin']:
            if not args['--port']:
                args['--port'] = 21
                args['port'] = 21
            if args['report']:
                admin_report(args['<ip>'], args['port'], args['--user'], args['--write'])
            elif args['userinfo']:
                admin_user_info(args['<ip>'], args['port'], args['--user'], args['--write'])
            elif args['remove']:
                admin_remove(args['<ip>'], args['--port'], args['<user>'])
            elif args['changepw']:
                admin_change_password(args['<ip>'], args['--port'], args['<user>'], args['<password>'])
            elif args['getlog']:
                admin_getlog(args['<ip>'], args['port'])
            elif args['usage']:
                admin_usage(args['<ip>'], args['port'], args['--user'])
        elif args['start']:
            start_client(args['<ip>'], args['--port'])
        elif args['sync']:
            switch_sync(args['--once'])
        elif args['signup']:
            user_signup(args['<ip>'], args['--port'],  args['--user'], args['--password'], args['--root'])
        elif args['setup']:
            user_setup(args['<ip>'], args['--port'], args['--user'], args['--password'], args['--root'])
        elif args['changepw']:
            user_set_password(args['<ip>'], args['<user>'], args['--port'])
        elif args['deactivate']:
            user_deactivate(args['<ip>'], args['--port'])
