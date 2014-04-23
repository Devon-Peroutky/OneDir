import os
import pyinotify
from client import OneDirFtpClient
from ftplib import error_perm

# Unfixed bug: To reproduce
# Create a folder. Name that folder. Delete the folder. Make a file with exact same name.


class EventHandler(pyinotify.ProcessEvent):
    """
    Note: The source code for pyinotify ProcessEvent explicitly mentions not to override the init
    """

    def process_IN_CREATE(self, event):
        if self.checks(event):
            if event.dir:
                ListenerContainer.add_watch(event.pathname)
                ListenerContainer.client.mkdir(event.pathname)
            else:
                ListenerContainer.client.upload(event.pathname)

    def process_IN_DELETE(self, event):
        if self.checks(event):
            if event.dir:
                ListenerContainer.client.delete_folder(event.pathname)
            else:
                ListenerContainer.client.delete_file(event.pathname)

    def process_IN_DELETE_SELF(self, event):
        if self.checks(event):
            if event.dir:
                ListenerContainer.rm_watch(event.pathname)
                ListenerContainer.client.delete_folder(event.pathname)
            else:
                ListenerContainer.client.delete_file(event.pathname)

    def process_IN_MODIFY(self, event):
        if self.checks(event):
            ListenerContainer.client.upload(event.pathname)

    def process_IN_MOVED_FROM(self, event):
        if self.checks(event):
            if event.dir:
                ListenerContainer.move_to_folder = event.pathname
                ListenerContainer.rm_watch(event.pathname)
            else:
                ListenerContainer.move_to_file = event.pathname
            ListenerContainer.client.move_from(event.pathname)

    def process_IN_MOVED_TO(self, event):
        ListenerContainer.move_to_folder = None
        ListenerContainer.move_to_file = None
        if event.dir:
            ListenerContainer.add_watch(event.pathname)
        if not event.pathname[-1] == '~':
            ListenerContainer.client.move_to(event.pathname)

    def process_default(self, event, to_append=None):
        self.checks(event)

    def checks(self, event):
        """
        Checks if the last command was a move from command.
        Checks if the file is a temp file.
        """
        if ListenerContainer.move_to_folder:
            try:
                ListenerContainer.client.delete_folder(ListenerContainer.move_to_folder)
            except error_perm as e:
                print e  # TODO delete
                pass  # nothing to delete
            ListenerContainer.move_to_folder = None
        if ListenerContainer.move_to_file:
            try:
                ListenerContainer.client.delete_file(ListenerContainer.move_to_file)
            except error_perm as e:
                print e  # TODO delete
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

    def __init__(self):
        raise Exception('Static class. No __init__')

    @staticmethod
    def add_watch(path):
        path = os.path.relpath(path, ListenerContainer.root_dir)
        temp = ListenerContainer.watch_manager.add_watch(path, ListenerContainer.mask, rec=True)
        ListenerContainer.__watch_dict.update(temp)

    @staticmethod
    def rm_watch(path):
        path = os.path.relpath(path, ListenerContainer.root_dir)
        try:
            ListenerContainer.__watch_dict[path]
        except KeyError:
            path = './' + path
        ListenerContainer.watch_manager.rm_watch(ListenerContainer.__watch_dict[path], rec=True)
        del ListenerContainer.__watch_dict[path]


def main(ip, user, password, root_dir):
    """
    Since pyintofiy says not override its init i made a static class for event handler to use.
    """
    ListenerContainer.root_dir = root_dir
    ListenerContainer.client = OneDirFtpClient(ip, '21', user, 'BigCheese', password, ListenerContainer.root_dir)
    notifier = pyinotify.Notifier(ListenerContainer.watch_manager, EventHandler())
    ListenerContainer.add_watch('.')
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


if __name__ == '__main__':
    print 'DONT FOR GET TO SET IP... this is mine!'
    main('127.0.0.1', 'admin', 'admin', os.getcwd())
