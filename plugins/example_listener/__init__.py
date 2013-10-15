import logging
logger=logging.getLogger('plugins.example_listener')

from events.base import Event_listener,event_listener

from . import submodule

def unload():
    logger.debug("unloading...")
    1/0

@event_listener("connect_event")
class listen_tester(Event_listener):
    """docstring for listen_tester"""
    def __init__(self):
        super().__init__()
        logger.info("listen_tester init")
    def run(self,event):
        logger.info("listen_tester called")

