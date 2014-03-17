__author__ = 'Rupali'

import sys
import time
import logging
from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler
from watchdog.events import FileSystemEventHandler
#from watchdog.events import DirSystemEventHandler

class MyHandler(FileSystemEventHandler):
    def on_any_event(self, event):
        print "Location:", event.src_path
        print "Type:", event.event_type
    def on_modified(self, event):
        print "I can do things here that only happen when a file system is modified."
        print "Keep in mind that the file is being modified twice (see LoggingEventHandler output)"
    def on_created(self, event):
        print "I can do things here that only happen when a file is created."
        print "Keep in mind that this happens when the file is modified as well."
    def on_deleted(self, event):
        print "I can do things here that only happen when a file is deleted."
        print "Keep in mind that this happens when the file is modified as well."
        #does not seem to occur when a file/folder is deleted, and I'm not sure why.
    def on_moved(self,event):
        print "I can do things here that only happen when a file is moved."
        print "This happens when the file is modified."
        print "This happens when a file/folder is renamed."
        print "Source path:", event.src_path
        print "Destination path:", event.dest_path

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    path = sys.argv[1] if len(sys.argv) > 1 else '.' #can enter a specific file path as a command line argument, or not & the program will process the current directory.
    #example command line argument: "python test_Watchdog.py /home/rupali/Documents/CS3240/OneDir/Listener"
    #This also picks up changes in itself if it is in the directory (or a subdirectory) of the specified directory
    event_handler = LoggingEventHandler()
    event_handler2 = MyHandler()

    observer = Observer()
    #observer.schedule(event_handler, path, recursive=True) #recursive makes it look for changes in subdirectories
        #prints a log that looks like this to the terminal:
        #2014-03-17 00:02:56 - Created file: /home/rupali/Documents/CS3240/OneDir/Listener/WatchDog/test.txt___jb_bak___
        #2014-03-17 00:02:56 - Modified file: /home/rupali/Documents/CS3240/OneDir/Listener/WatchDog/test.txt___jb_bak___
        #2014-03-17 00:02:56 - Moved file: from /home/rupali/Documents/CS3240/OneDir/Listener/WatchDog/test.txt to /home/rupali/Documents/CS3240/OneDir/Listener/WatchDog/test.txt___jb_old___
        #2014-03-17 00:02:56 - Moved file: from /home/rupali/Documents/CS3240/OneDir/Listener/WatchDog/test.txt___jb_bak___ to /home/rupali/Documents/CS3240/OneDir/Listener/WatchDog/test.txt
        #2014-03-17 00:02:56 - Modified file: /home/rupali/Documents/CS3240/OneDir/Listener/WatchDog/test.txt
        #2014-03-17 00:02:56 - Deleted file: /home/rupali/Documents/CS3240/OneDir/Listener/WatchDog/test.txt___jb_old___
    observer.schedule(event_handler2, path, recursive=True)

    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()