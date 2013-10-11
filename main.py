import logging
logger=logging.getLogger('main')

import lib.cfg
import lib.common
lib.common.init()
#set debug here so that all later imports can use import-time redefines
lib.common.debug(5)
import lib.pluginloader


import entities

import events

#import ipdb;ipdb.set_trace()

def main():
    '''
    1:start servers
    2:connect suits
    3:connect tiles
    4:connect arena
    
    5:choose gametype
    6:pass events to gametype code
        gametype code overrides code from normal play via the lazerserver calling (in order) gametype code, then default code (default normally only does heartbeats)
        gametype code inherits from abstract code from the entities.* overriding with its own functions
    '''
    events.init()
    entities.init()#starts network server
    #suits and others should connect automatically. (maybe send UPD broadcast packet?)
    ##TODO::: send broadcast packet saying server is up and running (if no error on entities.init())
    
    lib.pluginloader.load_plugins()

    logger.info(events.base.listeners)

    while True:
        event = events.base.get()

        logger.info(event)
    

if __name__ == '__main__':
    main()
