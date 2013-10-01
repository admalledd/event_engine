import logging
logger = logging.getLogger('event.base')

import queue

event_queue = queue.Queue()


def put(event):
    if not isinstance(event,Event):
        raise TypeError("event %r not a child of <events.base.Event>"%event)
    logger.debug(event)
    event_queue.put(event)
def get():
    return event_queue.get()


class Event:
    """Base event class, root of the tree for all events"""
    def __init__(self):
        pass
