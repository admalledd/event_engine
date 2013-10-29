import logging
logger=logging.getLogger('remote.example_remote')

from events.base import Event_listener

from . import submodule

def unload():
    logger.debug("unloading...")
def onload():
    '''only __init__.py of the plugin gets onload() called,
     its up to the plugin to recurse to submodules'''
    logger.debug("loading...")
    submodule.onload()

class listen_tester(Event_listener):
    """docstring for listen_tester"""
    etype="connect_event"
    def __init__(self):
        super().__init__()
        logger.info("remote listen_tester init")
    def run(self,event):
        logger.info("remote Connection from %s opened"%event.id)

