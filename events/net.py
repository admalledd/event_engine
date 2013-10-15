
from . import base


class connect_event(metaclass=base.Event):
    '''we just got a new connection, this is just after basic handshaking'''

class disconnect_event(metaclass=base.Event):
    '''lost a connection, for any reason.'''

class ping_event(metaclass=base.Event):
    '''got a ping, go PONG!'''