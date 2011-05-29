



def find():
    '''find all active players upon startup, or find any players missing a playerobject'''
    
    #still in testing, return just the 127.0.0.1:1981 test port for the fakeplayer server
    return [Player('127.0.0.1',1981)]
    
class Player(object):
    def __init__(self,host,port):
        '''player comunications instance, handles hinding the un-needed worry of network code
        player data is updated whenever we get new data from the suit. 
        
        network coms layout:
        
        
        
        stats layout: both dict and object:: stats['location'] == stats.location
        location: x,y coord based on center tile
        health:
        active:'''
        
        
        self.stats={
        'location':[25,25]
        }