__author__ = 'Devon'
import sys
import os
import pyinotify
<<<<<<< HEAD
sys.path.insert(0, '../../Server/ftpserver/')
from client import OneDirFtpClient
=======
#sys.path.insert(0, '../../Server/ftpserver/')
#os and shutil for updating files and whatnot - for test cases
from client import OneDirFtpClient

>>>>>>> 7c8da97b9fdd1c69c7f5000936c89e88bd506685
import datetime
import logging
import socket
from apscheduler.scheduler import Scheduler
import socket

o = OneDirFtpClient(socket.gethostbyname(socket.gethostname()), "admin", "admin", os.getcwd())

class ModHandler(pyinotify.ProcessEvent):
<<<<<<< HEAD
    global o

    def create(self, theFile):
        if self.isDir:
            o.mkdir(theFile)
        else:
	    o.upload(theFile)
        print "Created: %s " % theFile

    def delete(self, theFile):
        if self.isDir:
            o.delete_folder(theFile)
        else:
            o.delete_file(theFile)
        print "Deleted: %s " % theFile

    def renameModification(self, fromFile, toFile):
	self.create(toFile)
	self.delete(fromFile)
=======
    #global o

    #o = OneDirFptClient("172.27.108.250", "admin", "admin", "root_dir") #at school
>>>>>>> 7c8da97b9fdd1c69c7f5000936c89e88bd506685

    def __init__(self):

        #self.o = OneDirFtpClient("127.27.43.39", "admin", "admin", "/home/rupali/Documents/CS3240/OneDir/extra/WatchTesting")
        #self.o = OneDirFtpClient("172.27.43.171", "admin", "admin", "/home/rupali/Documents/CS3240/OneDir/extra/WatchTesting")
        self.o = OneDirFtpClient(socket.gethostbyname(socket.gethostname()), "admin", "admin", "/home/rupali/Documents/CS3240/OneDir/extra/WatchTesting")
        self.initialTS = datetime.datetime(2005, 7, 14, 12, 30)
        self.currentTS = datetime.datetime.now()

        self.schedule = Scheduler()
        logging.basicConfig()
        self.schedule.start()

        self.stack = []
        self.previousFull= ""
        self.happened=False

        self.isDir=False
        self.file=""
        self.path=""
        self.full=""

    def process(self):
        self.post_processing()

    def process_IN_CREATE(self, event):
        self.currentTS = datetime.datetime.now()
        self.file = event.name
<<<<<<< HEAD
	self.path = event.path
	self.full = event.pathname
	self.isDir = event.dir

	difference = self.currentTS-self.initialTS
	if (difference.total_seconds() < 1 and self.full is self.previousFull):
		self.stack.append("Create")
	else:
		executionTime = self.currentTS+datetime.timedelta(seconds=.25)
		job = self.schedule.add_date_job(lambda: self.process(), date=executionTime)
		self.previousFull = event.pathname
		self.initialTS=datetime.datetime.now()
		del self.stack[:]
		self.stack.append("Create")

    def process_IN_MOVED_FROM(self, event):
	self.previous=event.pathname
	self.currentTS = datetime.datetime.now()
        self.file = event.name
	self.path = event.path
	self.full = event.pathname
	self.isDir = event.dir

	difference = self.currentTS-self.initialTS
	if (difference.total_seconds() < 1 and self.stack[0] is "Create"):
		self.stack.append("Moved_From")
	else:
		executionTime = self.currentTS+datetime.timedelta(seconds=.25)
		job = self.schedule.add_date_job(lambda: self.process(), date=executionTime)
		self.previousFull = event.pathname
		self.initialTS=datetime.datetime.now()
		del self.stack[:]
		self.stack.append("Moved_From")
=======
        self.path = event.path
        self.full = event.pathname
        self.isDir = event.dir

        difference = self.currentTS-self.initialTS
        if (difference.total_seconds() < 1 and self.full is self.previousFull):
            self.stack.append("Create")
        else:
            executionTime = self.currentTS+datetime.timedelta(seconds=1.5)
            job = self.schedule.add_date_job(lambda: self.process(), date=executionTime)
            self.previousFull = event.pathname
            self.initialTS=datetime.datetime.now()
            del self.stack[:]
            self.stack.append("Create")

    def process_IN_MOVED_FROM(self, event):
        self.currentTS = datetime.datetime.now()
        self.file = event.name
        self.path = event.path
        self.full = event.pathname
        self.isDir = event.dir

        difference = self.currentTS-self.initialTS
        if (difference.total_seconds() < 1 and self.stack[0] is "Create"):
            self.stack.append("Moved_From")
        else:
            executionTime = self.currentTS+datetime.timedelta(seconds=1.5)
            job = self.schedule.add_date_job(lambda: self.process(), date=executionTime)
            self.previousFull = event.pathname
            self.initialTS=datetime.datetime.now()
            del self.stack[:]
            self.stack.append("Moved_From")
