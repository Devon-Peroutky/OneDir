import errno
import pyinotify
from datetime import datetime
from client import OneDirFtpClient
from ftplib import error_perm, error_reply
from threading import Timer, Thread
import os
import json
import time
from OneDirServer.sql_manager import TableManager
from shutil import rmtree
from socket import error as SocketError


class ListenerContainer(object):
    watch_manager = pyinotify.WatchManager()
    move_to_folder = None
    move_to_file = None
    mask = pyinotify.ALL_EVENTS
    client = None
    __watch_dict = {}
    root_dir = None
    is_syncing = True
    config = None
    sync_db = None
    last_sync = '0'
    nick = None
    is_checking = True
    blockList = []
    check_update = False
    updating = False
    login = None

    def __init__(self):
        raise Exception('Static class. No __init__')

    @staticmethod
    def add_watch(path):
        # print  '<<<<<<<<', path, '>>>>>>>>>'
        if path == '.':
            path = ListenerContainer.root_dir
        temp = ListenerContainer.watch_manager.add_watch(path, ListenerContainer.mask, rec=True)
        ListenerContainer.__watch_dict.update(temp)

    @staticmethod
    def add_config(path):
        temp = ListenerContainer.watch_manager.add_watch(path, pyinotify.IN_MODIFY, rec=False)
        ListenerContainer.__watch_dict.update(temp)
        ListenerContainer.config = path

    @staticmethod
    def rm_watch(path):
        try:
            ListenerContainer.__watch_dict[path]
        except KeyError:
            if path == '.':
                path = ListenerContainer.root_dir
            else:
                path = './' + path
        ListenerContainer.watch_manager.rm_watch(ListenerContainer.__watch_dict[path], rec=True)
        del ListenerContainer.__watch_dict[path]

    @staticmethod
    def print_w():
        print ListenerContainer.__watch_dict


