import logging
logger=logging.getLogger('plugins.example_listener.submodule')

from events.base import Event_listener,event_listener

@event_listener("connect_event")
class listen_tester2(Event_listener):
    """docstring for listen_tester"""
    def __init__(self):
        super().__init__()
        logger.info("listen_tester2 init")
    def run(self):
        logger.info("listen_tester2 called")
