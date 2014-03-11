from copy import deepcopy
import os
import json
from ftplib import FTP
from nose.tools import with_setup
from extra.testhelper.helpers import n_eq, n_ok


"""
There are two test in this I still don't know how to implement yet.

The writen test are passing.
Which is good for most user functionality.
There still is some ADMIN functionality that this does NOT cover.
That was done in the server config script.

I guess that is the next big step.

Another good step would be to create a true client class out of the commands
tested bellow.
"""

__author__ = 'Justin Jansen'
__status__ = 'Testing'
__date__ = '03/10/14'


# Needs server login credentials
server_ip = None
port_num = None
users = None
server_map = None


class SetupError(Exception):
    """
    Will be thrown if there are problems with setting up server
    Before tests are run on it.
    """
    pass


class ToDoError(Exception):  # TODO delete this when done writing tests
    """
    A place hold for the tests that have not been writen
    """
    pass


def setup_module():
    """
    Loads file and checks to see if it is even possible to connect to the server.
    If file not found, or can not connect will throw error and no tests will be run.
    """
    if not os.path.isfile('server_config.txt'):
        print 'need file, server_config.txt, file template:'
        with open('conf_template.txt', 'r') as r:
            print r.read()
        raise SetupError('Setup File not found: more info in std.out')
    with open('server_config.txt') as jd:
        global server_ip
        global port_num
        global users
        config = json.load(jd)
        server_ip = str(config['ip'])
        port_num = str(config['port'])
        users = config['users']
        ftp = FTP()
        ftp.connect(server_ip, port_num)
        del ftp


callbacks = []


def setup_callback():
    global callbacks
    callbacks = []


def general_callback(ret_val):
    global callbacks
    callbacks += [ret_val]


def test_get_welcome():
    ftp = FTP()
    ftp.connect(server_ip, port_num)
    actual = ftp.getwelcome().split(' ')
    actual = actual[1:]
    actual = ' '.join(actual)
    expected = "Welcome to back to OneDir"
    n_eq(expected, actual)


def test_pwd():
    """
    Checks starting dir
    Should log in as admin in the root dir
    """
    ftp = FTP()
    un = users.keys()[0]
    pw = str(users[un][0])
    ftp.connect(server_ip, port_num)
    ftp.login(str(un), str(pw))
    actual = ftp.pwd()
    expected = '/'
    ftp.quit()
    n_eq(expected, actual)


@with_setup(setup_callback)
def test_ls():
    """
    Checks that the files in a dir can be printed
    """
    ftp = FTP()
    un = users.keys()[1]
    pw = str(users[un][0])
    ftp.connect(server_ip, port_num)
    ftp.login(str(un), str(pw))
    ftp.retrlines('NLST', general_callback)
    actual = callbacks[0]
    expected = 'shared_folder'
    ftp.quit()
    n_eq(expected, actual)


def test_cd():
    """
    @precondition: test_pwd passed
    Checks change dir
    """
    ftp = FTP()
    un = users.keys()[2]
    pw = str(users[un][0])
    ftp.connect(server_ip, port_num)
    ftp.login(str(un), str(pw))
    before = ftp.pwd()
    ftp.cwd('download_from')
    after = ftp.pwd()
    actual = not before == after
    ftp.quit()
    n_ok(actual)


def test_download():
    """
    @precondition: test_cd passed
    Tries to download a file
    """
    ftp = FTP()
    un = users.keys()[2]
    pw = str(users[un][0])
    ftp.connect(server_ip, port_num)
    ftp.login(str(un), str(pw))
    ftp.cwd('download_from')
    file_name = 'to_download.txt'
    file_d = open(file_name, 'wb')
    ftp.retrlines('RETR %s' % file_name, file_d.write)
    file_d.close()
    ftp.quit()
    actual = None
    with open(file_name, 'r') as r:
        actual = r.read()
    if os.path.isfile(file_name):
        os.remove(file_name)
    expected = "This is some text in to_download.txt"
    n_eq(expected, actual)


@with_setup(setup_callback)
def test_upload():  # TODO STORE LINES HAS ITS OWN CALLBACK! Might be useful later
    """
    @precondition: test_cd passed
    @precondition: test_ls passed
    Tries to upload a file
    """
    file_name = 'uploaded_file.txt'
    with open(file_name, 'w') as w:
        file_txt = "This will be inserted into the file"
        w.write(file_txt)
    ftp = FTP()
    un = users.keys()[2]
    pw = str(users[un][0])
    ftp.connect(server_ip, port_num)
    ftp.login(str(un), str(pw))
    ftp.cwd('upload_to')
    ftp.storlines("STOR %s" % file_name, open(file_name, 'rb'))
    ftp.retrlines('NLST', general_callback)
    ftp.quit()
    actual = callbacks[0] == file_name
    if os.path.isfile(file_name):
        os.remove(file_name)
    n_ok(actual)


