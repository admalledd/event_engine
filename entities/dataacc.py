import logging
logger = logging.getLogger('abs.dataacc')
import pprint


import lib.common#for debug

from . import base
import entities


class dataacc(base.Entity):
    '''
    self.ID == object identification descriptor, each suit is unique.
    self.ID == netobj.OID   aka:: abs.objects[self.ID][1].OID == self.ID
    
    
    '''
    def __init__(self,ID):
        
        #initialize basic common things, including ID
        super().__init__(ID)
        self.translation_codes.update({
                                        'sget':self.status_get
                                        })
        
        self.status.update({#json-able data structure with all relavent suit data and game data
        'health':100,
        'ammos':[100],
        'weapon':0,#weapon is the index for weapons and ammo
        'weapons':['basic'],
        'location':[0,0],
        'team':'red',
        'player_name':'john_doe'
        })

    def status_get(self,data):
        '''get the status dict of a object and return it as a pprint.format string'''
        
        entities.entities[self.ID][1].outgoingq.put(('sgot',abs.objects[data['oid']][0].status))
        
        
    
    def run_packet(self,short_func,data):
        '''pass thinking off to the super class, but add in our obtype
        
        note that most if not all data accesor calls should be handeld here, they should not make it to the game code often if at all.
        '''
        super().run_packet(self,'suit',short_func,data)
    