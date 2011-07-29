class suit(object):
    '''
    self.sid == suit identification descriptor, each suit is unique.
    
    self.wr_suit_con == weakref to the suit connection handler, allows for it to die, but must be careful to check its life each time...
    '''
    def __init__(self,sid):
        self.sid=sid
        
    def _read_sock(self):
        if self.sid in suits:
            if not suits[self.sid].outq.empty():
                #data to get and read/parse
                logger.info(suits[self.sid].outq.get())
        else:
            logger.warn('suit %s read requested, but suit not connected')

