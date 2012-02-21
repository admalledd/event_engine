#absbase class file

import logging
logger = logging.getLogger('abs.absbase')
from lib import thread2 as threading
import time
import json


import lib.common#for debug

import abs
##import loop to mainfile!! (way around this concept? move game loop to new file?)
import __main__#for __main__.gametype which is a gametype object


class absbase(object):
    '''
    self.ID == object identification descriptor, each is unique.
    self.ID == netobj.OID
    
    
    object code in the abstraction layer deals with translating the json (or dictionary) input to the relevant functions
    in the game code object object, also handles any connctivity/status information. 
    
    holds all stats for the current object. no information is stored elsewhere in code about this object except maybe in the debug area
    also this is where any stats at the end of game (or during as well) is saved to the data base for later computation (signal sent from game
    code at game end for new stats computation by the stats server)
    '''
    def __init__(self,id):
        self.ID=id
        #basic translation codes for things that are not item specific
        self.translation_codes={\
        'ghit':self.got_hit,                #got hit with a shot (tend to use it for dropping "mines")
        'stup':self.status_update,          #status update, normaly a health update from a preveious got_hit()
        'ping':self.ping,                   #just a simple ping to keep the lines open, data is reported back, and logger.debug()'d
        'pong':self.pong,                   #simmilar to above, but no reply needed, only log data
        'dcon':self.close_connection        
        }
        self.status={#json-able data structure with all relavent object data and game data, empty here in this code
        'arena':0#int of what arena this object is in (should be updated from the client on connect, must not be zero for long :D)
        }
    def run_packet(self,obtype,short_func,data):
        '''it is up to this function to decide what function gets called for what
        (got_hit(self.id,self,other), player_move(self.id,self,old_loc,new_loc) ect....
        '''
        
        if lib.common.debug() >4:
            #high debug
            logger.debug((short_func,data))
        if short_func in self.translation_codes:
            self.translation_codes[short_func](data)
        else:
            #not in tranlation codes, try game specific codes
            ran=False
            if __main__.gametype[0]['running']:
                ran = getattr(__main__.gametype[self.status['arena'], obtype).run_packet(self,short_finc,data)
                
            if not ran:#game code did not have the required packet data! oh teh noes!
                logger.error('packet unable to be run ! %s'%((self.ID,short_func,data)))
    def ping(self,data):
        '''object ping'd the server, return pong and any data exactly as it was sent'''
        if 'pingdata' in data:
            logger.info('object %s pinged with data: %s'%(self.ID,data))
        
        return_data=json.dumps(data)
        abs.objects[self.ID][1].outgoingq.put(('pong',return_data))
    
    def pong(self, data):
        '''server ping'd the object, this is the return pong 
        TODO: add server ping send, as well as travel time it takes to execute the command'''
        if 'pingdata' in data:
            logger.info('object %s pinged with data: %s'%(self.ID,data))
    
    def status_update(self,data):
        self.status.update(data)
        
    def got_hit(self,data):
        #in the future, load weapon from weapons in the arena
        ##TODO: remove debugish lines when we have more stuff, and place it in the debug inspector area. as well as moving all code to gamecode
        print data
        logger.info('object %s got hit with weapon "%s"'%(self.ID,data['weapon']))
        
    def close_connection(self,data):
        logger.info('object %s requesting closing network, "%s"'%(self.ID,data))
        abs.objects[self.ID][1].close()