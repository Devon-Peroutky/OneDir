#!/usr/bin/python2

from hashlib import md5
from random import choice
from hash_chars import hash_chars 
from binascii import b2a_base64
from ftplib import FTP
from nose import with_setup
from OneDir.extra.testhelper.helpers import n_eq, n_ok
from datetime import datetime
import ntplib, time

ip = '10.0.0.5'
port = 21
admin = 'admin'
admin_pw = 'admin'

salt = ''.join(choice(hash_chars) for i in range(100))
password = 'abc'
split = len(salt)/2
password = salt[:split] + password + salt[split:]
password = b2a_base64(md5(password).digest()).strip()
#start = str(datetime.now())    
start = ntplib.NTPClient()
start = start.request('pool.ntp.org')
start = time.strftime('%Y%m%d%H%M%S', time.localtime(start.tx_time))


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
        ftp.connect(ip)
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
    received += [line]


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
        ftp.close()
    except AttributeError:
        pass
    ftp = None


@with_setup(setup_admin, teardown_admin)
def test_user_list():
    """
    Gets a list of all the users 
    Checks for responce code: 226
    Checks a line representing admin exists.
    """
    expected = '226'
    ftp.retrlines('site userlist', callback)
    actual = ftp.lastresp
    line = "('admin', 1, 'welcome', 'goodbye')"
    if line in received:
        n_eq(expected, actual)
    else:
        print received
        n_ok(False, message='line not recieved') 


@with_setup(setup_admin, teardown_admin)
def test_user_add():
    """
    Attempts to create a user
    @requires: user_list to pass.
    Checks for responce code: 200
    Checks that user is in database.
    """
    expected = '200'
    ftp.sendcmd('site useradd user_one 0 %s %s' % (password, salt))
    actual = ftp.lastresp
    ftp.retrlines('site userlist', callback)
    line = "('user_one', 0, 'welcome', 'goodbye')"
    if line in received:
        n_eq(expected, actual)
    else:
        print received
        n_ok(False, message='User not added')


@with_setup(setup_admin, teardown_admin)
def test_user_del():
    """
    Attempts to delete a user.
    @requires: user_add to pass.
    Check for responce code: 200
    Checks that user is not in database.
    """
    expected = '200'
    ftp.sendcmd('site userdel user_one')
    actual = ftp.lastresp
    line = "('user_one', 0, 'welcome', 'goodbye')"
    ftp.retrlines('site userlist', callback)
    if not line in received:
        n_eq(expected, actual)
    else:
        print received
        n_ok(False, message='user not deleted')


@with_setup(setup_admin, teardown_admin)
def test_deactivate():
    """
    Checks if a user can deactivate their own account.
    Checks if connection is termated.
    Attempts to log in again.
    @requires: user_add to pass
    """
    ftp.sendcmd('site useradd user_two 0 %s %s' % (password, salt))
    f = FTP()
    f.connect(ip)
    f.login('user_two', 'abc')
    f.sendcmd('site deactiv')
    try:
        f.nlst()
        n_ok(False, message='did not disconnect')
    except:
        pass
    try:
        f.connect(ip)
        f.login('user_two', 'abc')
        n_ok(False, message='could still log in')
    except:
        pass
    assert True


@with_setup(setup_admin, teardown_admin)
def test_sync():
    """
    Tries to get a list of events. That occurred for the admin user. During this test.
    """
    x = ftp.retrlines('site sync %s' % start, callback)
    for r in received:
        print r
    assert False
    if len(received) > 0:
        assert True
    else:
        assert False    

@with_setup(setup_admin, teardown_admin)
def test_get_log():
    """
    Gives the location of log. A normal download command can be used to download it.
    Checks for responce code: 200
    Check the name of the log.
    """
    expected = '200'
    log = ftp.sendcmd('site getlog')
    actual = ftp.lastresp
    log = log.split('/')[-1]
    if log == 'pyftpd.log':
        n_eq(expected, actual)
    else:
        print log
        n_ok(False)
