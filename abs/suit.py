import logging
logger = logging.getLogger('abs.suit')

import lib.common#for debug

from . import absbase
import abs


class suit(absbase.absbase):
    '''
    self.ID == suit identification descriptor, each suit is unique.
    self.ID == netobj.OID   aka:: abs.objects[self.ID][1].OID == self.ID
    
    
    '''
    def __init__(self,ID):
        
        #initialize basic common things, including ID
        absbase.absbase.__init__(self,ID)
        ##self.translation_codes.update({}) #unused
        
        self.status.update({#json-able data structure with all relavent suit data and game data
        'health':100,
        'ammos':[100],
        'weapon':0,#weapon is the index for weapons and ammo
        'weapons':['basic'],
        'location':[0,0],
        'team':'red',
        'player_name':'john_doe'
        })

    def run_packet(self,short_func,data):
        '''pass thinking off to the super class, but add in our obtype
        '''
        absbase.absbase.run_packet(self,'suit',short_func,data)
    