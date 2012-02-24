
import logging
logger = logging.getLogger('game.gamebase')
import lib
#general base game code 


class gamebase(object):
    def __init__(self):
        '''base code for game objects
        
        this should be over ridden by new gametypes so that they can choose the *base classes to use
        '''
        self.tile = tilebase()
        self.suit = suitbase()
        self.gobj = gobjbase()
    def __del__(self):
        '''if we are really high on the debugging, log deletion of important game objects
        
        descoverd while testing this: it apeares that the translatio_codes are creating a refrence cycle
        that is not being garbage collected D:
        
        basically, this is here to clean up everything before we leave.
        '''
        del self.suit.translation_codes
        del self.tile.translation_codes
        del self.gobj.translation_codes
        if lib.common.debug()>4:
            logger.debug('game deleted::%s, %s'%(self.__class__, self))    
        
class objbase(object):
    def __init__(self):
        '''base class for all gameobjects (tiles, suits, game peices)
        the concept for these classes is that they will have the *base classes and some mixins, and by using mixins you get new features
            (example is adding a new got_hit function)
        
        '''
        self.translation_codes={'ghit':self.got_hit}
    if lib.common.debug() >4:#dont even include this function when running normally, dont want to have it cause collection errors
        print 'test123'
        def __del__(self):
            '''if we are really high on the debugging, log deletion of important game objects'''
            logger.debug('object deleted::%s, %s'%(self.__class__, self))
    def run_packet(self,proxyobj,short_func,data):
        '''it is up to this function to decide what function gets called for what
        (got_hit(self.id,self,other), player_move(self.id,self,old_loc,new_loc) ect....
        
        all functions that are called should return sucsess or failure (true/false)
        '''
        
        if lib.common.debug() >3:
            #high debug
            logger.debug((short_func,data))
        if short_func in self.translation_codes:
            return self.translation_codes[short_func](proxyobj,data)
            
    def got_hit(self,proxyobj,data):
        #in the future, load weapon from weapons in the arena
        if 'hits' not in proxyobj.status:
            proxyobj.status['hits'] = 1
        else:
            proxyobj.status['hits'] +=1
            
        logger.info('object %s got hit with weapon "%s", hit total of %s times'%(proxyobj.ID,data['weapon'], proxyobj.status['hits']))
        return True
class tilebase(objbase):
    def __init__(self):
        '''base for all tiles'''
        super(tilebase,self).__init__()
        
class suitbase(objbase):
    def __init__(self):
        '''base for all suits'''
        super(suitbase,self).__init__()
        
class gobjbase(objbase):
    def __init__(self):
        '''game thingy base class ( targets, bases, smart walls, turrets ect), really needs a new name that is not conflicting...'''
        super(gobjbase,self).__init__()