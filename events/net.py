
from . import base


class connect_event(base.Event):
    '''we just got a new connection, this is just after basic handshaking'''

class disconnect_event(base.Event):
    '''lost a connection, for any reason.'''

class ping_event(base.Event):
    '''got a ping, go PONG!'''