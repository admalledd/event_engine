
#define game base classes here, with other files for library action

#all communication in the game code is call-response only
#however the suits should be doing a "status update/check" about every 250 milliseconds
#during this status/update check we can respond with anything we want to force onto the suit

#from .gamebase import gamebase as default


from events.base import Event_listener,event_listener

@event_listener("connect_event")
class listen_tester(Event_listener):
    """docstring for listen_tester"""
    def __init__(self):
        super().__init__()
        print("listen_tester init")

