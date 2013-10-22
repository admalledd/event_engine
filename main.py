import logging
logger=logging.getLogger('main')
import traceback
import sys

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
    #load plugins first, they may add new events.
    lib.pluginloader.load_plugins()
    entities.init()#starts network server
    logger.info("event tree:%s"%events.base.events)
    logger.info("listener tree:%s"%events.base.listeners)
    while True:
        try:

            event = events.base.get()
            events.handle_event(event)
        except KeyboardInterrupt:
            logger.info("server quit requested!")
            lib.pluginloader.unload_plugins()
            return
        except Exception as e:
            logger.critical("error handling event %s:\n%s"%(event.name,traceback.format_exc()))
    

if __name__ == '__main__':
    main()
