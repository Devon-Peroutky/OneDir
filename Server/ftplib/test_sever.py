import os
import json
from ftplib import FTP
from nose.tools import with_setup
from extra.testhelper.helpers import n_eq, n_ok


"""

There a few things I need to figure out before I can even start these tests.
I might need to rewrite my server config script... to use a sever_map...
there this and that will always be the same

I also need to figure out how to kill the connection to the server in that very short burst where these
tiny files are uploading.  Maybe mock as a tool for that.  Or maybe I just need to make a larger file.
If the file is larger I already know how to do it in Arch Linux, I will just have to figure out
how do do it in Ubuntu.

"""


__author__ = 'Justin Jansen'
__status__ = 'Testing'
__date__ = '03/07/14'


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
    n_eq(expected, actual)


def test_cd():
    """
    Checks change dir
    """
    ftp = FTP()
    un = users.keys()[2]
    pw = str(users[un][0])
    ftp.connect(server_ip, port_num)
    ftp.login(str(un), str(pw))
    raise ToDoError


def test_alternate_user():
    """
    Uses alternate login credentials, and checks that start in different dir
    """
    raise ToDoError


def test_download():
    """
    Tries to download a file
    """
    raise ToDoError


def test_upload():
    """
    Tries to upload a file
    """
    raise ToDoError


def test_shares():
    """
    Uploads a file into a shared folder of one user, and downloads it with the other.
    @precondition: test_download - Pass
    @precondition: test_upload - Pass
    """
    raise ToDoError


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
