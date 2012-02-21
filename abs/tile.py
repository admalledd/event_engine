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
        
        #initialize basic common things, including ID
        absbase.absbase.__init__(self,ID)
        ##self.translation_codes.update({}) #unused
        
        self.status.update({#json-able data structure with all relavent tile data and game data
        'location':[0,0],
        })
    
    def run_packet(self,short_func,data):
        '''pass thinking off to the super class, but add in our obtype
        '''
        absbase.absbase.run_packet(self,'tile',short_func,data)
    