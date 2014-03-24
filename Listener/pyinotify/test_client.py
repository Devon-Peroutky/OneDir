import os
from shutil import copyfile, rmtree
from ftplib import FTP
from client import OneDirFptClient
from extra.testhelper.helpers import n_eq, n_ok
from nose.tools import timed

__author__ = 'Justin Jansen'
__status__ = 'Testing'
__date__ = '03/18/14'

# lol, this was a way bigger pain then i thought it would be to test.
# This has to manually ensure that the local filesystem matches the filesystem on the server


class SetupError(Exception):
    """
    Checks if you configured the server correct.
    """
    pass

###{{{START: needed setup info :START}}}###
ip = '10.0.0.6'
user = 'admin'
pw = 'admin'
test_dir = 'client_test'
###{{{END: needed setup info :END}}}###


###{{{START: some globals for testing :START}}}###
uploaded_file = os.path.join(test_dir, 'check_file.txt')
server_folder = os.path.join(test_dir, 'first_transfer')
test_image = 'test_img.png'
path_to_image = os.path.abspath('../../extra/fancy/small_strip.png')
###{{{END: some globals for testing :END}}}###


def setup_module():
    """
    Checks ip, username, password
    Checks/creates testing folder
    Checks for image to upload.
    """
    try:
        global test_dir
        global test_image
        ftp = FTP(ip, user, pw)
        ftp.quit()
        ftp.close()
    except:
        msg = 'Setup is incorrect. Make sure server is on. Ip: %s User: %s Password: %s ' % (ip, user, pw)
        raise SetupError(msg)
    else:
        if not os.path.isfile(path_to_image):
            msg = 'Image not found in path to image'
            raise SetupError(msg)
        if not os.path.exists(test_dir):
            os.mkdir(test_dir)
        test_dir = os.path.abspath(test_dir)
        copyfile(path_to_image, os.path.join(test_dir, test_image))
        test_image = os.path.join(test_dir, 'test_img.png')


def teardown_module():
    """
    Removes testing folder. After running this tests a few times
    I figured out the folders and files it is leaving on the server.
    """
    f = OneDirFptClient(ip, user, pw, test_dir)
    f.delete_file('test_img.png')
    f.quit()
    f.close()
    if os.path.exists(test_dir):
        rmtree(test_dir)


def test_connect():
    """
    Tests the __init__
    Checks for response code : 230
    """
    expected = '230'
    f = OneDirFptClient(ip, user, pw, test_dir)
    actual = f.lastresp
    f.quit()
    f.close()
    n_eq(expected, actual)


def test_upload_file():
    """
    Creates a text file, and tries to upload it to the server.
    Checks for response code: 226
    Checks for file on server.
    """
    expected = '226'
    with open(uploaded_file, 'w') as w:
        w.write('some text for the file')
    f = OneDirFptClient(ip, user, pw, test_dir)
    f.upload(uploaded_file)
    actual = f.lastresp
    nlst = f.nlst()
    f.quit()
    f.close()
    if os.path.split(uploaded_file)[1] in nlst:
        n_eq(expected, actual, f, 'upload')
    else:
        print 'nlst:', nlst
        n_ok(False, f, 'upload', message='Not in NLST')


def test_upload_image():
    """
    Tries to upload an image to the server.
    Checks for response code: 226
    Checks for file on server.
    @requires: ../../extra/fancy/small_strip.png to exist
    """
    expected = '226'
    f = OneDirFptClient(ip, user, pw, test_dir)
    f.upload(test_image)
    actual = f.lastresp
    nlst = f.nlst()
    f.quit()
    f.close()
    if os.path.split(test_image)[1] in nlst:
        n_eq(expected, actual, f, 'upload')
    else:
        print 'nlst:', nlst
        n_eq(False, f, 'upload', message='Not in NLST')


def test_download_file():
    """
    Tries to download a file from the server.
    Checks for response code: 226
    Checks if file exists.
    Note: This will downloaded the file into this folder not the testing folder.
    @requires: test_upload_file to pass.
    """
    expected = '226'
    if os.path.isfile(uploaded_file):
        os.remove(uploaded_file)
    f = OneDirFptClient(ip, user, pw, test_dir)
    f.download(uploaded_file)
    actual = f.lastresp
    f.quit()
    f.close()
    if os.path.isfile(uploaded_file):
        n_eq(expected, actual, f, 'download')
    else:
        n_ok(False, f, 'download', message='File not downloaded')


def test_download_image():
    """
    Tries to download a image from the server.
    Checks for response code: 226
    Checks that the file has been downloaded.
    @requires: test_upload_image to pass
    """
    expected = '226'
    if os.path.isfile(test_image):
        os.remove(test_image)
    f = OneDirFptClient(ip, user, pw, test_dir)
    f.download(test_image)
    actual = f.lastresp
    f.quit()
    f.close()
    if os.path.isfile(test_image):
        n_eq(expected, actual, f, 'download')
    else:
        n_ok(False, f, 'download', message='File not downloaded')


