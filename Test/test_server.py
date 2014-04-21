from copy import deepcopy
from ftplib import FTP
import hashlib
import os
from nose import with_setup
# from extra.testhelper.helpers import n_eq, n_ok
from helpers import n_eq, n_ok

__author__ = 'Justin Jansen'
__status__ = 'Testing'
__date__ = '03/13/14'


# This set of tests is different.  It builds the server as it tests it.
# There is no need for any kind of initial setup before hand.
# Only edit the line ip bellow and make sure the server is running.
# These tests are sequential, it assumed that every test before has passed.
# Note: all these seemingly random numbers are response codes.

ip = '10.0.0.6'
port = 21
admin = 'admin'
admin_pw = 'admin'


ftp = None
received = []


class SetupError(Exception):
    """
    Checks if you configured the server correct.
    """
    pass


def setup_module():
    global ftp
    try:
        ftp = FTP()
        ftp.connect(ip, port)
        ftp.login(admin, admin_pw)
        ftp.quit()
        ftp = None
    except:
        msg = 'Setup is incorrect. Make sure server is on. Ip: %s Port: %s ' % (ip, port)
        raise SetupError(msg)


def setup_callback():
    global received
    received = []


def callback(line):
    global received
    received += line


def setup_admin():
    global ftp
    ftp = FTP()
    ftp.connect(ip, port)
    ftp.login(admin, admin_pw)
    setup_callback()


def teardown_admin():
    global ftp
    try:
        ftp.quit()
    except AttributeError:
        pass
    ftp = None


@with_setup(setup_admin, teardown_admin)
def test_pwd():
    """
    All users see '/' as their starting dir.
    Admin is actually in the same file as all the server python files
    """
    actual = ftp.pwd()
    expected = '/'
    n_eq(expected, actual)


@with_setup(setup_admin, teardown_admin)
def test_make_dir():
    """
    Makes a dir called server, and checks for the response code '257'
    Which means that everything is all good.
    """
    ftp.voidcmd('MKD /test_fs')
    expect = '257'
    actual = ftp.lastresp
    n_eq(expect, actual)


@with_setup(setup_admin, teardown_admin)
def test_cd():
    """
    Changers Current working Dir to 'test_fs'
    """
    diff_dir = '/test_fs'
    before = ftp.pwd()
    ftp.cwd(diff_dir)
    after = ftp.pwd()
    actual = (not before == after) and (after == diff_dir)
    n_ok(actual)


# new user to use now
user_one = 'userOne'
user_one_pw = 'abc'
u1_ftp = None


def setup_user_one():
    global u1_ftp
    u1_ftp = FTP()
    u1_ftp.connect(ip, port)
    u1_ftp.login(user_one, user_one_pw)


def teardown_user_one():
    global u1_ftp
    try:
        u1_ftp.quit()
    except AttributeError:
        pass
    u1_ftp = None


@with_setup(setup_admin, teardown_admin)
def test_user_add():
    """
    Makes a new user
    """
    ftp.cwd('/test_fs')
    ftp.voidcmd('mkd %s' % user_one)
    ftp.voidcmd('useradd %s %s' % (user_one, user_one_pw))
    r1 = ftp.lastresp
    setup_user_one()
    r2 = u1_ftp.lastresp
    teardown_user_one()
    expected = ['200', '230']
    actual = [r1, r2]
    n_eq(expected, actual)


@with_setup(setup_user_one, teardown_user_one)
def test_upload():
    """
    Attempts to upload a file
    NOTE: This one has been edited in order to fix the extra line being appended to the end of the file.
    NOTE: This works with any file type.
    """
    new_dir = 'upload_folder'
    f_name = 'uploaded.txt'
    u1_ftp.voidcmd('mkd %s' % new_dir)
    with open(f_name, 'w') as w:
        w.write('some text for the file')
    u1_ftp.cwd(new_dir)
    u1_ftp.storbinary('STOR %s' % f_name, open(f_name, 'rb'))
    actual = u1_ftp.lastresp
    expected = '226'
    if os.path.isfile(f_name):
        os.remove(f_name)
    n_eq(expected, actual)


