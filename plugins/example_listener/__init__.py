import logging
logger=logging.getLogger('plugins.example_listener')

from events.base import Event_listener

from . import submodule

def unload():
    logger.debug("unloading...")

class listen_tester(Event_listener):
    """docstring for listen_tester"""
    etype="connect_event"
    def __init__(self):
        super().__init__()
        logger.info("listen_tester init")
    def run(self,event):
        logger.info("listen_tester called")

