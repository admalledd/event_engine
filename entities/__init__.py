'''
data def's:::

structure of entities: {ID<int>:[base.Entity(),server.con_handler()]}
'''
#std lib
import logging
logger = logging.getLogger('entities')

#server libs
import lib.cfg

#abs layer
from . import server

entities=None#start out None, till init() is called
def init():
    '''start su_server thread, and watch thing-a-ma-jigs, returns a dict that will be where all entities are stored
    for this netserver
    '''
    global entities
    entities = server.init()
    server.server_thread.start()
    logger.info('net server started on port %s'%lib.cfg.main['net_server'].getint('port'))
    return entities