class EventHandler(pyinotify.ProcessEvent):
    """
    Note: The source code for pyinotify ProcessEvent explicitly mentions not to override the init
    """

    def process_IN_CREATE(self, event):
        """
        Raises a weird IOError while making a new document, because of some temp file that
        inotify is not picking up.  It seems safe to just ignore.
        """
        # print 'create'
        try:
            if self.checks(event):
                if ListenerContainer.is_syncing and not event.pathname[:2] == '.#':
                    if event.dir:
                        ListenerContainer.add_watch(event.pathname)
                        ListenerContainer.client.mkdir(event.pathname)
                    else:
                        while True:
                            try:
                                #print 'in create'
                                ListenerContainer.client.upload(event.pathname)
                                break
                            except SocketError or error_reply:
                                reset()
                else:
                    timer = now()
                    if event.dir:
                        ListenerContainer.add_watch(event.pathname)
                        x = [timer, 'MKDIR', event.pathname]
                    else:
                        x = [timer, 'UPLOAD', event.pathname]
                    ListenerContainer.sync_db.quick_push(x)
        except:
            # print 'Error in create', event.pathname
            pass

    def process_IN_CLOSE_WRITE(self, event):
        # print  'close write', event.pathname
        if self.checks(event):
            if ListenerContainer.is_syncing and not event.pathname[:2] == '.#':
                if event.dir:
                    ListenerContainer.add_watch(event.pathname)
                    ListenerContainer.client.mkdir(event.pathname)
                else:
                    while True:
                            try:
                                ListenerContainer.client.upload(event.pathname)
                                break
                            except SocketError or error_reply:
                                reset()
            else:
                timer = now()
                if event.dir:
                    ListenerContainer.add_watch(event.pathname)
                    x = [timer, 'MKDIR', event.pathname]
                else:
                    x = [timer, 'UPLOAD', event.pathname]
                ListenerContainer.sync_db.quick_push(x)

    def process_IN_DELETE(self, event):
        # print  'delete'
        try:
            if self.checks(event):
                if ListenerContainer.is_syncing:
                    if event.dir:
                        ListenerContainer.client.delete_folder(event.pathname)
                    else:
                        ListenerContainer.client.delete_file(event.pathname)
                else:
                    timer = now()
                    if event.dir:
                        x = [timer, 'DELFOLDER', event.pathname]
                    else:
                        x = [timer, 'DELFILE', event.pathname]
                    ListenerContainer.add_watch(event.pathname)
        except:
            # print  'Error in delete', event.pathname
            pass

    def process_IN_DELETE_SELF(self, event):
        if self.checks(event):
            if ListenerContainer.is_syncing:
                if event.dir:
                    ListenerContainer.rm_watch(event.pathname)
                    ListenerContainer.client.delete_folder(event.pathname)
                else:
                    ListenerContainer.client.delete_file(event.pathname)
            else:
                timer = now()
                if event.dir:
                    ListenerContainer.rm_watch(event.pathname)
                    x = [timer, 'DELFOLDER', event.pathname]
                else:
                    x = [timer, 'DELFILE', event.pathname]
                ListenerContainer.add_watch(event.pathname)

    def process_IN_MODIFY(self, event):
        # print  'modify'
        if event.pathname == ListenerContainer.config:
            time.sleep(1)
            jd = open(event.pathname)
            conf = json.load(jd)
            jd.close()
            ListenerContainer.is_syncing = conf['is_syncing']
            if not conf['is_syncing']:
                ListenerContainer.sync_db.connect()
            else:
                ListenerContainer.sync_db.disconnect()
                updater()
        elif self.checks(event):
            try:
                if ListenerContainer.is_syncing:
                    ListenerContainer.client.upload(event.pathname)
                else:
                    timer = now()
                    x = [timer, 'UPLOAD', event.pathname]
                    ListenerContainer.sync_db.quick_push(x)
            except:
                # print 'Error in Modify', event.pathname
                pass

    def process_IN_MOVED_FROM(self, event):
        # print  'move from'
        if self.checks(event):
            if ListenerContainer.is_syncing:
                if event.dir:
                    ListenerContainer.move_to_folder = event.pathname
                    ListenerContainer.rm_watch(event.pathname)
                else:
                    ListenerContainer.move_to_file = event.pathname
                ListenerContainer.client.move_from(event.pathname)
            else:
                timer = now()
                if event.dir:
                    ListenerContainer.rm_watch(event.pathname)
                else:
                    ListenerContainer.move_to_file = event.pathname
                x = [timer, 'MOVEFROM', event.pathname]
                ListenerContainer.sync_db.quick_push(x)
            t = Timer(0.1, self.timeout, [event.pathname])
            t.start()


    def process_IN_MOVED_TO(self, event):
        # print  'move to'
        ListenerContainer.move_to_folder = None
        ListenerContainer.move_to_file = None
        if ListenerContainer.is_syncing:
            if event.dir:
                ListenerContainer.add_watch(event.pathname)
            if not event.pathname[-1] == '~':
                try:
                    ListenerContainer.client.move_to(event.pathname)
                except:
                    # print  'Correction in move too', event.pathname
                    ListenerContainer.client.upload(event.pathname)
        else:
            timer = now()
            if event.dir:
                ListenerContainer.add_watch(event.pathname)
            if not event.pathname[-1] == '~':
                x = [timer, 'MOVETO', event.pathname]
                ListenerContainer.sync_db.quick_push(x)


    def process_default(self, event, to_append=None):
        if ListenerContainer.is_syncing:  # TODO I dont think that i will need to sync this.
            self.checks(event)

    def timeout(self, pathname):
        # print  'timeout'
        if ListenerContainer.is_syncing:
            if ListenerContainer.move_to_folder == pathname:
                try:
                    ListenerContainer.client.delete_folder(ListenerContainer.move_to_folder)
                except error_perm as e:
                    pass  # nothing to delete
                ListenerContainer.move_to_folder = None
            if ListenerContainer.move_to_file == pathname:
                try:
                    ListenerContainer.client.delete_file(ListenerContainer.move_to_file)
                except error_perm as e:
                    pass  # nothing to delete
                ListenerContainer.move_to_file = None
        else:
            timer = now()
            if ListenerContainer.move_to_folder == pathname:
                x = [timer, 'DELFOLDER', pathname]
                ListenerContainer.sync_db.quick_push(x)
                ListenerContainer.move_to_folder = None
            if ListenerContainer.move_to_file == pathname:
                x = [timer, 'DELFILE', pathname]
                ListenerContainer.sync_db.quick_push(x)
                ListenerContainer.move_to_file = None
 
    def checks(self, event):
        """
        Checks if the last command was a move from command.
        Checks if the file is a temp file.
        """
        # # print  'checks'
        if ListenerContainer.is_syncing:
            if ListenerContainer.move_to_folder:
                try:
                    ListenerContainer.client.delete_folder(ListenerContainer.move_to_folder)
                except error_perm as e:
                    pass  # nothing to delete
                ListenerContainer.move_to_folder = None
            if ListenerContainer.move_to_file:
                try:
                    ListenerContainer.client.delete_file(ListenerContainer.move_to_file)
                except error_perm as e:
                    pass  # nothing to delete
                ListenerContainer.move_to_file = None
            if event.pathname[-1] == '~':  # Temp file
                return False
            else:
                return True
        else:
            timer = now()
            if ListenerContainer.move_to_folder:
                x = [timer, 'DELFOLDER', event.pathname]
                ListenerContainer.sync_db.quick_push(x)
                ListenerContainer.move_to_folder = None
            if ListenerContainer.move_to_file:
                x = [timer, 'DELFILE', event.pathname]
                ListenerContainer.sync_db.quick_push(x)
                ListenerContainer.move_to_file = None
            if event.pathname[-1] == '~':  # Temp file
                return False
            else:
                return True


