import logging
logger = logging.getLogger('abs.tile')

import lib.common#for debug

from . import base
import entities


class tile(base.Entity):
    '''
    self.ID == tile identification descriptor, each tile is unique.
    self.ID == netobj.OID   aka:: abs.objects[self.ID][1].OID == self.ID
    
    
    '''
    def __init__(self,ID):
        
        #initialize basic common things, including ID
        super().__init__(ID)
        ##self.translation_codes.update({}) #unused
        
        self.status.update({#json-able data structure with all relavent tile data and game data
        'location':[0,0],
        })
    
    def run_packet(self,short_func,data):
        '''pass thinking off to the super class, but add in our obtype
        '''
        super().run_packet(self,'tile',short_func,data)
    