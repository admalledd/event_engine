import lib.configobj as cj
import lib.common

import os

#normally, config's are added via the lib.cfg.add() function
#however, here we must have the main cfg open early to set logfilename
#just trust that we can use os.getcwd() for this...
main=cj.ConfigObj(os.path.join(os.getcwd(),'config.ini'))

def add(*path,**KWARGS):
    '''add cfg name to global name space within lib.cfg'''
    if 'name' in KWARGS:
        name=KWARGS['name']
    else:
        raise Error('must have name= in call')
    #is name a string?
    if not isinstance(name,basestring):
        raise Error('name must be str')
    #is name "mostly" valid?
    if '.' in name:
        raise Error('name cant have a "." in it')
    
    ##todo: make more reliable from mistakes
    #if (',','=','-','(',')','%','@','<','>','!','#') in name:
    #    raise Error('invalid name for cfgobj')
        
    #get sub-path
    file_name=os.path.join(*path)
    #join with full path
    file_name=os.path.join(lib.common.curdir,file_name)
    
    #add to modual as a usable name
    globals()[name]=cj.ConfigObj(file_name)
    
    from lib import logger
    logger.debug('%s config opened and loaded'%name)