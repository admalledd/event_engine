#import coms
import threading
import time
import random

import lib
import lib.cfg
import lib.common
lib.common.init()
import abs.suit

import games

gametype=None#gametype is started for each game, server runs one game at a time right now
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
    abs.suit.init()
    while True:
        time.sleep(1)
    
def test():
    pass
if __name__ == '__main__':
    lib.common.debug(5)
    main()
