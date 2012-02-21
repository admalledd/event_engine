
#general base game code 


class gamebase(object):
    def __init__(self):
        '''base code for game objects
        
        this should be over ridden by new gametypes so that they can choose the *base classes to use
        '''
        self.tile = tilebase()
        self.suit = suitbase()
        self.gobj = gobjbase()
        
        
class objbase(object):
    def __init__(self):
        '''base class for all gameobjects (tiles, suits, game peices)
        the concept for these classes is that they will have the *base classes and some mixins, and by using mixins you get new features
            (example is adding a new got_hit function)
        
        '''
        pass
    
    def got_hit(self,data):
        #in the future, load weapon from weapons in the arena
        ##TODO: remove debugish lines when we have more stuff, and place it in the debug inspector area. as well as moving all code to gamecode
        print data
        logger.info('object %s got hit with weapon "%s"'%(self.ID,data['weapon']))
        
class tilebase(objbase):
    def __init__(self):
        '''base for all tiles'''
        pass 
class suitbase(objbase):
    def __init__(self):
        '''base for all suits'''
        pass 
class gobjbase(objbase):
    def __init__(self):
        '''game thingy base class ( targets, bases, smart walls, turrets ect), really needs a new name that is not conflicting...'''
        pass 