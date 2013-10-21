import logging
logger=logging.getLogger('plugins.example_listener.submodule')

from events.base import Event_listener,Event
import entities

def unload():
    logger.debug("unloading...")

class got_hit_event(Event):
    pass


class got_hit_listener(Event_listener):
    """docstring for got_hit_listener"""
    etype="got_hit_event"
    def __init__(self):
        super().__init__()
        logger.info("got_hit_listener init")
    def run(self,event):
        logger.info("got_hit_listener called")


class ping_listener(Event_listener):
    """docstring for ping_listener"""
    etype="ping_event"
    def __init__(self):
        super().__init__()
        logger.info("ping_listener init")
    def run(self,event):
        logger.info("ping data:%s"%event.__dict__)
        logger.debug("sending pong...")
        event.entity.send_packet("pong",event.__dict__)