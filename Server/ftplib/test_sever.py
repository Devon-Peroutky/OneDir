import os
import json
from nose.tools import with_setup

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
username = None
password = None
user_dir = None
server_map = None  # TODO i am not sure how i am going to do this


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
    global server_ip
    global port_num
    global username
    global password
    global user_dir
    global server_map
    if not os.path.isfile('server_config.txt'):
        # TODO TEMPLATE
        raise SetupError('Setup File not found: more info in std.out')
    check_list = ['ip', 'port', 'user', 'pass', 'dir', 'server_map']
    loaded_file = {}  # TODO
    for key, value in loaded_file:  # TODO fix
        if not key in check_list:
            raise SetupError('Incorrect config file' + key + ' not found.')
    server_ip = loaded_file['ip']
    port_num = loaded_file['port']
    username = loaded_file['user']
    password = loaded_file['pass']
    user_dir = loaded_file['dir']
    # TODO connect

# TODO i might need a teardown also if i start dumping out files.


def connect_server():
    raise ToDoError


def disconnect_server():
    raise ToDoError


@with_setup(connect_server, disconnect_server)
def test_pwd():
    """
    Checks starting dir
    """
    raise ToDoError


@with_setup(connect_server, disconnect_server)
def test_cd():
    """
    Checks change dir
    """
    raise ToDoError


@with_setup(connect_server, disconnect_server)
def test_ls():
    """
    Checks that the files in a dir can be printed
    """
    raise ToDoError


@with_setup(connect_server, disconnect_server)
def test_alternate_user():
    """
    Uses alternate login credentials, and checks that start in different dir
    """
    raise ToDoError


@with_setup(connect_server, disconnect_server)
def test_download():
    """
    Tries to download a file
    """
    raise ToDoError


@with_setup(connect_server, disconnect_server)
def test_upload():
    """
    Tries to upload a file
    """
    raise ToDoError


@with_setup(connect_server, disconnect_server)
def test_shares():
    """
    Uploads a file into a shared folder of one user, and downloads it with the other.
    @precondition: test_download - Pass
    @precondition: test_upload - Pass
    """
    raise ToDoError


@with_setup(connect_server, disconnect_server)
def test_interrupt_down():
    """
    Kills the connection and Download, Checks that it is handled gracefully.
    @precondition: test_download - Pass
    """
    raise ToDoError


@with_setup(connect_server, disconnect_server)
def test_interrupt_up():
    """
    Kills the connection on a upload, Checks that it is handled gracefully.
    """
    raise ToDoError
