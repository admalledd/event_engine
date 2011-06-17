import os, time
 
def createDaemon():
    """ 
        This function create a service/Daemon that will execute a det. task
    """
 
    try:
        # Store the Fork PID
        pid = os.fork()
 
        if pid > 0:
        print 'PID: %d' % pid 
        os._exit(0)
 
    except OSError, error:
        print 'Unable to fork. Error: %d (%s)' % (error.errno, error.strerror)
        os._exit(1)
 
    doTask()
 
def doTask():
    """ 
      This function create a task that will be a daemon
    """
  
    for i in range(10):
        print time.ctime()
        #file.flush()
        time.sleep(0.25)
 
 
if __name__ == '__main__':
 
    # Create the Daemon
    createDaemon()
