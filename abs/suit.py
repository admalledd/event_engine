import logging
logger = logging.getLogger('abs.suit.suit')
from lib import thread2 as threading
import time
import json


import lib.common
import lib.cfg


##import loop to mainfile!! (way around this concept? move game loop to new file?)
import __main__#for __main__.gametype which is a gametype object
suits={}#format: {SID:[suitobj,netobj]}

class suit(object):
    '''
    self.sid == suit identification descriptor, each suit is unique.
    self.sid == netobj.OID
    
    
    suit code in the abstraction layer deals with translating the json (or dictionary) input to the relevant functions
    in the game code suit object. 
    '''
    def __init__(self,sid):
        self.SID=sid
        self.translation_codes={\
        'ghit':self.got_hit,                #got hit from another suit
        'stup':self.status_update,          #status update, normaly a position update, or a health update from a preveious got_hit()
        'ping':self.ping,                   #just a simple ping to keep the lines open, data is reported back, and logger.debug()'d
        'pong':self.pong,                   #simmilar to above, but no reply needed, only log data
        'dcon':self.close_connection
        }
        self.status={#json-able data structure with all relavent suit data
        'health':100,
        'ammos':[100],
        'weapon':0,#weapon is the index for weapons and ammo
        'weapons':['basic'],
        'location':[0,0],
        'team':'red',
        'player_name':'john_doe'
        }
    def run_packet(self,short_func,data):
        '''it is up to this function to decide what function gets called for what
        (got_hit(self.sid,self,other), player_move(self.sid,self,old_loc,new_loc) ect....
        '''
        
        if lib.common.debug() >4:
            #high debug
            logger.debug((short_func,data))
        
        self.translation_codes[short_func](data)
    def ping(self,data):
        if 'pingdata' in data:
            logger.info('suit %s pinged with data: %s'%(self.SID,data))
            print suits
        return_data=json.dumps(data)
        print return_data
        suits[self.SID][1].outgoingq.put(('pong',return_data))
    
    def pong(self, data):
        if 'pingdata' in data:
            logger.info('suit %s pinged with data: %s'%(self.SID,data))
    
    def status_update(self,data):
        self.status.update(data)
        
    def got_hit(self,data):
        #in the future, load weapon from weapons in the arena
        print data
        logger.info('suit %s got hit with weapon "%s"'%(self.SID,data['weapon']))
        if __main__.gametype is not None:
            __main__.gametype.suit.gothit(self,data)
    def close_connection(self,data):
        logger.info('suit %s requesting closing network, "%s"'%(self.SID,data))
        suits[self.SID][1].close()