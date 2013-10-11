#absbase class file

import logging
logger = logging.getLogger('entities.base')
import time
import json


import lib.common#for debug

import entities
import events



class Entity(object):
    '''
    self.ID == object identification descriptor, each is unique.
    self.ID == netobj.OID
    
    
    object code in the abstraction layer deals with translating the json (or dictionary) input to the relevant functions
    in the game code object object, also handles any connectivity/status information. 
    
    holds all stats for the current object. no information is stored elsewhere in code about this object except maybe in the debug area
    also this is where any stats at the end of game (or during as well) is saved to the data base for later computation (signal sent from game
    code at game end for new stats computation by the stats server)
    '''
    def __init__(self,id):
        self.ID=id
        #basic translation codes for things that are not item specific
        self.translation_codes={\
        'stup':self.status_update,          #status update, normally a health update from a previous got_hit()
        'ping':self.ping,                   #just a simple ping to keep the lines open, data is reported back, and logger.debug()'d
        'pong':self.pong,                   #similar to above, but no reply needed, only log data
        'dcon':self.close_connection,
        'evnt':self.fire_event              #data dict for a event, parse it and fire it off
        }
        self.status={#json-able data structure with all relevant object data and game data, empty here in this code
        }

    def run_packet(self,short_func,data):
        '''it is up to this function to decide what function gets called for what
        (got_hit(self.id,self,other), player_move(self.id,self,old_loc,new_loc) ect....
        '''
        
        if lib.common.debug() >4:
            #high debug
            logger.debug((short_func,data))

        if short_func in self.translation_codes:
            self.translation_codes[short_func](data)
        else:
            logger.error('packet unable to be run ! %s'%(str((self.ID,short_func,data))))
    def send_packet(self,short_func,data):
        '''Queue up a packet to be sent back across the network'''
        entities.entities[self.ID][1].outgoingq.put((short_func,json.dumps(data)))

    def ping(self,data):
        '''object ping'd the server, return pong and any data exactly as it was sent'''
        if 'pingdata' in data:
            logger.info('object %s pinged with data: %s'%(self.ID,data))
        send_packet("pong",data)
        
    
    def pong(self, data):
        '''server ping'd the object, this is the return pong 
        TODO: add server ping send, as well as travel time it takes to execute the command'''
        if 'pingdata' in data:
            logger.info('object %s ponged with data: %s'%(self.ID,data))
    
    def status_update(self,data):
        self.status.update(data)

    def fire_event(self,data):
        ''' got a event from the remote entity, fire it along...


        Event data structure:::
        {
            "name":"$$$$"
            "..."

        }

        '''
        if data['name'] not in events.base.events:
            logger.critical('event "%s" tried to fire but not found in event tree!'%data['name'])
            return
        event=events.base.events[data['name']](data)
        events.put(event)

        
    def close_connection(self,data):
        logger.info('object %s requesting closing network, "%s"'%(self.ID,data))
        entities.entities[self.ID][1].close()