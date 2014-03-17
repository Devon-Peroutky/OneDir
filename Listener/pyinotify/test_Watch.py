__author__ = 'Devon'
import os
import pyinotify

class ModHandler(pyinotify.ProcessEvent):
    '''
        Create -> Move_From -> Move_To
        Delete: Move_From
        Rename: Move_From, Move_To
        New File: Create
        Copied In: Create
        Modified: Create, Move_From, Move_To
        Just Getting a Move_To means we either had a MODIFICATION or a RENAMING
    '''
    print "IN HERE"

    def __init__(self):
        print "SUP"
        self.directory=False
        self.movedTo=False
        self.movedFrom=False
        self.create=False

    # --- If a file or directory is CREATED or MODIFIED---
    def process_IN_CREATE(self, event):
        print 'Created: '
        self.directory = event.dir
        self.create=True
        self.post_processing()

    # --- If a file or directory is DELETED or RENAMED or MODIFIED---
    def process_IN_MOVED_FROM(self, event):
        print 'Moved From'
        self.directory = event.dir
        self.movedFrom=True
        self.post_processing()

    def process_IN_DELETE(self, event):
        print 'Deleted'
        self.directory = event.dir
        self.movedFrom=True
        self.post_processing()

    def process_IN_MOVED_TO(self, event):
        print 'Move To'
        self.directory = event.dir
        self.movedTo=True
        self.post_processing()

    def post_processing(self):
        movedFrom=self.movedFrom
        movedTo=self.movedTo
        create=self.create
        directory=self.directory
        print "Moved From: " + str(movedFrom)
        print "Moved To: " + str(movedTo)
        print "Create: " + str(create)


        # Delete
        if (movedFrom and not movedTo and not create):
            if directory:
                print "Directory Deleted!"
            else:
                print "File Deleted!"

        # Rename
        elif (movedTo and movedFrom and not create):
            if directory:
                print "Directory Renamed!"
            else:
                print "File Renamed!"

        # Modified
        elif (create and movedTo and movedFrom):
            if directory:
                print "Directory Modified!"
            else:
                print "File Modified!"

        # New File
        elif (create and not movedTo and not movedFrom):
            if directory:
                print "Directory Create!"
            else:
                print "File Created!"
        else:
            print "Rename or Modification!"
        print "-------------------------------"

        # ----- Reset -----
        self.directory=False
        self.movedTo=False
        self.movedFrom=False
        self.create=False

def main():
    # --- Values ---
    directory="/home/ubuntu/Documents/School/Spring_2014/Software_Development/THE_PROJECT"
    mask = pyinotify.ALL_EVENTS | pyinotify.IN_DELETE

    # --- Initialization ---
    wm = pyinotify.WatchManager()
    handler = ModHandler()
    notifier = pyinotify.Notifier(wm, handler)

    # Add a new watch on the directory for ALL_EVENTS.
    wm.add_watch(directory, mask, rec=True)

    # Add a new watch on the directory for a file being MODIFIED
    #wm.add_watch(directory, pyinotify.IN_MODIFY)

    # Add a new watch on the directory for a file that is CREATED
    #wm.add_watch(directory, pyinotify.IN_CREATE)

    # Add a new watch on the directory for a file that is DELETED
    #wm.add_watch(directory, pyinotify.IN_DELETE)

    # Add a new watch on the directory for a file that is RENAMED??????
    #wm.add_watch(directory, pyinotify.IN_ATTRIB)

    # Add a new watch on the directory for all of the above in a SUBDIRECTORY???

    # Loop forever and handle events.
    notifier.loop()

if __name__ == '__main__':
    main()
