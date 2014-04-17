#!/usr/bin/python2

from ftplib import FTP
from nose import with_setup
from OneDir.extra.testhelper.helpers import n_eq, n_ok
from datetime import datetime

ip = '10.0.0.5'
port = 21
admin = 'admin'
admin_pw = 'admin'

password = 'abc'
start = None

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
def test_get_time():
    """
    Tries to get the server time. 
    Checks it length (for formatting)
    Checks for responce code: 200
    Tries to cast time to an int.
    """
    expected = '200'
    x = ftp.sendcmd('site gettime')
    actual = ftp.lastresp
    x = x.split(' ')[1]
    if len(x) == 20:
        int(x)
        global start
        start = x
        n_eq(expected, actual)
    else:
        print 'length: ', len(x)
        print 'value', x
        n_ok(False)

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
    ftp.sendcmd('site useradd user_one 0 %s' % password)
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
    ftp.sendcmd('site useradd user_two 0 %s' % password)
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
    @requires: get time to pass
    """
    x = ftp.retrlines('site sync %s' % start, callback)
    for r in received:
        print r
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


usr = 'user_three'
new_pw = 'def' 


@with_setup(setup_admin, teardown_admin)
def test_admin_change_password():
    """
    Creates a new users.
    Changes new user password.
    Attempts to log in with new password.
    Checks for responce code: 200
    """
    expected = '200'
    ftp.sendcmd('site useradd %s 0 %s' % (usr, password))
    ftp.sendcmd('site changepw %s %s' % (usr, new_pw))  
    actual = ftp.lastresp
    f = FTP()
    f.connect(ip)
    try:
        f.login(usr, new_pw)
        n_eq(expected, actual)
    except:
        n_ok(False, message='Authentication Failed')


def test_user_change_password():
    """
    User logs in, and attemps to change their own password.
    @requires: admin change password to work.
    User logs out and then attemps to log in with new password.
    Checks for responce code: 200
    """
    expected = '200'
    f = FTP()
    f.connect(ip)
    f.login(usr, new_pw)
    pw_three = 'hij'
    f.sendcmd('site setpw %s %s' % (new_pw, pw_three))
    actual = f.lastresp
    f.quit()
    f.close()
    f.connect(ip)
    try:
        f.login(usr, pw_three)
        n_eq(expected, actual)
    except:
        n_ok(False, message='Authentication Failed')


@with_setup(setup_admin, teardown_admin)
def test_set_flag_one_arg():
    """
    Set a single arg flag in the database.
    Checks for responce code: 200
    Check for flag in sync.
    @require: sync to pass.
    """
    expected = '200'
    ftp.sendcmd('site setflag abc')
    actual = ftp.lastresp
    print start
    ftp.retrlines('site sync %s' % start, callback)
    check = False
    for r in reversed(received):
        x = eval(r)
        if x[2] == 'FLAG':
            if x[3] == 'abc' and x[4] == 'abc':
                check = True
                break
    if check:
        n_eq(expected, actual)
    else:
        n_ok(check, message='Flag not found')



@with_setup(setup_admin, teardown_admin)
def test_set_flag_two_args():
    """
    Set a single arg flag in the database.
    Checks for responce code: 200
    Check for flag in sync.
    @require: sync to pass.
    """
    expected = '200'
    ftp.sendcmd('site setflag abc def')
    actual = ftp.lastresp
    ftp.retrlines('site sync %s' % start, callback)
    check = False
    for r in reversed(received):
        x = eval(r)
        if x[2] == 'FLAG':
            if x[3] == 'abc' and x[4] == 'def':
                check = True
                break
    if check:
        n_eq(expected, actual)
    else:
        for r in received:
            print r
        n_ok(check, message='Flag not found')

@with_setup(setup_admin, teardown_admin)
def test_who_am_i():
    """
    Ask the server for its secondary username.
    Checks to see that it is ip adress still.
    Checks for responce code: 200
    """
    expected = '200'
    x = ftp.sendcmd('site whoami')
    actual = ftp.lastresp
    x = x.split(':')[-1]
    x = x.split('.')
    checker = True
    for y in x:
        try:
            int(y)
        except:
            checker = False
            break
    if checker:
        n_eq(expected, actual)
    else:
        n_ok(checker, message='not a ip')

@with_setup(setup_admin, teardown_admin)
def test_i_am():
    """
    Sets secondary username.
    Checks for responce code: 200
    Checks that the name was set. 
    @requres: who am i to pass
    """
    expected = '200'
    ftp.sendcmd('site iam abc')
    actual = ftp.lastresp
    x = ftp.sendcmd('site whoami')
    x = x.split(':')
    x[0] = x[0].split(' ')[1]
    if x[0] == 'admin' and x[1] == 'abc':
        n_eq(expected, actual)
    else:
        print x
        n_ok(False, message='name not set')

def teardown_module():
    f = FTP()
    f.connect(ip)
    f.login('admin', 'admin')
    f.sendcmd('site userdel user_three')
    f.quit()
    f.close()
