#import coms
import threading
import time
import random

import lib
import lib.cfg
import lib.common
lib.common.init()
import abs

import games

gametype=[{'running':False},None,None]
def main():
    '''
    1:start servers
    2:connect suits
    3:connect tiles
    4:connect arena
    
    5:choose gametype
    6:pass events to gametype code
        gametype code overrides code from normal play via the lazerserver calling (in order) gametype code, then default code (default normally only does heartbeats)
        gametype code inherits from abstract code from the abs.* overriding with its own functions
    '''
    
    
    abs.init()#start abstraction code, starts network server
    #suits and others should connect automatically. (maybe send UPD broadcast packet?)
    ##TODO::: send broadcast packet saying server is up and running (if no error on ans.init())
    
    #choose games, start with default games (later make them replaceable)
    gametype[1] = games.default()
    gametype[2] = games.default()
    gametype[0]['running']=True
    while True:
        time.sleep(1)#nothing to do in main code yet, all is in background threads
    

if __name__ == '__main__':
    lib.common.debug(5)
    main()
