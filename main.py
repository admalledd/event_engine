#import coms
import threading
import time
import random

import lib
import lib.cfg
import lib.common
lib.common.init()
import abs.suit

l={'l':[]}
def main():
    #lib.cfg.add('config.ini',name='main')
    abs.suit.init()
    time.sleep(600)
    
def test():
    pass
if __name__ == '__main__':
    lib.common.debug(5)
    main()