class ReverseClient():
    def __init__(self,  listener_root_dir):
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
        ## print  'site'
        self.rnfr_handler()
        arg = line.split(' ')[0]
        if arg in ['gettime', 'sync']:
            return False
        return 'site', line

    def rc_MKD(self, line):
        # print  'mkd'
        self.rnfr_handler()
        path = os.path.join(self.root_dir, line)
        os.mkdir(path)

    def rc_RNFR(self, line):
        ## print  'rnfr'
        path = os.path.join(self.root_dir, line)
        self.is_rnfr = path


    def rc_RNTO(self, line):
        ## print  'rnto'
        ### print  self.root_dir, line
        path = os.path.join(self.root_dir, line)
        os.rename(self.is_rnfr, path)
        self.is_rnfr = None

    def rc_CWD(self, line):
        ## print  'cwd'
        self.rnfr_handler()
        if line == '/':
            self.root_dir = os.getcwd()
        else:
            self.root_dir = os.path.join(self.root_dir, line)

    def rc_STOR(self, line):
        # print  'stor'
        self.rnfr_handler()
        path = os.path.join(self.root_dir, line)
        basename = os.path.split(path)[0]
        if basename == '/':
            basename = '.'
            path = ListenerContainer.root_dir + path
        try:
            ListenerContainer.rm_watch(basename)
            if path[-3:] == 'tmp':
                path = path[:-4]
                while True:
                    try:
                        ListenerContainer.client.download(path)
                        break
                    except error_perm:
                        time.sleep(1)
                        print 'stuck'
            else:
                ListenerContainer.client.download(path)
            filename = os.path.basename(path)
            os.rename(filename, path)
        except:
            # print  'error in rc stor', line
            pass
        finally:
            # print  path
            ListenerContainer.add_watch(basename)

    def rc_CDUP(self, line):
        ## print  'cdup'
        self.rnfr_handler()
        self.root_dir = os.path.join(self.root_dir, '..')
        self.root_dir = os.path.abspath(self.root_dir)

    def rc_RMD(self, line):
        ## print  'rmd'
        self.rnfr_handler()
        path = os.path.join(self.root_dir, line)
        rmtree(path)

    def rc_DELE(self, line):
        ## print  'del'
        self.rnfr_handler()
        path = os.path.join(self.root_dir, line)
        os.remove(path)


class ForwardClient(object):
    # def __init__(self, client):
    #     self.client = client
    #     self.mf = None
    def __init__(self):
        self.mf = None

    def fc_ADDWATCH(self, path):
        ## print  'addwatch'
        pass

    def fc_MKDIR(self, path):
        ## print  'mkdir'
        self.check()
        ListenerContainer.client.mkdir(path)

    def fc_UPLOAD(self, path):
        ## print  'upload'
        self.check()
        ListenerContainer.client.upload(path)

    def fc_DELFOLDER(self, path):
        ## print  'del folder'
        self.check()
        ListenerContainer.client.delete_folder(path)

    def fc_DELEFILE(self, path):
        ## print  'del file'
        self.check()
        ListenerContainer.client.delete_file(path)

    def fc_RMWATCH(self, path):
        ## print  'rm watch'
        pass

    def fc_MOVEFROM(self, path):
        ## print  'MOVEFROM'
        self.mf = path
        ListenerContainer.client.move_from(path)

    def fc_MOVETO(self, path):
        ListenerContainer.client.move_to(path)

    def check(self):
        if self.mf:
            try:
                ListenerContainer.client.delete_file(self.mf)
            except:
                try:
                    ListenerContainer.client.delete_folder(self.mf)
                except:
                    pass
        self.mf = None


