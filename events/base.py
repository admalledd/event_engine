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

class _meta_Event_listener(type):
    """Base listener class, subclasses must be decorated with
    the __init__ cannot have arguments (@event_listener decorator inits for you, singleton) 
    """
    def __new__(cls,class_name,bases,namespace):
        #logger.debug((cls,class_name,bases,namespace))

        #ignore the base class... it does not get added to the event tree...
        if namespace['__module__'] == "events.base" and class_name == "Event_listener":
            return type.__new__(cls,class_name,bases,namespace)

        if 'etype' not in namespace:
            raise TypeError("etype must be set")

        if 'priority' not in namespace:
            namespace['priority'] = EVENT_NORMAL
        if not isinstance(namespace['priority'], int) or namespace['priority'] <0:
            raise TypeError("priority must be int=>0")

        if namespace['etype'] not in listeners:
            listeners[namespace['etype']]={}
            logger.warn('event "%s" not in cached event tree, might be ignored?'%namespace['etype'])
        if namespace['priority'] not in listeners[namespace['etype']]:
            listeners[namespace['etype']][namespace['priority']]=list()


        cls = type.__new__(cls,class_name,bases,namespace)
        #append only the class, not an instance. for some reason we kill python3 and pypy3 otherwise?
        listeners[namespace['etype']][namespace['priority']].append(cls)

        logger.debug('new listener on "%s" with priority "%s": "%s.%s()"'%(
            namespace['etype'],
            namespace['priority'],
            namespace['__module__'],
            class_name))
        return cls

class Event_listener(metaclass=_meta_Event_listener):
    def run(self,event):
        '''Default run for an event listener, should be overridden by subclasses'''
        raise NotImplementedError()


class _meta_event(type):
    """Base event metaclass, root of the tree for all events."""
    def __new__(cls,class_name,bases,namespace):
        #logger.debug((cls,class_name,bases,namespace))
        if class_name == "Event" and namespace['__module__'] == 'events.base':
            return type.__new__(cls,class_name,bases,namespace)
        if class_name not in listeners:
            listeners[class_name]={}
        else:
            logger.warn('event "%s" already in cached listeners tree, duped event? or out-of order loading?'%class_name)
        if class_name in events:
            logger.severe("multiple events of the same name in event tree! event '%s'"%class_name)
            return
        else:
            events[class_name] = namespace['__module__']
        cls=type.__new__(cls,class_name,bases,namespace)
        logger.debug('event "%s" added to event tree from %s.%s'%(
            class_name,
            namespace['__module__'],
            class_name)
        )
        events[class_name]=cls
        return cls


class Event(metaclass=_meta_event):
    '''The true base class for events, here are all the default functions ect ect
    most will raise NotImplementedError

    '''
    def __init__(self,kwargs):
        self.kwargs=kwargs
        d={}
        d.update(self.__dict__)
        d.update(kwargs)
        self.__dict__=d

