'''here we define the raw network stuff for the suit interface to the abstraction layer.

how this works in a step-by-step:

1:suit connects to server on (lib.cfg.abs_suit['su_server']['host'],lib.cfg.abs_suit['su_server'].as_int('port'))
2:server requests SID
3:check abs.suit.suits for this SID (note that abs.suit.suits is a copy of the one in this area, look out!)
4-a: if sid is in dictionary, update it to this connection (assume failure of network and suit is re-negotiating)
4-b: if sid is NOT in dictionary, create SID suit object, add to that object a weakref to this connection


'''



import logging
logger = logging.getLogger('abs.suit.server')

import SocketServer
import socket
import threading
import select
import Queue
try: 
    from cStringIO import StringIO as sio
except ImportError:
    from StringIO import StringIO as sio
import traceback    
import sys
import weakref


#local
import lib.cfg
from . import suit
suits={}

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

    
    def setup(self):
        '''
        create queue's and get the SID. place handler in suits
        
        queue's are in self.qu{first_tpye:queue}
        '''
        self.SID=None
        self.inq = Queue.Queue(10) #read from suit
        self.outq= Queue.Queue(10) #headed to suit
        logger.info('handling new suit connection from %s'%(self.client_address,))
        #set timeout for network latency
        self.request.settimeout(0.5)
        
        #set up and start write thread
        self.write_thread = threading.Thread(target=self.write)
        self.write_thread.setDaemon(True)
        self.write_thread.start()
        
        self.getSID()
        logger.info('suit %s connected from %s'%(self.SID,self.client_address))
        
        
        if self.SID in suits:
            logger.warn('new connection for %s is already connected, overwritting old with new'%self.SID)
            suits[self.SID].wr=weakref.ref(self)
            suits[self.SID].dispatcher_t.start()
        else:
            logger.info('new suit object being created for %s'%self.SID)
            s=suit.suit(self.SID,weakref.ref(self))
            suits[self.SID]=s
            
            
    def handle(self):
        '''here we wait forever waiting for data. once it arrives, send control to self.read(), and pass data to self.parse_put()'''
        while True:
            self.handle_one()
            
            
    def handle_one(self):
        '''handle one data packet from suit to server'''
        readready,writeready,exceptionready = select.select([self.request],[],[])
        for streamobj in readready:
            if streamobj == self.request:
                #we have new data to read from suit, read it and pass to self.parse_put()
                type,data=self.read()
                self.parse_put(type,data)
                    
                    
    def parse_put(self,type,data):
        '''parse the header packet and put the data into the queue it belongs in.
        the suit.suit() object has a thread trying to read input and fires the correct functions based off of this.
        however, if any special signals arrive that need to be grabbed here at the lower level, this is where it happens
        
        type definition:
        # 
        ##  "xyzzasdf"
        #
        # "x" first char: "r" or "s" r== server to suit packet, s==suit to server packet
        #
        # "y" second char: "r" or "q" or "s" r==response to query, q==query for data, s==satus packet
        #
        # "zz" third and fourth chars: these deal with the specific data type that this packet is. in this level of
        #the code, we cannot tell what these are for. all we can do is pass them up to the next level.
        #however, there are some exceptions to this, most notably, when requesting the SID. this must be captured down here.
        #
        #
        #
        # "asdf" fourth to eigth char: next header, part of data.
        
        #x is used for filler of packet. packet headers are in multiples of 4-bytes
        
        '''
        ##todo::: add to stack for reliability the logging of all data in
        
        #here is an example of not passing the code any higher: are we receiving a SID packet?
        if type=='srid':#srid means suit responding to server about id packet
            if data[:4] == 'sidx':#data packed is a SID id packet (not a team packet or suit name packet)
                self.SID=int(data[4:])#get our SID
                return #because we already took care of this, dont add to output, but not all needs to be blocked from output
        if lib.common.debug() >4:
            #high debug level, print raw packets
            logger.debug((type,data))
        self.outq.put((type,data))
        
        
    def write(self):
        '''write same protocall as the read, but now we use it for output'''
        while True:
            type,data=self.inq.get()
            packet=self.make_packet(type,data)
            ##todo::: add to stack for reliability the logging of all data out
            self.request.sendall(packet)
            
            
    def make_packet(self,type,data):
        content_len = str(len(data))
        if len(content_len) > 4:
            raise Error('data packet too large for protocall')
        while len(content_len) <4:
            content_len='0'+content_len
        if len(type) !=4:
            raise Error('type must be 4 bytes long')
        
        pak=''.join((content_len,type,data))
        return pak
        
        
    def read(self):
        '''time to define the data packet protocall we are using.
        data is sent with a header of 8 bytes.
        first 4 tell us how long the message is (aka content-length)
        next tell us what type of data it is (a request or a response)
        
        
        header definition:
        # 
        ##  "asdfxyzz"
        #
        # "asdf" first to fourth char: size of packet in bytes, not including 8byte header for parsing
        #
        # "x" fifth char: "r" or "s" r== server to suit packet, s==suit to server packet
        #
        # "y" sixth char: "r" or "q" or "s" r==response to query, q==query for data, s==satus packet
        #
        # "zz" seventh and eigth chars: these deal with the specific data type that this packet is. in this level of
        #the code, we cannot tell what these are for. all we can do is pass them up to the next level.
        #however, there are some exceptions to this, most notably, when requesting the SID. this must be captured down here.
        #
        #
        #
        
        #x is used for filler of packet. packet headers are in multiples of 4-bytes


        TODO:this sucks at large data, probably a good idea to find some way to limmit it...
        '''
        header = self.request.recv(8)
        content_len = int(header[:4])
        #see description above for header layout
        type = header[4:]
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
        return type,data
        
        
    def getSID(self):
        '''a nice mesage asking for the suits SID
        requests SID, then waits for self.SID to be filled via normal self.parse_put() functionality
        '''
        self.inq.put(('rqid','sidx'))#send get SID request
        
        #block waiting for the response, but block nicly using select
        
        while self.SID is None:
            self.handle_one()
            
            
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
    #set up our server. doesnt start yet, only when abs.suit.init() is called
    su_server=SocketServer.ThreadingTCPServer((lib.cfg.main['abs_suit_server']['host'],lib.cfg.main['abs_suit_server'].as_int('port')), suit_con_handler)
    su_server.daemon_threads = True
    su_server_thread = threading.Thread(target=su_server.serve_forever)
    su_server_thread.setDaemon(True)