>>>>>>> 7c8da97b9fdd1c69c7f5000936c89e88bd506685

    def process_IN_MOVED_TO(self, event):
        self.currentTS = datetime.datetime.now()
        self.file = event.name
<<<<<<< HEAD
	self.path = event.path
	self.full = event.pathname
	self.isDir = event.dir

	difference = self.currentTS-self.initialTS
	if (difference.total_seconds() < 1 and self.stack[len(self.stack)-1] is "Moved_From"):
		self.stack.append("Moved_To")
	else:
		executionTime = self.currentTS+datetime.timedelta(seconds=.25)
		job = self.schedule.add_date_job(lambda: self.process(), date=executionTime)
		self.previousFull = event.pathname
		self.initialTS=datetime.datetime.now()
		del self.stack[:]
		self.stack.append("Moved_To")

    def post_processing(self):
	global o
=======
        self.path = event.path
        self.full = event.pathname
        self.isDir = event.dir

        difference = self.currentTS-self.initialTS
        if (difference.total_seconds() < 1 and self.stack[len(self.stack)-1] is "Moved_From"):
            self.stack.append("Moved_To")
        else:
            executionTime = self.currentTS+datetime.timedelta(seconds=1.5)
            job = self.schedule.add_date_job(lambda: self.process(), date=executionTime)
            self.previousFull = event.pathname
            self.initialTS=datetime.datetime.now()
            del self.stack[:]
            self.stack.append("Moved_To")

    def post_processing(self):
<<<<<<< HEAD
        if len(self.stack) is 1:
            if self.stack[0] is "Create":
                print "Created: %s " % self.full
                if self.isDir:
                    #print self.full
                    self.o.mkdir(self.full)
                else:
                    self.o.upload(self.full)
            elif self.stack[0] is "Moved_From":
                print "Deleted: %s " % self.full
                if self.isDir:
                    self.o.delete_folder(self.full)
                else:
                    self.o.delete_file(self.full)
            else:
                print "Error"
        elif len(self.stack) is 2:
            if self.stack[0] is "Moved_From" and self.stack[1] is "Moved_To":
                print "Renamed: %s" % self.full
                #print "Original name: %s" % self.previousFull
                self.o.move(self.previousFull,self.full)
=======
>>>>>>> 7c8da97b9fdd1c69c7f5000936c89e88bd506685
    	# --- Creation/Deletion ---
	if len(self.stack) is 1:
		if self.stack[0] is "Create":
			self.create(self.full)
		elif self.stack[0] is "Moved_From":
			self.delete(self.full)
		else:
			print "Error"
	# --- Rename ---
	elif len(self.stack) is 2:
		if self.stack[0] is "Moved_From" and self.stack[1] is "Moved_To":			
			self.renameModification(self.previous, self.full) 
			print "Renamed: %s" % self.full
		else:
			print "Error"
	# --- Modified ---
	elif len(self.stack) is 3:
		if self.stack[0] is "Create" and self.stack[1] is "Moved_From" and self.stack[2] is "Moved_To":	
			self.renameModification(self.previous, self.full) 					
			print "Modified: %s" % self.full
		else:
			print "Error"
	self.happened=True
<<<<<<< HEAD

def main():
    directory="."
=======
	
	'''
        #global o
        if (movedFrom and not movedTo and not create):
            if directory:
                #global o
                #o.delete_folder(filename)
                print "Directory Deleted!"
>>>>>>> dba54fd6129713a24d34aa4ccee3b169c5cfe2b6
            else:
                print "Error"
        elif len(self.stack) is 3:
            if self.stack[0] is "Create" and self.stack[1] is "Moved_From" and self.stack[2] is "Moved_To":
                print "Modified: %s" % self.full
                #delete what's on the server, and then reupload file
                self.o.delete_file(self.full)
                self.o.upload(self.full)
            else:
                print "Error"
        self.happened = True

        '''
            #global o
            if (movedFrom and not movedTo and not create):
                if directory:
                    #global o
                    #o.delete_folder(filename)
                    print "Directory Deleted!"
                else:
            continue
                    #o.delete_file(filename)
        '''


def main():
    directory= "../../extra/WatchTesting"
    #directory = "/OneDir"
    #print directory
>>>>>>> 7c8da97b9fdd1c69c7f5000936c89e88bd506685

    wm = pyinotify.WatchManager()
    mask = pyinotify.IN_CREATE | pyinotify.IN_MOVED_FROM | pyinotify.IN_MOVED_TO
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
