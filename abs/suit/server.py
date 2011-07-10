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

#local
import lib.cfg
from . import comms


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
        '''
        self.inq = Queue.Queue(10) #read from suit
        self.outq= Queue.Queue(10) #headed to suit
        logger.info('handling new suit connection from %s'%(self.client_address,))
        self.request.settimeout(0.5)
        self.getSID()
        logger.info('suit %s connected from %s'%(self.SID,self.client_address))
        if self.SID in suits:
            logger.warn('new connection for %s is already connected, overwritting old with new'%self.SID)
        suits[self.SID]=self
    def handle(self):
        while True:
            readready,writeready,exceptionready = select.select([self.request],[],[])
            
            for streamobj in readready:
                if streamobj == self.request:
                    #we have new data to read from suit, read it and append to outq
                    self.outq.put(self.read())
    def write(self,type,data):
        '''write same protocall as the read, but now we use it for output'''
        pass
    def read(self):
        '''time to define the data packet protocall we are using.
        data is sent with a header of 8 bytes.
        first 4 tell us how long the message is (aka content-length)
        next tell us what type of data it is (a request or a response)
        
        TODO:this sucks at large data, probably a good idea to find some way to limmit it...
        '''
        header = self.request.recv(8)
        content_len = int(header[:4])
        ##type is 'resp' or 'rqst' or 'stat'
        type = header[4:]
        if type not in comms.first:
            #carefull, if self.SID not inserted yet...
            logger.warn('first packet type from %s is not in database!'%self.SID)
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
        #a nice mesage asking for the suits SID
        
        self.request.send('gsid')
        
        #block waiting for the response, but block nicly using select
        inputready,outputready,exceptionready = select.select([self.request],[],[])
        for streamobj in inputready:
            if streamobj == self.request:
                tpye = None
                while True:
                    type,data = self.read()
                    if type == comms.cfg['first_type']['suit_response']:
                        #data now holds sub-header of 4 bytes again.
                        if data[:4] == 'rsid':
                            #now that our data is here, and it was from this request, parse!
                            #simple expresion here btw
                            self.SID = int(data[4:])
                            return
    def finnish(self):
        logger.warn('suit %s requested connection closed.'%self.SID)
        del suits[self.SID]
    def finnish_ex(self):
        buff=sio()
        traceback.print_exc(file=buff)
        logger.error('suit communication error! %s'%buff.getvalue())
        buff.close()
        del buff#stupid GC hates me
        try:
            del suits[self.SID]#remove connection from sharing dictionary
        except:
            logger.warn('suit connection error, yet suit not in registry')

su_server=SocketServer.ThreadingTCPServer((lib.cfg.abs['su_server']['host'],lib.cfg.abs['su_server'].as_int('port')), suit_con_handler)
su_server.daemon_threads = True
su_server_thread = threading.Thread(target=su_server.serve_forever)
su_server_thread.setDaemon(True)