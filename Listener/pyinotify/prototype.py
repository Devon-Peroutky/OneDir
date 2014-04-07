__author__ = 'Devon'
import sys
import os
import pyinotify
sys.path.insert(0, '../../Server/ftpserver/')
from client import OneDirFptClient
import datetime
import logging
from apscheduler.scheduler import Scheduler

class ModHandler(pyinotify.ProcessEvent):
    global o
    global hit

    #o = OneDirFptClient("172.27.108.250", "admin", "admin", "root_dir") #at school
    #o = OneDirFptClient("127.27.99.34", "admin", "admin", "root_dir")

    def __init__(self):

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

    # --- If a file or directory is CREATED or MODIFIED---
    def process_IN_CREATE(self, event):
	self.currentTS = datetime.datetime.now()
        self.file = event.name
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

    def process_IN_MOVED_TO(self, event):
	self.currentTS = datetime.datetime.now()
        self.file = event.name
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
    	# --- Creation/Deletion ---
	if len(self.stack) is 1:
		if self.stack[0] is "Create":
		        print "Created: %s " % self.full
		elif self.stack[0] is "Moved_From":
		        print "Deleted: %s " % self.full
		else:
			print "Error"
	# --- Rename ---
	elif len(self.stack) is 2:
		if self.stack[0] is "Moved_From" and self.stack[1] is "Moved_To":			
			print "Renamed: %s" % self.full
		else:
			print "Error"
	# --- Modified ---
	elif len(self.stack) is 3:
		if self.stack[0] is "Create" and self.stack[1] is "Moved_From" and self.stack[2] is "Moved_To":			
			print "Modified: %s" % self.full
		else:
			print "Error"
	self.happened=True
	
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
    directory="../../extra/WatchTesting"
    #directory = "/OneDir"
    #print directory

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
