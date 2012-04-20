
import os
import collections
import threading
import time

class logreader(object):
    def __init__(self):
        self.text=collections.deque([],25)
        self.txt_lock=threading.Lock()
        
        
    def get_text(self):
        with self.txt_lock:
            return tuple(self.text)
    def open(self):
        
        self.r_thread = threading.Thread(target=self.reader)
        self.r_thread.setDaemon(True)
        self.__running=True
        self.r_thread.start()
        
    def close(self):
        self.__running=False
        self.text=collections.deque([],25)
    def reader(self):
    
        def follow(thefile):
            #thefile.seek(0,2)      # Go to the end of the file
            while self.__running:
                line = thefile.readline()
                if not line:
                    time.sleep(0.1)    # Sleep briefly
                    continue
                yield line
            print "ending logreader"

        logfile = open(os.path.join(os.getcwd(),'..','lazertag.log'))
        loglines = follow(logfile)
        for line in loglines:
            with self.txt_lock:
                self.text.append(line)