@with_setup(setup_user_one, teardown_user_one)
def test_download():
    """
    Attempts to download a file
    """
    u1_ftp.cwd('upload_folder')
    f_name = 'uploaded.txt'
    download_file = open(f_name, 'wb')
    u1_ftp.retrlines('RETR %s' % f_name, download_file.write)
    download_file.close()
    if os.path.isfile(f_name):
        os.remove(f_name)
    else:
        n_ok(False)
    actual = u1_ftp.lastresp
    expected = '226'
    n_eq(actual, expected)


@with_setup(setup_user_one, teardown_user_one)
def test_delete_file():
    """
    Deletes the file that we uploaded earlier
    """
    u1_ftp.cwd('upload_folder')
    u1_ftp.delete('uploaded.txt')
    actual = u1_ftp.lastresp
    expected = '250'
    n_eq(actual, expected)


@with_setup(setup_user_one, teardown_user_one)
def test_delete_empty_folder():
    """
    Deletes the folder we were uploading into
    """
    u1_ftp.rmd('upload_folder')
    actual = u1_ftp.lastresp
    expected = '250'
    n_eq(actual, expected)


###{{{ [START]: Delete Full Folder }}}###
delete_files = []
delete_folders = []


def save_delete_files():
    global delete_files
    x = deepcopy(delete_files)
    delete_files = []
    return x


def save_delete_folder():
    global delete_folders
    x = deepcopy(delete_folders)
    delete_folders = []
    return x


def a_callback(line):
    if not len(line) == 0:
        if not line[0] == 'd':
            global delete_files
            delete_files += [line.split(' ')[-1]]
        else:
            global delete_folders
            delete_folders += [line.split(' ')[-1]]


def rec_delete(a_ftp, to_delete):
    a_ftp.cwd(to_delete)
    a_ftp.dir(a_callback)
    fi = save_delete_files()
    fo = save_delete_folder()
    for f in fo:
        rec_delete(a_ftp, f)
    for f in fi:
        a_ftp.delete(f)
    a_ftp.cwd('..')
    a_ftp.rmd(to_delete)

###{{{ [END]: Delete Full Folder }}}###


@with_setup(setup_user_one, teardown_user_one)
def test_delete_full_folder():
    """
    Makes a dir fills it then deletes it while it is full.
    """
    u1_ftp.voidcmd('mkd %s' % 'temp_dir')
    u1_ftp.cwd('temp_dir')
    f_name = 'filler.txt'
    with open(f_name, 'w') as w:
        w.write('some text for the file')
    u1_ftp.storlines('STOR %s' % f_name, open(f_name, 'rb'))
    if os.path.isfile(f_name):
        os.remove(f_name)
    u1_ftp.cwd('..')
    rec_delete(u1_ftp, 'temp_dir')
    rep = u1_ftp.nlst()
    actual = not 'temp_dir' in rep
    n_ok(actual)


@with_setup(setup_user_one, teardown_user_one)
def test_rename():
    """
    Renames a file on the server.
    """
    f_name = 'filler.txt'
    with open(f_name, 'w') as w:
        w.write('some text for the file')
    u1_ftp.storlines('STOR %s' % f_name, open(f_name, 'rb'))
    if os.path.isfile(f_name):
        os.remove(f_name)
    u1_ftp.rename(f_name, 'abc.txt')
    rep = u1_ftp.lastresp
    x = u1_ftp.nlst()
    actual = (rep == '250') and ('abc.txt' in x)
    n_ok(actual)


@with_setup(setup_user_one, teardown_user_one)
def test_check_file():
    """
    Gets the checksum of a file
    NOTE: This has been changed so that the file is not longer written with an extra line at the end
    """
    f_name = 'check_this.txt'
    with open(f_name, 'w') as w:
        w.write('some text for the file')
    u1_ftp.storbinary('STOR %s' % f_name, open(f_name, 'rb'))
    local = hashlib.sha224(open(f_name, 'rb').read()).hexdigest()
    if os.path.isfile(f_name):
        os.remove(f_name)
    setup_callback()
    u1_ftp.retrlines('checksum %s' % f_name, callback)
    server = received
    server = ''.join(server)
    n_eq(server, local)


def test_share_exist():
    """
    I know how to do this, but i have not done it yet.
    """
    assert False


def test_share_upload():
    """
    I know how to do this, but i have not done it yet.
    """
    assert False


def teardown_module():
    """
    Deletes all the file off the test_server so the test can be ran again.
    """
    setup_admin()
    rec_delete(ftp, 'test_fs')
    ftp.voidcmd('shutdown')