@with_setup(setup_callback)
def test_delete():
    """
    @precondition: test_cd passed
    @precondition: test_ls passed
    Tries to delete a file off the server
    """
    ftp = FTP()
    un = users.keys()[2]
    pw = str(users[un][0])
    ftp.connect(server_ip, port_num)
    ftp.login(str(un), str(pw))
    ftp.cwd('upload_to')
    ftp.retrlines('NLST', general_callback)
    file_name = 'uploaded_file.txt'
    if callbacks[0] == file_name:
        setup_callback()
        ftp.delete(file_name)
        ftp.retrlines('NLST', general_callback)
        ftp.quit()
        if len(callbacks) == 0:
            n_ok(True)
        else:
            n_ok(False)
    else:
        ftp.quit()
        raise SetupError('File to delete not found')


@with_setup(setup_callback)
def test_shares_exists():
    """
    @precondition: test_cd passed
    @precondition: test_ls passed
    Tests to see if the two users are seeing the same dir,
    for their shared folder.
    """
    user_one = FTP()
    user_two = FTP()
    u1_un = users.keys()[2]
    u2_un = users.keys()[1]
    u1_pw = str(users[u1_un][0])
    u2_pw = str(users[u2_un][0])
    user_one.connect(server_ip, port_num)
    user_two.connect(server_ip, port_num)
    user_one.login(u1_un, u1_pw)
    user_two.login(u2_un, u2_pw)
    user_one.retrlines('NLST', general_callback)
    user_one_dirs = deepcopy(callbacks)
    setup_callback()
    user_two.retrlines('NLST', general_callback)
    user_two_dirs = deepcopy(callbacks)
    setup_callback()
    if user_one_dirs == user_two_dirs:
        raise SetupError('They are in the same folder')
    user_one.cwd('shared_folder')
    user_two.cwd('shared_folder')
    user_one.retrlines('NLST', general_callback)
    user_one_dirs = deepcopy(callbacks)
    setup_callback()
    user_two.retrlines('NLST', general_callback)
    user_two_dirs = deepcopy(callbacks)
    actual = user_one_dirs == user_two_dirs
    user_one.quit()
    user_two.quit()
    n_ok(actual)


shared_fn_name = 'uploaded_share.txt'


def clear_file():
    """
    Deletes the file from the server so it does not effect future tests
    Also deletes it locally to reduce clutter :)
    @precondition: test_delete passed
    """
    setup_callback()
    ftp = FTP()
    un = users.keys()[2]
    pw = str(users[un][0])
    ftp.connect(server_ip, port_num)
    ftp.login(str(un), str(pw))
    ftp.cwd('shared_folder')
    ftp.retrlines('NLST', general_callback)
    if shared_fn_name in callbacks:
        ftp.delete(shared_fn_name)
    if os.path.isfile(shared_fn_name):
        os.remove(shared_fn_name)
    ftp.quit()


@with_setup(setup_callback, clear_file)
def test_shares_uploads():
    """
    @precondition: test_cd passed
    @precondition: test_ls passed
    @precondition: test_upload passed
    User1 uploads a file into its shared folder
    User2 runs a ls command its shared folder to see if the file is there
    """
    user_one = FTP()
    user_two = FTP()
    u1_un = users.keys()[2]
    u2_un = users.keys()[1]
    u1_pw = str(users[u1_un][0])
    u2_pw = str(users[u2_un][0])
    user_one.connect(server_ip, port_num)
    user_two.connect(server_ip, port_num)
    user_one.login(u1_un, u1_pw)
    user_two.login(u2_un, u2_pw)
    user_one.retrlines('NLST', general_callback)
    user_one_dirs = deepcopy(callbacks)
    setup_callback()
    user_two.retrlines('NLST', general_callback)
    user_two_dirs = deepcopy(callbacks)
    setup_callback()
    if user_one_dirs == user_two_dirs:
        raise SetupError('They are in the same folder')
    user_one.cwd('shared_folder')
    user_two.cwd('shared_folder')
    with open(shared_fn_name, 'w') as w:
        file_txt = "This will be inserted into shared the file"
        w.write(file_txt)
    user_one.storlines("STOR %s" % shared_fn_name, open(shared_fn_name, 'rb'))
    user_one.quit()
    setup_callback()
    user_two.retrlines('NLST', general_callback)
    user_two.quit()
    actual = shared_fn_name in callbacks
    n_ok(actual)


def test_interrupt_down():
    """
    Kills the connection and Download, Checks that it is handled gracefully.
    @precondition: test_download - Pass
    """
    raise ToDoError


def test_interrupt_up():
    """
    Kills the connection on a upload, Checks that it is handled gracefully.
    """
    raise ToDoError
