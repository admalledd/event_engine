import logging
logger=logging.getLogger('plugins.example_listener.submodule')

from events.base import Event_listener,event_listener
import entities

def unload():
    logger.debug("unloading...")

@event_listener("got_hit_event")
class got_hit_listener(Event_listener):
    """docstring for got_hit_listener"""
    def __init__(self):
        super().__init__()
        logger.info("got_hit_listener init")
    def run(self,event):
        logger.info("got_hit_listener called")


@event_listener("ping_event")
class ping_listener(Event_listener):
    """docstring for ping_listener"""
    def __init__(self):
        super().__init__()
        logger.info("ping_listener init")
    def run(self,event):
        logger.info("ping data:%s"%event.__dict__)
        logger.debug("sending pong...")
        event.entity.send_packet("pong",event.__dict__)
