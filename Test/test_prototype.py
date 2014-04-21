__author__ = 'rupali'
import os
import sys
from shutil import copyfile, rmtree
from ftplib import FTP
#from extra.testhelper.helpers import n_eq, n_ok
from nose.tools import timed
import psutil
import prototype
#sys.path.insert(0, '../../Server/sql/')
#from OneDir.sql_manager import TableAdder, TableManager
#sys.path.insert(0, '../../Server/ftpserver')
from OneDir.Server.ftpserver.testing_server import main, setup_users
import time

class SetupError(Exception):
    """
    Checks if you configured the server correct.
    """
    pass

###{{{START: needed setup info :START}}}###
ip = '127.27.43.39'
user = 'admin'
pw = 'admin'
test_dir = '/home/rupali/Documents/CS3240/OneDir/extra/WatchTesting'
check_dir = '/home/rupali/Documents/CS3240/toMirror'
###{{{END: needed setup info :END}}}###


###{{{START: some globals for testing :START}}}###
uploaded_file = os.path.join(test_dir, 'check_file.txt')
existing_file = os.path.join(check_dir, 'check_file.txt')
uploaded_folder = os.path.join(test_dir, 'first_transfer')
checkFolder = os.path.abspath(check_dir)
test_image = 'test_img.png'
path_to_image = os.path.abspath('../../extra/fancy/small_strip.png')
###{{{END: some globals for testing :END}}}###


def setup_module():
    """
    Starts running the server by running python testing_server.py
    Starts running the watch by calling main in prototype.py
    """
    #consider running server in another thread rather than executing it manually
    #setup_users()
    #main()
    #prototype.main()


def teardown_module():
    """
    terminates prototype.py; terminates testing_server.py
    consider deleting crap here
    """
    #for process in psutil.process_iter():
    #    if process.cmdline == ['python', 'prototype.py']:
    #        print("Prototype process found. Terminating.")
    #        process.terminate()
    #        break
    #for process in psutil.process_iter():
    #    if process.cmdline == ['python', '../../Server/ftpserver/testing_server.py']:
    #        print("Server process found. Terminating...")
    #        process.terminate()
    #watchpath = test_dir
    filelist = os.listdir(test_dir) #watchTesting
    mirrorList = os.listdir(check_dir) #toMirror
    for file in filelist:
        t = os.path.join(test_dir, file)
        if os.path.isfile(t):
            os.remove(t)
        else:
            os.rmdir(t)
    # delete everything in toMirror:
    for file in mirrorList:
        t = os.path.join(check_dir, file)
        if os.path.isfile(t):
            os.remove(t)
        else:
            os.rmdir(t)


def test_createFolder():
    """
    Creates a folder in Watch_Testing, and verifies that the folder was created in toMirror
    """
    print "here!"
    dir_name = "TestMkDir"
    the_dir = os.path.join(test_dir, dir_name) #filepath = /WatchTesting/TestMkDir
    os.mkdir(the_dir) #actually make the empty folder
    time.sleep(2)
    #check ToMirror to make sure stuff happened
    if os.path.exists(os.path.join(check_dir, dir_name)):
        assert True
    else:
        assert False


# def test_delFolder():
#     """
#     Creates and deletes the folder "TestDel" and verifies deletion
#     """
#     dir_name = "TestDel"
#     the_dir = os.path.join(test_dir, dir_name)
#     os.mkdir(the_dir) #assuming this works based on passing the last test, test_createFolder()
#     time.sleep(2)
#     folderPath = os.path.join(check_dir, dir_name) #in toMirror
#     if os.path.exists(folderPath):
#         print "exists in toMirror"
#         #os.rmdir(the_dir)
#         rmtree(the_dir)
#         time.sleep(2)
#         if not os.path.exists(the_dir):
#             print "deleted from WatchTesting"
#             if not os.path.exists(folderPath):
#                 print "deleted from toMirror"
#                 assert True
#             else:
#                 print "not deleted from toMirror"
#                 assert False
#     else:
#         print "in the failure"
#         return False


def test_createFile():
    """
    Creates a file in Watch_Testing, and verifies that the file was created
    """
    file_name = "TestMkFile.txt"
    filepath = os.path.join(test_dir, file_name)  # filepath = /WatchTesting/TestMkDir
    checkpath = os.path.join(check_dir, file_name)  # looks in toMirror
    with open(filepath, 'w') as w:
        w.write("abc")
    time.sleep(2)
    if os.path.exists(checkpath):
        assert True
    else:
        assert False


# def test_delFile():
#     """
#     Creates a file and then deletes it
#     """
#     file_name = "DelFile.txt"
#     filepath = os.path.join(test_dir, file_name)
#     checkpath = os.path.join(check_dir, file_name)
#     with open(filepath, 'w') as w:
#         w.write("foo")
#     time.sleep(2)
#     if os.path.exists(checkpath):
#         os.remove(filepath)
#         time.sleep(2)
#         if not os.path.exists(checkpath):
#             assert True
#         else:
#             assert False
#     else:
#         assert False


def test_renameDir():
    """
    Creates a directory and then renames it
    """
    counter = 0
    file_name = "toRename"
    create_filepath = os.path.join(test_dir, file_name)
    rename_filepath = os.path.join(test_dir, "renamed")
    toRename_checkpath = os.path.join(check_dir, file_name)
    checkpath = os.path.join(check_dir, "renamed")
    os.mkdir(create_filepath)
    time.sleep(2)
    if os.path.exists(toRename_checkpath):
        counter = 1
        os.rename(create_filepath, rename_filepath) #OSError possibility, but don't know why
        time.sleep(2)
        if os.path.exists(checkpath):
            counter = 2
    if counter == 2:
        assert True
    else:
        assert False


def test_renameFile():
    """
    Creates a file and renames it
    """
    counter = 0
    file_name = "toRename.txt"
    create_filepath = os.path.join(test_dir, file_name)
    rename_filepath = os.path.join(test_dir, "renamed.txt")
    toRename_checkpath = os.path.join(check_dir, file_name)
    checkpath = os.path.join(check_dir, "renamed.txt")
    with open(create_filepath, 'w') as w:
        w.write("bar")
    time.sleep(2)
    if os.path.exists(toRename_checkpath):
        counter = 1
        os.rename(create_filepath, rename_filepath)
        time.sleep(2)
        if os.path.exists(checkpath):
            counter = 2
    if counter == 2:
        assert True
    else:
        assert False


def test_modifyFile():
    """
    Modifies the end of the file by appending a string to it
    """
    file_name = "modify.txt"
    filepath = os.path.join(test_dir, file_name) #watchtesting
    checkpath = os.path.join(check_dir, file_name) #toMirror
    with open(filepath, 'w') as w:
        w.write("foo")
    time.sleep(2)
    with open(filepath, 'a') as adding:
        adding.write("bar")
    time.sleep(2)
    with open(checkpath, 'r') as checking:
        s = checking.readline()
        print s
    if s == "foobar":
        assert True
    else:
        assert False