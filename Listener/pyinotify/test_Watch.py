__author__ = 'Devon'
import sys
import os.path
import pyinotify
sys.path.insert(0, '../../Server/ftpserver/')
from client import OneDirFptClient


class ModHandler(pyinotify.ProcessEvent):
    print "IN HERE"
    #o = OneDirFptClient("172.27.108.250", "admin", "admin", "root_dir") #at school
    global o
    o = OneDirFptClient("127.27.99.34", "admin", "admin", "root_dir")

    def __init__(self):
        print "SUP"
        self.directory=False
        self.movedTo=False
        self.movedFrom=False
        self.create=False
        self.filename = ""
        self.filenameTo = ""

    # --- If a file or directory is CREATED or MODIFIED---
    def process_IN_CREATE(self, event):
        print 'Created: '
        self.directory = event.dir
        self.create = True
        self.filename = event.pathname
        self.post_processing()
        print "event path: ", event.path

    # --- If a file or directory is DELETED or RENAMED or MODIFIED---
    def process_IN_MOVED_FROM(self, event):
        print 'Moved From'
        self.directory = event.dir
        self.movedFrom=True
        self.filename = os.path.join(event.path, event.name)
        self.post_processing()
        #print "event path: ", event.path


    def process_IN_DELETE(self, event):
        print 'Deleted'
        self.directory = event.dir
        self.movedFrom=True
        self.post_processing()
        #print "event path:", event.path

    def process_IN_MOVED_TO(self, event):
        print 'Move To'
        self.directory = event.dir
        self.movedTo=True
        self.post_processing()
        self.filenameTo = os.path.join(event.path, event.name)
        print "filenameTo:", self.filenameTo

    def post_processing(self):
        movedFrom=self.movedFrom
        movedTo=self.movedTo
        create=self.create
        directory=self.directory
        filename=self.filename
        filenameTo=self.filenameTo
        print "Moved From: " + str(movedFrom)
        print "Moved To: " + str(movedTo)
        print "Create: " + str(create)
        print "filename: " + filename
        print "filename destination: " + filenameTo

        # Delete
        #global o
        if (movedFrom and not movedTo and not create):
            if directory:
                #global o
                #o.delete_folder(filename)
                print "Directory Deleted!"
            else:
                #o.delete_file(filename)
                print "File Deleted!"

        # Rename
        elif (movedTo and movedFrom and not create):
            if directory:
                #o.move(filename,filenameTo)
                print "renamed from:", filename, "renamed to:", filenameTo
                print "Directory Renamed!"
            else:
                o.move(filename, filenameTo)
                print "renamed from:", filename, "renamed to:", filenameTo
                print "File Renamed!"

        # Modified
        elif (create and movedTo and movedFrom):
            if directory:
                print "here"
                print "Directory Modified!"
            else:
                print "File Modified!"

        # New File
        elif (create and not movedTo and not movedFrom):
            if directory:
                #o.mkdir(filename)
                print "mkdir param: ", filename
                print "Directory Create!"
            else:
                #o.upload(filename)
                print "upload param:", filename
                print "File Created!"
        else:
            print "Rename or Modification!"
            print "renamed from", filename, "to", filenameTo
        print "-------------------------------"

        # ----- Reset -----
        self.directory=False
        self.movedTo=False
        self.movedFrom=False
        self.create=False

def main():
    # --- Values ---
    #directory="/home/ubuntu/Documents/School/Spring_2014/Software_Development/THE_PROJECT"
    directory = "/home/rupali/Documents/CS3240/OneDir"
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
