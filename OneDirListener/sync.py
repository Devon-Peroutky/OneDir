#!/usr/bin/python2
from datetime import datetime


__author__ = 'Justin'

import os
from shutil import rmtree
from OneDirServer.sql_manager import TableManager


class LastMerge():
    check = None

    def __init__(self):
        pass


class ReverseClient():
    def __init__(self, client, listener_root_dir):
        self.root_dir = listener_root_dir
        self.is_rnfr = None
        self.client = client

    def rnfr_handler(self):
        """
        Checks to see if the last command was a 
        rename from command. 
        """
        if self.is_rnfr:
            pass  # TODO delete value in is_rnfr
        self.is_rnfr = None
        
    def rc_SITE(self, line):
        #print 'site'
        self.rnfr_handler()
        arg = line.split(' ')[0]
        if arg in ['gettime', 'sync']:
            return False
        return 'site', line

    def rc_MKD(self, line):
        #print 'mkd'
        self.rnfr_handler()
        path = os.path.join(self.root_dir, line)
        os.mkdir(path)

    def rc_RNFR(self, line):
        #print 'rnfr'
        path = os.path.join(self.root_dir, line)
        self.is_rnfr = path

    def rc_RNTO(self, line):
        #print 'rnto'
        ##print self.root_dir, line
        path = os.path.join(self.root_dir, line)
        os.rename(self.is_rnfr, path)
        self.is_rnfr = None

    def rc_CWD(self, line):
        #print 'cwd'
        self.rnfr_handler()
        if line == '/':
            self.root_dir = os.getcwd()
        else:
            self.root_dir = os.path.join(self.root_dir, line)

    def rc_STOR(self, line):
        #print 'stor'
        self.rnfr_handler()
        path = os.path.join(self.root_dir, line)
        self.client.download(path)
        filename = os.path.basename(path)
        os.rename(filename, path)

    def rc_CDUP(self, line):
        #print 'cdup'
        self.rnfr_handler()
        self.root_dir = os.path.join(self.root_dir, '..')
        self.root_dir = os.path.abspath(self.root_dir)

    def rc_RMD(self, line):
        #print 'rmd'
        self.rnfr_handler()
        path = os.path.join(self.root_dir, line)
        rmtree(path)

    def rc_DELE(self, line):
        #print 'del'
        self.rnfr_handler()
        path = os.path.join(self.root_dir, line)
        os.remove(path)

class ForwardClient(object):
    def __init__(self, client):
        self.client = client
        self.mf = None

    def fc_ADDWATCH(self, path):
        #print 'addwatch'
        pass

    def fc_MKDIR(self, path):
        #print 'mkdir'
        self.check()
        self.client.mkdir(path)

    def fc_UPLOAD(self, path):
        #print 'upload'
        self.check()
        self.client.upload(path)

    def fc_DELFOLDER(self, path):
        #print 'del folder'
        self.check()
        self.client.delete_folder(path)

    def fc_DELEFILE(self, path):
        #print 'del file'
        self.check()
        self.client.delete_file(path)

    def fc_RMWATCH(self, path):
        #print 'rm watch'
        pass

    def fc_MOVEFROM(self, path):
        #print 'MOVEFROM'
        self.mf = path
        self.client.move_from(path)

    def fc_MOVETO(self, path):
        self.client.move_to(path)

    def check(self):
        if self.mf:
            try:
                self.client.delete_file(self.mf)
            except:
                try:
                    self.client.delete_folder(self.mf)
                except:
                    pass
        self.mf = None

def get_server_list(client, nick, last_sync):
    full = client.sync(last_sync)
    filtered = []
    for val in full:
        if not val[1] in [nick, 'sync']:
            filtered += [val]
    return filtered


def get_client_list():
    t = TableManager(os.path.expanduser('~') + '/.onedirclient/sync.db', 'local')
    t.connect()
    client_list = t.pull()
    t.clear_table()
    t.disconnect()
    return client_list


def merge_lists(client, server_list, client_list):
    st = int(client.gettime())
    ct = datetime.now()
    ct = ct.strftime('%Y%m%d%H%M%S%f')
    ct = int(ct)
    diff = st - ct
    merged_list = []
    while len(server_list) > 0 or len(client_list) > 0:
        if len(server_list) == 0:
            merged_list += [client_list[0]]
            del client_list[0]
        elif len(client_list) == 0:
            merged_list += [server_list[0]]
            del server_list[0]
        else:
            if int(server_list[0][0]) >= int(client_list[0][0])-diff:
                merged_list += [server_list[0]]
                del server_list[0]
            else:
                merged_list += [client_list[0]]
                del client_list[0]
    if not merged_list == LastMerge.check:
        LastMerge.check = merged_list
        return merged_list
    else:
        print 'SKIPPED'
        LastMerge.check = merged_list
        return []


def sync(client, merged_list, sync_dir):
    r = ReverseClient(client, sync_dir)
    f = ForwardClient(client)
    for val in merged_list:
        print val
        try:
            if len(val) == 5:
                cmd = 'r.rc_%s("%s")' % (str(val[2]), str(val[4]))
            else:
                cmd = 'f.fc_%s("%s")' % (str(val[1]), str(val[2]))
            eval(cmd)
        except:
            print 'failed'
            if len(val) == 5:
                print val
    f.check()
    LastMerge.check = merged_list

def main():
    sync('a', '/home/justin/abc/')


if __name__ == '__main__':
    main()
