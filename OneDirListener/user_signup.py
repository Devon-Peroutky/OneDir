__author__ = 'rupali'

from shutil import rmtree
from OneDirServer.sql_manager import TableAdder
from client import *
from getpass import getpass
import json
from uuid import getnode as get_mac
#from onedir_runner import root_check


def main(ip, port, username=None, password=None, root_dir=None):
    """
    Prompts a new user through the creation of a non-admin account.
    """
    client = OneDirNoAuthClient(ip, port)
    nickname = get_mac()
    if not username:  #paramaters not passed in
        username = raw_input("Welcome new user! Enter in your desired username: ")
        temppw = None
        while password is None:
            try:
                temppw = client.user_sign_up(username)
                break
            except KeyError:
                username = raw_input("Sorry, that username is taken. Please enter another username: ")
        password = getpass("Username available! Please enter in a desired password:")
        pw_check = getpass("Please re-enter your password:")
        while not password == pw_check:
            password = getpass("Passwords do not match. Please enter a desired password:")
            pw_check = getpass("Please re-enter your password:")
        print 'The default server directory is: %s/OneDirFiles' % os.path.expanduser('~')
        ret = False
        while True:
            rep = raw_input('Would you like to use this:[Y/n]: ')
            rep = rep.lower()
            rep = rep.strip(' ')
            if rep in ['y', 'ye', 'yes', 'n', 'no', '']:
                ret = rep in ['y', 'ye', 'yes', '']
                break
            else:
                prompt = 'Input not understood: please enter yes or no.'
        if ret:
            root_dir = '%s/OneDirFiles' % os.path.expanduser('~')
            root_check(root_dir)
        else:
            root_dir = None
            for i in range(3):
                root_dir = raw_input('Please enter path to where you want the server file to go: ')
                if os.path.isdir(root_dir):
                    try:
                        os.rmdir(root_dir)
                        os.mkdir(root_dir)
                        break
                    except OSError:
                        print 'Sorry, not an empty directory. Try again.'
                else:
                    try:
                        os.mkdir(root_dir)
                        break
                    except OSError:
                        print 'Sorry, path not valid. Try again.'
                if i == 2:
                    print 'Too many tries. Aborting.'
                    sys.exit(1)
        create_user(ip, port, username, password, temppw, nickname, root_dir)
    else:  #parameters passed in
        try:
            root_check(root_dir)
            temppw = client.user_sign_up(username)
            create_user(ip, port, username, password, temppw, nickname, root_dir)
        except KeyError:
            print "Sorry, the entered username is taken."


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


def create_user(ip, port, username, password, temppw, nickname, root_dir):
    data = {"username": username, "root_dir": root_dir, "nick": str(nickname), "is_syncing": True, "password": password}
    path = os.path.expanduser('~') + '/.onedirclient/client.json'
    conf_folder = os.path.expanduser('~') +'/.onedirclient'
    if not os.path.exists(conf_folder):
        os.mkdir(conf_folder)
    with open(path, 'w') as filename:
        json.dump(data, filename)
    ftpclient = OneDirFtpClient(ip, port, username, nickname, temppw, root_dir)
    ftpclient.set_password(temppw, password)
    db = conf_folder + '/sync.db'
    ta = TableAdder(db, 'local')
    ta.add_column('time')
    ta.add_column('cmd')
    ta.add_column('line')
    ta.commit()


if __name__ == "__main__":
    main()