def get_server_list(nick, last_sync):
    last_sync = int(last_sync)
    last_sync -= 1000000
    last_sync = str(last_sync)
    full = ListenerContainer.client.sync(last_sync)
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


def merge_lists(server_list, client_list):
    st = int(ListenerContainer.client.gettime())
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

    return merged_list


def sync(merged_list, sync_dir):
    r = ReverseClient(sync_dir)
    f = ForwardClient()
    for val in merged_list:
        # print  val
        cmd = None
        try:
            if len(val) == 5:
                line = str(val[4])
                if line[0] == '.':
                    line = line[1:]
                cmd = 'r.rc_%s("%s")' % (str(val[2]), line)
            else:
                cmd = 'f.fc_%s("%s")' % (str(val[1]), str(val[2]))
            # print  cmd
            eval(cmd)
        except error_reply:
            reset()
            try:
                eval(cmd)
            except:
                print 'error reply in syc', cmd
                if len(val) == 5:
                    pass
        except:
            print 'genereal error in sync', cmd
            pass
    f.check()


def checker():
    while ListenerContainer.is_checking:
        if not ListenerContainer.updating:
            time.sleep(5)
            try:
                updater()
            except KeyboardInterrupt:
                break
            except not KeyboardInterrupt:
                print 'error in checker'
                reset()
            ListenerContainer.check_update = True


def updater():
    ListenerContainer.updating = True
    old_nick = ListenerContainer.client.who_am_i()
    old_nick = old_nick.split(':')[1]
    ListenerContainer.client.i_am('sync')
    while True:
        try:
            start_sync = ListenerContainer.client.gettime()
            server_list = get_server_list(
                ListenerContainer.nick,
                ListenerContainer.last_sync
            )
            client_list = get_client_list()
            merged = merge_lists(server_list, client_list)
            ListenerContainer.last_sync = start_sync
            if len(merged) == 0:
                break
            else:
                sync(merged, ListenerContainer.root_dir)
        except error_reply:
            print 'error in updater'
            reset()
    ListenerContainer.client.i_am(old_nick)
    ListenerContainer.updating = False


def now():
    x = datetime.now()
    return x.strftime('%Y%m%d%H%M%S%f')

def reset():
    ListenerContainer.client = OneDirFtpClient(
        ListenerContainer.login['ip'],
        ListenerContainer.login['port'],
        ListenerContainer.login['username'],
        ListenerContainer.login['nick'],
        ListenerContainer.login['password'],
        ListenerContainer.login['root_dir']
    )


def main(ip, port):
    """
    Since pyintofiy says not override its init i made a static class for event handler to use.
    """
    conffile = os.path.expanduser('~') + '/.onedirclient'
    conffile = os.path.join(conffile, 'client.json')
    conffile = os.path.abspath(conffile)
    jd = open(conffile)
    conf = json.load(jd)
    jd.close()
    conf['ip'] = ip
    conf['port'] = port
    ListenerContainer.login = conf
    ListenerContainer.client = OneDirFtpClient(
        ip,
        port,
        conf['username'],
        conf['nick'],
        conf['password'],
        conf['root_dir']
    )
    t = Thread(target=checker, name='checker', args=())
    t.start()
    ListenerContainer.is_syncing = conf['is_syncing']
    ListenerContainer.root_dir = conf['root_dir']
    ListenerContainer.nick = conf['nick']
    notifier = pyinotify.Notifier(ListenerContainer.watch_manager, EventHandler())
    ListenerContainer.add_watch(conf['root_dir'])
    ListenerContainer.add_config(conffile)
    ListenerContainer.sync_db = TableManager('/home/justin/.onedirclient/sync.db', 'local')
    if not conf['is_syncing']:
        ListenerContainer.sync_db.connect()
    while True:
        try:
            notifier.process_events()
            if notifier.check_events():
                notifier.read_events()
        except KeyboardInterrupt:
            if ListenerContainer.move_to_folder:
                try:
                    ListenerContainer.client.delete_folder(ListenerContainer.move_to_folder)
                except error_perm:
                    pass  # Nothing to do
            if ListenerContainer.move_to_file:
                try:
                    ListenerContainer.client.delete_file(ListenerContainer.move_to_file)
                except error_perm:
                    pass  # Nothing to do
            ListenerContainer.is_checking = False
            notifier.stop()
            break
        except not KeyboardInterrupt:
            print 'error caught in main'
            reset()

if __name__ == '__main__':
    print  'DONT FOR GET TO SET IP... this is mine!'
    main('10.0.0.5', 1024)