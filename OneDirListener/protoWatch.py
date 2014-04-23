__author__ = 'Devon'
import sys
import os
import pyinotify
# sys.path.insert(0, '../../Server/ftpserver/')
from client import OneDirFtpClient
import datetime
import logging
import socket
from apscheduler.scheduler import Scheduler
from ftplib import error_perm

class EventHandler(pyinotify.ProcessEvent):
    def create(self, theFile):
        try:
           if self.isDir:
                ListenerContainer.add_watch(theFile)
                ListenerContainer.client.mkdir(theFile)
           else:
                ListenerContainer.client.upload(theFile)
        except:
            print "----------- Problem adding the watcher and/or creating the file -----------"

    def delete(self, theFile):
        try:
            if self.isDir:
                ListenerContainer.rm_watch(theFile)
                ListenerContainer.client.delete_folder(theFile)
            else:
                ListenerContainer.client.delete_file(theFile)
        except:
            print "----------- Problem removing watcher and/or deleting the file -----------"

    def renameModification(self, fromFile, toFile):
	self.delete(fromFile)
	self.create(toFile)

    def __init__(self):
        # Initialize Time
	self.initialTS = datetime.datetime(2005, 7, 14, 12, 30)
	self.currentTS = datetime.datetime.now()

        # Initialize Scheduler
	self.schedule = Scheduler()
	logging.basicConfig()
	self.schedule.start()

        # Initialize History 
	self.stack = []
	self.happened=False		# IMPLEMENT THIS SO THAT IF EVENT HAPPENED WE CANCEL THE SCHEDULE EVENT


    def setup(self, event):
	self.currentTS = datetime.datetime.now()
        self.file = event.name
	self.path = event.path
	self.full = event.pathname
	self.isDir = event.dir

    def process_IN_CREATE(self, event):
        self.setup(event)

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
        self.setup(event)
        self.previous=event.pathname

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

    def process_IN_MOVED_TO(self, event):
        self.setup(event)

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

    def process(self):
	global o
    	# --- Creation/Deletion ---
	if len(self.stack) is 1:
		if self.stack[0] is "Create":
			self.create(self.full)
			print "Created: %s" % self.full
		elif self.stack[0] is "Moved_From":
			self.delete(self.full)
			print "Deleted: %s" % self.full
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

def main(ip, port, username, nickname, password, root_dir):
    directory="."

    ListenerContainer.root_dir = root_dir
    ListenerContainer.client = OneDirFtpClient(ip, port, username, nickname, password, ListenerContainer.root_dir)
    notifier = pyinotify.Notifier(ListenerContainer.watch_manager, EventHandler())
    ListenerContainer.add_watch(directory)

    while True:
	try:
            notifier.process_events()
            if notifier.check_events():
                notifier.read_events()
        except:
            notifier.stop()
            break

if __name__ == '__main__':
    print 'DONT FOR GET TO SET THE IP!'
    main('127.0.0.1', '21', 'admin', 'TheBigCheese','admin', os.getcwd())