def test_move_as_move_file():
    """
    Tries to move a file from one place to another.
    Creates a folder to move it too.
    Check for response code: 250
    Checks the new new location on the server for the file.
    @requires: test_upload_file to pass
    """
    expected = '250'
    if not os.path.exists(server_folder):
        os.mkdir(server_folder)
    f = OneDirFptClient(ip, user, pw, test_dir)
    f.mkd('first_transfer')
    to_file = os.path.join(server_folder, os.path.split(uploaded_file)[1])
    f.move(uploaded_file, to_file)
    actual = f.lastresp
    nlst = f.nlst('first_transfer')
    f.quit()
    f.close()
    if os.path.split(uploaded_file)[1] in nlst:
        n_eq(expected, actual, f, 'move')
    else:
        print 'nlst:', nlst
        n_ok(False, f, 'move', message='File not moved')


def test_move_as_move_folder():
    """
    Tries to move one folder into another.
    Creates one more folder.
    Tries to move folder into it.
    Checks for response code: 250
    @requires: test_move_as_file to pass
    """
    expected = '250'
    folder = os.path.join(test_dir, 'second_transfer')
    if not os.path.exists(folder):
        os.mkdir(folder)
    f = OneDirFptClient(ip, user, pw, test_dir)
    f.mkd('second_transfer')
    to_folder = os.path.abspath(folder)
    f.move('first_transfer', to_folder)
    actual = f.lastresp
    nlst = f.nlst('second_transfer')
    f.quit()
    f.close()
    if os.path.split(uploaded_file)[1] in nlst:
        n_eq(expected, actual, f, 'move')
    else:
        print 'nlst:', nlst
        n_ok(False, f, 'move', message='File not moved')


def test_move_as_rename():
    """
    Uploads a file and then tries to rename it Tries to rename a file.
    Check for response code:
    Checks ls for new file name
    @requires: test_upload to pass
    """
    expected = '250'
    before_name = os.path.join(test_dir, 'before_name.txt')
    with open(before_name, 'wb') as w:
        w.write('some text')
    f = OneDirFptClient(ip, user, pw, test_dir)
    f.upload(before_name)
    after_name = os.path.join(test_dir, 'after_name.txt')
    f.move(before_name, after_name)
    actual = f.lastresp
    nlst = f.nlst()
    f.quit()
    f.close()
    if 'after_name.txt' in nlst and not 'before_name.txt' in nlst:
        n_eq(expected, actual, f, 'move')
    else:
        print "nlst:", nlst
        n_ok(False, f, 'move', message='File not in nlst')


def test_delete_file():
    """
    Tries to delete a file ofter the server.
    Checks for response code:
    Checks the file is gone
    @requires: test_move_as_rename to pass
    """
    expected = '250'
    f = OneDirFptClient(ip, user, pw, test_dir)
    after_name = os.path.join(test_dir, 'after_name.txt')
    f.delete_file(after_name)
    actual = f.lastresp
    nlst = f.nlst()
    f.quit()
    f.close()
    if not 'after_name.txt' in nlst:
        n_eq(expected, actual, f, 'delete_file')
    else:
        print 'nlst:', nlst
        n_ok(False, f, 'delete_file', message='File still in nlst')

@timed(5)
def test_delete_empty_folder():
    """
    Tries to delete an empty folder
    Checks for response code: 250
    Checks that the file is gone
    """
    expected = '250'
    folder = os.path.join(test_dir, 'delete_this')
    if not os.path.exists(folder):
        os.mkdir(folder)
    f = OneDirFptClient(ip, user, pw, test_dir)
    f.mkd('delete_this')
    f.delete_folder(folder)
    actual = f.lastresp
    nlst = f.nlst()
    f.quit()
    f.close()
    if not 'delete_this' in nlst:
        n_eq(expected, actual, f, 'delete_folder')
    else:
        print 'nlst:', nlst
        n_ok(False, f, 'delete_folder', message='Folder in nlst')


@timed(5)
def test_delete_full_folder():
    """
    Tries to delete a folder with items in it.
    Checks for response code: 250
    Check for folder in dir
    """
    expected = '250'
    f = OneDirFptClient(ip, user, pw, test_dir)
    folder = os.path.join(test_dir, 'second_transfer')
    f.delete_folder(folder)
    actual = f.lastresp
    nlst = f.nlst()
    f.quit()
    f.close()
    if not 'second_transfer' in nlst:
        n_eq(expected, actual, f, 'delete_folder')
    else:
        print 'nlst:', nlst
        n_ok(False, f, 'delete_folder', message='Folder in nlst')