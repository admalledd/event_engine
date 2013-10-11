"""
listeners={
           "event_name":{
                    priority:[Event_listener()] #list of listeners for this priority
                    }
            }
"""

import logging
logger = logging.getLogger('event.base')
import importlib

import queue

event_queue = queue.Queue()

EVENT_LOW=30
EVENT_NORMAL=20
EVENT_HIGH=10
EVENT_HIGHEST=0

listeners={}
events={}



def put(event):
    event_queue.put(event)
def get():
    return event_queue.get()

def event_listener(name=None,priority=EVENT_NORMAL):
    ''' Event listening decorator for all listeners so that we can set
    up all the queue links and calling orders.
    '''

    if name==None:
        raise TypeError("event name cannot be None")
    if not isinstance(priority,int) or priority<0:
        raise TypeError("priority must be a int=>0")
    if name not in listeners:
        listeners[name]={}
        logger.warn('event "%s" not in cached event tree, might be ignored?'%name)
    if priority not in listeners[name]:
        listeners[name][priority]=list()

    def fn(clazz):
        obj=clazz()
        listeners[name][priority].append(obj)
        logger.debug('new listener on "%s" with priority "%s": "%s.%s()"'%(name,priority,clazz.__module__,clazz.__name__))
        return obj

    return fn

class Event(type):
    """Base event metaclass, root of the tree for all events"""
    def __new__(cls,class_name,bases,namespace):
        #bases= list(bases)
        #bases.append("events.base.Event")
        logger.warn((cls,class_name,bases,namespace))
        if class_name not in listeners:
            listeners[class_name]={}
        else:
            logger.warn('event "%s" already in cached listeners tree, duped event? or out-of order loading?'%class_name)
        if class_name in events:
            logger.severe("ERROR: multiple events of the same name in event tree!")
        else:
            events[class_name] = namespace['__module__']

        return type.__new__(cls,class_name,bases,namespace)
            
def init():
    for event,mname in events.items():
        mod = importlib.import_module(mname)
        clazz = getattr(mod, event)
        events[event] = clazz
    logger.warn(events)

class Event_listener:
    """Base listener class, subclasses must be decorated with @event_listener to work
    the __init__ cannot have arguments (@event_listener decorator inits for you, singleton) 
    """
    def run(self,event):
        '''Default run for an event listener, should be overridden by subclasses'''
        raise NotImplementedError() 