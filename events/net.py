
from . import base

class connect_event(metaclass=base.Event):
    '''we just got a new connection, this is just after basic handshaking'''
    def __init__(self,kwargs):
        self.__dict__.update(kwargs)

class disconnect_event(metaclass=base.Event):
    '''lost a connection, for any reason.'''
    def __init__(self,kwargs):
        self.__dict__.update(kwargs)