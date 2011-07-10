'''
suit abstration layer code. handles communcation to the suits, providing a list of suits, and queues for communication

each suit is in a thread of control, no exceptions or errors in coms should ever stop the server



the server keeps track for a short time the data going to and from each suit, writing out the data after each verify that it recieves.
this means that when a suit looses its link, and then reconnects, both remember where they left off and re-handshake with all missing data


data def's:::

suits:: a dictionary of {SID:suit_con_handler}
'''
import logging
logger = logging.getLogger('abs.suit')



suits={}



class suit(object):
    '''
    sid == suit identification descriptor, each suit is unique.
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


def init():
    '''start su_server thread, and watch thing-a-ma-jigs'''
    su_server_thread.start()


