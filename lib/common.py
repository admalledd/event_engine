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
import textwrap

import pygame

import lib.decorators

def p_rents(lo):
    '''
    a function to log where a function got called from
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
    ##finaly, use logging instance to log thins thing for us, saving it to file, printing to terminal and whatnot
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
        
        
        
datadir = 'data'
print "current path    ::",  os.getcwd()
#check if current directory has a folder with the same name as the datadir variable...
if os.path.exists(os.path.normpath(os.path.realpath(os.path.join(os.getcwd(),datadir)))):
    print 'current path works'
    curdir = os.getcwd()
#check one dir up from current...
elif os.path.exists(os.path.normpath(os.path.realpath(os.path.join(os.getcwd(),'..',datadir)))):
    curdir = os.path.normpath(os.path.realpath(os.path.join(os.getcwd(),'..')))
    print "changing tmp_path to::" , curdir
    #os.chdir(curdir)
#we have a problem... try loading from where this file is (hopefully...)
else:
    print 'could not find data folder manually, trying dynamically...'   
    #got rid of the inspect method of finding the file, seems that __file__ will work just as well.
    curdir = os.path.dirname(os.path.abspath(__file__))
    if os.path.exists(os.path.normpath(os.path.realpath(os.path.join(curdir,'..',datadir)))):
        curdir = os.path.normpath(os.path.realpath(os.path.join(curdir,'..')))
    else:
        print 'ERROR!! could not find main directory!'
        raise SystemExit
    print 'changing tmp_path to::' , curdir




log_name=os.path.join(curdir,'roving-robots.log')
# set up logging to file - see previous section for more details
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M',
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
logger = logging.getLogger('lib.common')
logger.info('logger set. logging to file:"%s"'%(log_name))
logger.debug('current path: %s'%os.getcwd())
logger.debug('currect tmp_path: %s'%curdir)

@lib.decorators.memoized
def load_img(*name):
    """ Load image and return image object"""
    name = os.path.join(*name)
    fullname = os.path.join(curdir,'data','img',name)
    try:
        image = pygame.image.load(fullname)
        #convert the img to have transparencies...
        if image.get_alpha is None:
            image = image.convert()
        else:
            image = image.convert_alpha()
    except pygame.error, message:
        #print 'Cannot load image:', fullname
        logger.critical('Cannot load image: %s'%fullname)
        raise SystemExit, message
    return image
    
def txt_box_render(raw_text,mian_rect,color=(0,0,0),ffont=None):
    '''takes in a string and splits it according to the main_rect's width,
    then renders it and returns a list of pygame.surfaces and rects'''
    if ffont==None:
        ffont=font##use lib.common.font
    txt=[]
    
    ##debug line, use if things are really broken...
    #print mian_rect.height/float(ffont.size(raw_text)[1])
    for index,text in enumerate(raw_text.split('\n')):
        #kazunthieght...
        for num,line in enumerate(textwrap.wrap(text,int(float(mian_rect.width)/(float(ffont.size(text)[0])/float(len(text)))))):
            ##render a line of text
            temp_var=ffont.render(line,True,color).convert_alpha()
            rect=temp_var.get_rect()
            topleft=mian_rect.topleft
            rect.topleft=(topleft[0],topleft[1]+(rect.height*num)+(rect.height*index))
            
            ##add to our list the current txt line...
            txt.append((temp_var,rect))
    ##return a list of img's to blit and thier rects...
    return txt
    
pygame.font.init()

font = pygame.font.Font(os.path.join(curdir,'data','fonts','freesansbold.ttf'), 12)
