
from . import base

class connect_event(base.Event):
    '''we just got a new connection, this is just after basic handshaking'''
    def __init__(self,ip,port,name):
        self.ip = ip
        self.port=port
        self.name=name