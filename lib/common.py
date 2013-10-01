'''
I understand that it is generally bad practice to set/change stuff at import, but i REALLY hate having to do it.
thus i have set code to run and set from import, and (hopefully) will not break everything.

**************************************************************************
set_dir code doc:::
    NOTE: no longer is it needed to change directory, instead use lib.common.curdir directly
    change the active directory for our use in the project
    tries three different ways of finding the data files
        1:::see if the current directory has a directory {data}
        2:::check if directory up one has {data}
        3:::if none of these worked, find the location of this file and use its parent directory.'''
import os
import logging
import logging.handlers
from lib.decorators import disabled,enabled
import lib


datadir = 'lib'


@enabled
def p_rents(lo):
    '''
    a function to log where a function got called from
    should never be called in production code _EVER_
    so: decorator to set if we disable this...
    '''
    import inspect ##because this fuinction should only be called during debug, i dont mind about the 'lag' here
    buf=[]
    for i in reversed(inspect.stack()[1:-1]):
        tmp=[]
        ##first, the path of the script
        if i[1].startswith(curdir):
            filename = i[1][len(curdir)+1:]
        else:
            filename=i[1]
        ##add line number
        lineno = str(i[2])
        ##add class ??? (also, check if it IS a class that we need info from)
        if 'self' in i[0].f_locals:
            cls = str(type(i[0].f_locals['self']))[8:-2]
            cls = str(cls.split('.')[1:])[2:-2]
        else:
            cls = ''
            
        ##add function of class/file
        func = i[3]
        
        buf.append("%s:%s:%s:%s()"%(filename,lineno,cls,func))
        
    path=" >> ".join(buf)
    ##finaly, use logging instance to log this thing for us, saving it to file, printing to terminal and whatnot
    lo.debug('call stack: %s'%path)
    
_debug = 0
def debug(value=None):
    '''function to set or return current debug level
    debug levels:
        0: normal, log info and higher to terminal, rest to roving-robots.log
        1: basic, log debug to console
        2: lots, log many annoying things to consol
        3: lagger, log enough that you notice the lag!'''
    global _debug
    if value is None:
        return _debug
    _debug = value
    if value>1:
        root = logging.getLogger('')
        root.handlers[1].setLevel(logging.DEBUG)
        
    else:
        root = logging.getLogger('')
        root.handlers[1].setLevel(logging.info)
        
        
        
print(("current path    ::",  os.getcwd()))
#check if current directory has a folder with the same name as the datadir variable...
if os.path.exists(os.path.normpath(os.path.realpath(os.path.join(os.getcwd(),datadir)))):
    print("current path works")
    curdir = os.getcwd()
#check one dir up from current...
elif os.path.exists(os.path.normpath(os.path.realpath(os.path.join(os.getcwd(),'..',datadir)))):
    curdir = os.path.normpath(os.path.realpath(os.path.join(os.getcwd(),'..')))
    print(("changing tmp_path to::" , curdir))
#we have a problem... try loading from where this file is (hopefully...)
else:
    print("could not find data folder manually, trying dynamically...")
    curdir = os.path.dirname(os.path.abspath(__file__))
    if os.path.exists(os.path.normpath(os.path.realpath(os.path.join(curdir,'..',datadir)))):
        curdir = os.path.normpath(os.path.realpath(os.path.join(curdir,'..')))
    else:
        print("ERROR!! could not find main directory!")
        raise SystemExit
    print(('changing tmp_path to::' , curdir))

#import here because this is after curdir is set
import lib.cfg
def init(LOGFILENAME=None):
    if LOGFILENAME==None:
        log_name=os.path.join(curdir,lib.cfg.main['log_settings']['filename'])
    # set up logging to file - see previous section for more details
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                        datefmt='%m-%d %H:%M:%S',
                        filename=log_name,
                        filemode='w')
    # define a Handler which writes INFO messages or higher to the sys.stderr
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    # set a format which is simpler for console use
    formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
    # tell the handler to use this format
    console.setFormatter(formatter)
    # add the handler to the root logger
    logging.getLogger('').addHandler(console)
    
    #make a socket handler, use same as file format
    streamer = logging.handlers.SocketHandler(lib.cfg.main['log_settings']['stream_host'], lib.cfg.main['log_settings'].getint('stream_port'))
    streamer.setLevel(logging.DEBUG)
    streamer.setFormatter(logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s'))
    logging.getLogger('').addHandler(streamer)
    
    lib.logger = logging.getLogger('lib')
    lib.logger.info('logger set. logging to file:"%s"'%(log_name))
    lib.logger.debug('current path: %s'%os.getcwd())
    lib.logger.debug('currect tmp_path: %s'%curdir)
