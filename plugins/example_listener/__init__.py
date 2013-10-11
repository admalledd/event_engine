import logging
logger=logging.getLogger('plugins.example_listener')

from events.base import Event_listener,event_listener

#TODO: submodle imports!
#import plugins.example_listener.submodule
#from . import submodle

@event_listener("connect_event")
class listen_tester(Event_listener):
    """docstring for listen_tester"""
    def __init__(self):
        super().__init__()
        logger.info("listen_tester init")
    def run(self):
        logger.info("listen_tester called")

