import logging
logger = logging.getLogger('abs.tile')
from lib import thread2 as threading
import time
import json


import lib.common#for debug


##import loop to mainfile!! (way around this concept? move game loop to new file?)
import __main__#for __main__.gametype which is a gametype object
tiles={}#format: {TID:[tileobj,netobj]}

class tile(object):
    '''
    self.tid == tile identification descriptor, each tile is unique.
    self.tid == netobj.OID
    
    
    tile code in the abstraction layer deals with translating the json (or dictionary) input to the relevant functions
    in the game code tile object, also handles any connctivity/status information. 
    
    holds all stats for the current tile. no information is stored elsewhere in code about this tile except maybe in the debug area
    also this is where any stats at the end of game (or during as well) is saved to the data base for later computation (signal sent from game
    code at game end for new stats computation by the stats server)
    '''
    def __init__(self,sid):
        self.TID=tid
        self.translation_codes={\
        'ghit':self.got_hit,                #got hit with a shot (tend to use it for dropping "mines")
        'gstp':self.got_stepped             #got stepped upon, see if anything fun needs to be done
        'stup':self.status_update,          #status update, normaly a health update from a preveious got_hit()
        'ping':self.ping,                   #just a simple ping to keep the lines open, data is reported back, and logger.debug()'d
        'pong':self.pong,                   #simmilar to above, but no reply needed, only log data
        'dcon':self.close_connection
        }
        self.status={#json-able data structure with all relavent tile data and game data
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
        if short_func in self.translation_codes:
            self.translation_codes[short_func](data)
        else:
            #not in tranlation codes, try game specific codes
            ran=False
            if __main__.gametype is not None:
                ran = __main__.gametype.tile.run_packet(self,short_func,data)
            
            if not ran:#game code did not have the required packet data! oh teh noes!
                logger.error('packet unable to be run ! %s'%((self.TID,short_func,data)))
    def ping(self,data):
        '''tile ping'd the server, return pong and any data exactly as it was sent'''
        if 'pingdata' in data:
            logger.info('tile %s pinged with data: %s'%(self.TID,data))
        
        return_data=json.dumps(data)
        tiles[self.TID][1].outgoingq.put(('pong',return_data))
    
    def pong(self, data):
        '''server ping'd the tile, this is the return pong 
        TODO: add server ping send, as well as travel time it takes to execute the command'''
        if 'pingdata' in data:
            logger.info('tile %s pinged with data: %s'%(self.TID,data))
    
    def status_update(self,data):
        self.status.update(data)
        
    def got_hit(self,data):
        #in the future, load weapon from weapons in the arena
        print data
        logger.info('tile %s got hit with weapon "%s"'%(self.TID,data['weapon']))
        if __main__.gametype is not None:#in reality, we should never have to check for None, as well as we need to know which game to play!
            __main__.gametype.tile.gothit(self,data)
    def close_connection(self,data):
        logger.info('tile %s requesting closing network, "%s"'%(self.TID,data))
        tiles[self.TID][1].close()