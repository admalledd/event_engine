import logging
logger=logging.getLogger('remote.example_remote.submodule')

from events.base import Event_listener,Event
import entities

def unload():
    logger.debug("unloading...")
def onload():
    logger.debug('loading...')

class got_hit_listener(Event_listener):
    """docstring for got_hit_listener"""
    etype="got_hit_event"
    def __init__(self):
        super().__init__()
        logger.info("remote got_hit_listener init")
    def run(self,event):
        logger.info("remote got_hit_listener called")


class ping_listener(Event_listener):
    """docstring for ping_listener"""
    etype="ping_event"
    def __init__(self):
        super().__init__()
        logger.info("remote ping_listener init")
    def run(self,event):
        logger.info("remote ping data:%s"%event.__dict__)
        logger.debug("sending pong...")
        event.entity.send_packet("pong",event.__dict__)