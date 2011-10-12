'''
suit abstration layer code. handles communcation to the suits, providing a list of suits, and queues for communication

each suit is in a thread of control, no exceptions or errors in coms should ever stop the server



the server keeps track for a short time the data going to and from each suit, writing out the data after each verify that it recieves.
this means that when a suit looses its link, and then reconnects, both remember where they left off and re-handshake with all missing data


data def's:::

suits:: a dictionary of {SID:suit_obj}
'''
#std lib
import logging
logger = logging.getLogger('abs.suit')

#server libs
import lib.cfg

#abs layer
from . import network





def init():
    '''start su_server thread, and watch thing-a-ma-jigs'''
    network.init()
    network.su_server_thread.start()
    logger.info('abs.suit server started')


