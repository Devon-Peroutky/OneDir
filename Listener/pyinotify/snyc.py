#!/usr/bin/python2
import sys

__author__ = 'Justin'

# This is just a demo, not actually useful yet.
# To use.  Start a fresh and empty server.  Start watch2.py.
# In the watch folder create a few files and folder.
# Stop the Listener (Leave Server On!)  Copy this (sync.py) into another directory.
# Run it from that directory.  It should print a mess of things.
# However, even with all those errors it still seems to remake the files
# that were made while the listener was on.

# If you have time play with it, and see if you can find where it does not work
# Write up a way to recreate the problem.  This is far from being fully tested.

# it works with:
# mkdir a
# cd a
# mkdir b c
# touch 123.txt
# cat 123 > 123.txt
# cd b
# touch 456.txt
# cd ../c
# touch 789.txt
# cd ..
# rm -r -f c
# STOP LISTENER

import os
from shutil import rmtree
from OneDir.Listener.pyinotify.client import OneDirFtpClient

o = OneDirFtpClient('10.0.0.5', 'admin', 'admin', os.getcwd())

class ReverseClient():
    def __init__(self, listener_root_dir):
        self.root_dir = listener_root_dir
        self.is_rnfr = None

    def rnfr_handler(self):
        """
        Checks to see if the last command was a 
        rename from command. 
        """
        if self.is_rnfr:
            pass  # TODO delete value in is_rnfr
        self.is_rnfr = None
        
    def rc_SITE(self, line):
        print 'site'
        self.rnfr_handler()
        arg = line.split(' ')[0]
        if arg in ['gettime', 'sync']:
            return False
        return 'site', line

    def rc_MKD(self, line):
        print 'mkd'
        self.rnfr_handler()
        path = os.path.join(self.root_dir, line)
        os.mkdir(path)

    def rc_RNFR(self, line):
        print 'rnfr'
        path = os.path.join(self.root_dir, line)
        self.is_rnfr = path

    def rc_RNTO(self, line):
        print 'rnto'
        print self.root_dir, line
        path = os.path.join(self.root_dir, line)
        os.rename(self.is_rnfr, path)
        self.is_rnfr = None

    def rc_CWD(self, line):
        print 'cwd'
        self.rnfr_handler()
        if line == '/':
            self.root_dir = os.getcwd()
        else:
            self.root_dir = os.path.join(self.root_dir, line)

    def rc_STOR(self, line):
        print 'stor'
        self.rnfr_handler()
        path = os.path.join(self.root_dir, line)
        o.download(path)
        filename = os.path.basename(path)
        os.rename(filename, path)

    def rc_CDUP(self, line):
        print 'cdup'
        self.rnfr_handler()
        self.root_dir = os.path.join(self.root_dir, '..')
        self.root_dir = os.path.abspath(self.root_dir)

    def rc_RMD(self, line):
        print 'rmd'
        self.rnfr_handler()
        path = os.path.join(self.root_dir, line)
        rmtree(path)

    def rc_DELE(self, line):
        print 'del'
        self.rnfr_handler()
        path = os.path.join(self.root_dir, line)
        os.remove(path)


def main():
    dont_need = ['PWD', 'LIST']
    r = ReverseClient(os.getcwd())
    print o.gettime()
    a = '20140419181257404987'
    x = o.sync(a)
    for y in x:
        if not y[2] in dont_need:
            try:
                cmd = 'r.rc_%s("%s")' % (str(y[2]), str(y[4]))
                cmd = eval(cmd)
                if cmd:
                    print cmd
            except:
                print
                print y
                print sys.exc_info()
                print


if __name__ == '__main__':
    main()
