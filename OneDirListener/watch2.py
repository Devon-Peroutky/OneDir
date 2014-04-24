import pyinotify
from client import OneDirFtpClient
from ftplib import error_perm
from threading import Timer
import os
import json
import time


class EventHandler(pyinotify.ProcessEvent):
    """
    Note: The source code for pyinotify ProcessEvent explicitly mentions not to override the init
    """

    def process_IN_CREATE(self, event):
        """
        Raises a weird IOError while making a new document, because of some temp file that
        inotify is not picking up.  It seems safe to just ignore.
        """
        try:
            if self.checks(event):
                if ListenerContainer.is_syncing and not event.pathname[:2] == '.#':
                    if event.dir:
                        ListenerContainer.add_watch(event.pathname)
                        ListenerContainer.client.mkdir(event.pathname)
                    else:
                        ListenerContainer.client.upload(event.pathname)
        except:
            print 'in create', event.pathname

    def process_IN_CLOSE_WRITE(self, event):
        print 'write close', event.pathname
        if self.checks(event):
            print event.pathname[:2] == '.#'
            if ListenerContainer.is_syncing and not event.pathname[:2] == '.#':
                if event.dir:
                    ListenerContainer.add_watch(event.pathname)
                    ListenerContainer.client.mkdir(event.pathname)
                else:
                    ListenerContainer.client.upload(event.pathname)

    def process_IN_DELETE(self, event):
        print 'delete', event.pathname
        try:
            if ListenerContainer.is_syncing:
                if self.checks(event):
                    if event.dir:
                        ListenerContainer.client.delete_folder(event.pathname)
                    else:
                        ListenerContainer.client.delete_file(event.pathname)
        except:
            print 'in delete', event.pathname

    def process_IN_DELETE_SELF(self, event):
        print 'delete self'
        if ListenerContainer.is_syncing:
            if self.checks(event):
                if event.dir:
                    ListenerContainer.rm_watch(event.pathname)
                    ListenerContainer.client.delete_folder(event.pathname)
                else:
                    ListenerContainer.client.delete_file(event.pathname)

    def process_IN_MODIFY(self, event):
        print 'in modify'
        if event.pathname == ListenerContainer.config:
            time.sleep(1)
            jd = open(event.pathname)
            conf = json.load(jd)
            jd.close()
            ListenerContainer.is_syncing = conf['is_syncing'] 
        elif ListenerContainer.is_syncing:
            if self.checks(event):
                ListenerContainer.client.upload(event.pathname)

    def process_IN_MOVED_FROM(self, event):
        print 'moved from'
        if ListenerContainer.is_syncing:
            if self.checks(event):
                if event.dir:
                    ListenerContainer.move_to_folder = event.pathname
                    ListenerContainer.rm_watch(event.pathname)
                else:
                    ListenerContainer.move_to_file = event.pathname
                ListenerContainer.client.move_from(event.pathname)
                t = Timer(0.1, self.timeout, [event.pathname])
                t.start()
            
    def process_IN_MOVED_TO(self, event):
        print 'moved 2'
        if ListenerContainer.is_syncing:
            ListenerContainer.move_to_folder = None
            ListenerContainer.move_to_file = None
            if event.dir:
                ListenerContainer.add_watch(event.pathname)
            if not event.pathname[-1] == '~':
                try:
                    ListenerContainer.client.move_to(event.pathname)
                except:
                    ListenerContainer.client.upload(event.pathname)

    def process_default(self, event, to_append=None):
        print 'default'
        if ListenerContainer.is_syncing:
            self.checks(event)

    def timeout(self, pathname):
        print 'timeout'
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
 
    def checks(self, event):
        """
        Checks if the last command was a move from command.
        Checks if the file is a temp file.
        """
        print 'checks'
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

    def __init__(self):
        raise Exception('Static class. No __init__')

    @staticmethod
    def add_watch(path):
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
            path = './' + path
        ListenerContainer.watch_manager.rm_watch(ListenerContainer.__watch_dict[path], rec=True)
        del ListenerContainer.__watch_dict[path]
        
#def main(ip, port, user, nick ,password, root_dir):
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
    ListenerContainer.client = OneDirFtpClient(ip, port, conf['username'], conf['nick'], conf['password'], conf['root_dir'])
    ListenerContainer.is_syncing = conf['is_syncing']
    ListenerContainer.root_dir = conf['root_dir']
    notifier = pyinotify.Notifier(ListenerContainer.watch_manager, EventHandler())
    ListenerContainer.add_watch(conf['root_dir'])
    ListenerContainer.add_config(conffile)
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
            notifier.stop()
            break
        # except:
        #     pass  # To make sure it never turns off without interrupt

if __name__ == '__main__':
    print 'DONT FOR GET TO SET IP... this is mine!'
    main('10.0.0.5', 1024)