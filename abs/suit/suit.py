import logging
logger = logging.getLogger('abs.suit.suit')
import threading
import lib.common
import lib.cfg

class suit(object):
    '''
    self.sid == suit identification descriptor, each suit is unique.
    
    self.wr == weakref to the suit connection handler, allows for it to die, but must be careful to check its life each time...
    '''
    def __init__(self,sid,weakref):
        self.sid=sid
        self.wr=weakref#updated via abs.suit.server upon new connection
        
        self.dispatcher_t=threading.Thread(target=self.dispatcher)
        self.dispatcher_t.setDaemon(True)
        self.dispatcher_t.start()
    def dispatcher(self):
        '''it is up to this function to decide what function gets called for what
        (got_hit(self.sid,self,other), player_move(self.sid,self,old_loc,new_loc) ect....
        '''
        while True:
            if self.wr() is None:
                return#its the end, our weakref is dead. stop doing things in the active loop
            type,data = self.wr().outq.get()
            if lib.common.debug() >4:
                #high debug
                logger.debug((type,data))
                