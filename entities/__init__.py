'''
data def's:::

structure of entities: {ID<int>:[base.Entity(),server.con_handler()]}
'''
#std lib
import logging
logger = logging.getLogger('entities')

#server libs
import lib.cfg


entities={}#start out None, till init() is called

def get_entity(ID):
    '''get the object instance for this net instance, we dont store the ref because we want to be weak in case of problems
    if ID is not in dict, this is clearly an error condition and stale data got passed around...
    '''
    return entities[ID][0]

def get_netobj(ID):
    '''here it is possible to not have a netobj, but it will be None so long as the ID is valid. 
    just like get_entity(), scream if ID is invalid...'''    
    return entities[ID][1]

def close_netobj(ID):
    netobj = entities[ID][1]
    entities[ID][1]=None
    netobj.close()
def set_netobj(netobj):
    entities[netobj.OID][1]=netobj

def init():
    '''start su_server thread, and watch thing-a-ma-jigs, returns a dict that will be where all entities are stored
    for this netserver
    '''
    from . import server #import moved due to circular reference
    server.init()
    server.server_thread.start()
    logger.info('net server started on port %s'%lib.cfg.main['net_server'].getint('port'))
    return entities

