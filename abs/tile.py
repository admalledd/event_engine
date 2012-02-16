import logging
logger = logging.getLogger('abs.tile')

import lib.common#for debug

from . import absbase
import abs

class tile(object):
    '''
    self.ID == tile identification descriptor, each tile is unique.
    self.ID == netobj.OID
    
    
    '''
    def __init__(self,id):
        self.ID=id
        
        ##self.translation_codes.update({}) #unused
        
        self.status={#json-able data structure with all relavent tile data and game data
        'location':[0,0],
        'arena':0#int of what arena this object is in (should be updated from the client on connect, must not be zero long
        }
    
    def run_packet(self,short_func,data):
        '''pass thinking off to the super class, but add in our obtype
        '''
        absbase.absbase.run_packet(self,'suit',short_func,data)
    