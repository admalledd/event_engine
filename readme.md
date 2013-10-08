**Readme**
----------

In general this is a event server (think semi-rpc server...) hoping to make it a 
general game server for a few different projects.


**ToDo**
--------

* event listening system
    * main event queue (Thread safe INPUT)
    * Event loop that pulls one event and fires it through all listeners for that event
    * example put::: `events.put(events.base.Event())`
    * class decorator for event name / priority