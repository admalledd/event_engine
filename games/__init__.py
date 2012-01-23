



#define game base classes here, with other files for library action

#all communication in the game code is call-response only
#however the suits should be doing a "status update/check" about every 250 milliseconds





class game(object):
    def __init__(self):