

class got_hit_event(metaclass=base.Event):
    '''got hit event'''
    def __init__(self,kwargs):
        self.__dict__.update(kwargs)
        