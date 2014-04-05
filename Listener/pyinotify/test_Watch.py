__author__ = 'Devon'
import sys
import os
import pyinotify
sys.path.insert(0, '../../Server/ftpserver/')
from client import OneDirFptClient


class ModHandler(pyinotify.ProcessEvent):
    print "IN HERE"
    #o = OneDirFptClient("172.27.108.250", "admin", "admin", "root_dir") #at school
    global o
    #o = OneDirFptClient("127.27.99.34", "admin", "admin", "root_dir")

    def __init__(self):
	self.directory=False
        self.movedTo=False
        self.movedFrom=False
        self.create=False
        self.filename = ""
        self.filenameTo = ""

    # --- If a file or directory is CREATED or MODIFIED---
    def process_IN_CREATE(self, event):
        self.directory = event.dir
        self.create = True
        self.filename = event.pathname
        self.post_processing()
        print "Created: %s " % os.path.join(event.path, event.name)

    # --- If a file or directory is DELETED or RENAMED or MODIFIED---
    def process_IN_MOVED_FROM(self, event):
        self.directory = event.dir
        self.movedFrom=True
        self.filename = os.path.join(event.path, event.name)
        self.post_processing()
        #print "event path: ", event.path


    def process_IN_DELETE(self, event):
        self.directory = event.dir
        self.movedFrom=True
        self.post_processing()
        #print "event path:", event.path

    def process_IN_MOVED_TO(self, event):
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
	'''
        print "Moved From: " + str(movedFrom)
        print "Moved To: " + str(movedTo)
        print "Create: " + str(create)
        print "filename: " + filename
        print "filename destination: " + filenameTo
	'''
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
                #print "mkdir param: ", filename
                print "Directory Create!"
            else:
                #o.upload(filename)
                #print "upload param:", filename
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
    directory="/home/ubuntu/Documents/School/Spring_2014/Software_Development/OneDir/extra/WatchTesting"
    #directory = "/home/rupali/Documents/CS3240/OneDir"
    #print directory

    '''
    maskMoveTo = pyinotify.IN_MOVED_TO
    maskCreate = pyinotify.IN_CREATE
    maskDelete = pyinotify.IN_MOVED_FROM

    # --- Initialization ---
    wm = pyinotify.WatchManager()
    creates = pyinotify.WatchManager()
    deletes = pyinotify.WatchManager()
    modifies = pyinotify.WatchManager()
    notifier = pyinotify.Notifier(wm, ModHandler())

    # Add a new watch on the directory for Renames && Modified.
    # modifies.add_watch(directory, maskMoveTo, rec=True)

    # Add a new watch on the directory for Creates.
    creates.add_watch(directory, maskCreate, rec=True)
    modifies.add_watch(directory, maskMoveTo, rec=True)
    creates.add_watch(directory, maskDelete, rec=True)

    # Add a new watch on the directory for Deletes.
    deletes.add_watch(directory, maskDelete, rec=True)

    # Loop forever and handle events.
    notifier.loop()
    '''
    wm = pyinotify.WatchManager()
    mask = pyinotify.IN_CREATE | pyinotify.IN_MOVED_FROM | pyinotify.IN_DELETE
    
    notifier = pyinotify.Notifier(wm, ModHandler())

    wdd = wm.add_watch(directory, mask, rec=True)

    while True:
	try:
            notifier.process_events()
            if notifier.check_events():
                notifier.read_events()
        except KeyboardInterrupt:
            notifier.stop()
            break


if __name__ == '__main__':
    main()
