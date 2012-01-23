import logging
logger = logging.getLogger('abs.suit.server')

import SocketServer
from lib import thread2 as threading
import select
import Queue
try: 
    from cStringIO import StringIO as sio
except ImportError:
    from StringIO import StringIO as sio
import traceback    
import sys
import struct
import string
import json
import time

#local
import lib.cfg
from . import suit

 

class suit_con_handler(SocketServer.BaseRequestHandler):
    '''handle a reconnecting suit, put new descriptor in the suits, if the list of suits does not have the relevant SID create new.'''
    def __init__(self, request, client_address, server):
        self.request = request
        self.client_address = client_address
        self.server = server
        
        try:
            self.setup()
            self.handle()
            self.finish()
        except Exception:
            #log exception and end connection handler
            self.finnish_ex()
        finally:
            sys.exc_traceback = None    # Help garbage collection
            #no matter what, if we are here, it is time to clear our netobj from suit.suits
            
            if self.SID != None:
                logger.debug('removed connection from suit "%s"'%self.SID)
                suit.suits[self.SID][1]=None
    
    def setup(self):
        '''
        create queue's and get the SID. place handler in suits
        
        queue's are in self.qu{first_tpye:queue}
        '''
        #suit version: 16 char string representing version, start with 'lzr'
        self.SID=None#start workable
        self.suitversion=self.request.recv(16)
        if not self.suitversion.startswith('lzr'):
            raise Excption('connection not from suit to suit server!')
        
        #SID is the second thing sent over the wire
        self.SID=struct.unpack('q',self.request.recv(8))[0]
        
        logger.info('handling new suit connection from:%s\n \
                     suit software version............:%s\n \
                     suit ID..........................:%s'%(self.client_address,self.suitversion,self.SID))
        
        #set up queue's
        self.incomingq = Queue.Queue(10) #read from suit
        self.outgoingq= Queue.Queue(10) #headed to suit
        
        
        #set timeout for network latency
        self.request.settimeout(0.5)
        
        #set up and start write thread
        self.write_thread = threading.Thread(target=self.writer)
        self.write_thread.setDaemon(True)
        self.write_thread.start()
        
        
        
        
        if self.SID in suit.suits and suit.suits[self.SID][1] is not None:
            logger.warn('new connection for %s is already connected, overwritting old with new'%self.SID)
            suit.suits[self.SID][1]=self
        else:
            logger.info('new suit object being created for %s'%self.SID)
            s=suit.suit(self.SID)
            suit.suits[self.SID]=[s,self]
            
    def close(self):
        self.write_thread.terminate()
        self.run_handler=False
        time.sleep(0.25)
        self.request.close()
        
    def handle(self):
        self.run_handler=True
        while self.run_handler:
            readready,writeready,exceptionready = select.select([self.request],[],[],0.25)
            for streamobj in readready:
                if streamobj == self.request:
                    self.handle_one()
                    
    def handle_one(self):
        header = self.request.recv(8)
        content_len = struct.unpack('I',header[:4])[0]
        #see description above for header layout
        short_func = header[4:]
        for ch in short_func:
            if ch not in string.ascii_letters:
                raise Exception('received bad call function, must be ascii_letters. got:"%s"'%short_func)
        ##read data in 1024 byte chunks, but once under, use actual size
        if content_len >1024:
            tcon = content_len
            data = []
            while tcon > 1024:
                data.append(self.request.recv(1024))
                tcon = tcon-1024
            data.append(self.request.recv(tcon))
            data = ''.join(data)
        else:
            data = self.request.recv(content_len)
        
        data=json.loads(data)
        #add to incomingq, for suit to read and actupon
        suit.suits[self.SID][0].run_packet(short_func,data)
        
    def make_packet(self,action,data):
        '''
        this function is broken out so others beyond the writer can use it
        packet def:
            '####xxxx'
            4 chars of number, being packet size packed using struct.pack('I',####)
            4 chars of ASCII letters, to either:
                if from suit: to translate into function names (eg: 'ghit'==def got_hit(self,weapon)...)
                    here data would be the json object representing the weapon
                if from server: action name for suit to do (eg, 'chst'==changestats)
                    here data would be something like: {'health':('-',5)} #loose five health
        '''
        if len(action) !=4:
            raise Exception('action must be 4 chars.')
        if not isinstance(data, basestring):
            data = json.dumps(data)
        header=struct.pack('I',len(data))+action
        return header+data
    
    def writer(self):
        '''eats things from the outgoing queue.
        format of outgoing data: tuple(action,jsonabledata)'''
        while True:
            short_func,data=self.outgoingq.get()
            packet=self.make_packet(short_func,data)
            ##todo::: add to stack for reliability the logging of all data out
            self.request.sendall(packet)
    def finnish(self):
        logger.warn('suit %s requested connection closed.'%self.SID)
        
        
    def finnish_ex(self):
        buff=sio()
        traceback.print_exc(file=buff)
        if self.SID is not None:
            buff.write('SUIT ID: %s\n'%self.SID)
        logger.error('suit communication error! %s'%buff.getvalue())
        buff.close()
        del buff#stupid GC hates me
        

su_server=None
su_server_thread=None
def init():
    global su_server
    global su_server_thread
    def run_server():
        try:
            su_server.serve_forever()
        finally:
            su_server.server.close()
    #set up our server. doesnt start yet, only when abs.suit.init() is called
    su_server=SocketServer.ThreadingTCPServer((lib.cfg.main['abs_suit_server']['host'],lib.cfg.main['abs_suit_server'].as_int('port')), suit_con_handler)
    su_server.daemon_threads = True
    su_server_thread = threading.Thread(target=run_server)
    su_server_thread.setDaemon(True)#start in new thread as to not hang the main thread in case we want console acsess (ipython?)