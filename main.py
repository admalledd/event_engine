#import coms
import logging

import lib
import lib.cfg
import lib.common
lib.common.init()
#set debug here so that all later imports can use import-time redefines
lib.common.debug(5)
import entities

import games

import events
print(events.net_events.connect_event.__name__)
import pdb;pdb.set_trace()
raise SytemExit()
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
    
    ent_dict = entities.init()#starts network server and get in return a dict of any entities we will ever have
    #suits and others should connect automatically. (maybe send UPD broadcast packet?)
    ##TODO::: send broadcast packet saying server is up and running (if no error on entities.init())
    
    while True:
        event = events.base.get()
        logging.info(event)
    

if __name__ == '__main__':
    main()
