'''
suit abstration layer code. handles communcation to the suits, providing a list of suits, and queues for communication

each suit is in a thread of control, no exceptions or errors in coms should ever stop the server



the server keeps track for a short time the data going to and from each suit, writing out the data after each verify that it recieves.
this means that when a suit looses its link, and then reconnects, both remember where they left off and re-handshake with all missing data


data def's:::

su_dict:: a dictionary of {SID:suit_con_handler}
'''
import logging
logger = logging.getLogger('abs.suit')

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

#local
import lib.cfg



su_dict={}
su_server=SocketServer.ThreadingTCPServer()###give host/port from lib.cfg.suit
su_server.daemon_threads = True
su_server_thread = threading.Thread(target=su_server.serve_forever)
su_server_thread.setDaemon(True)

#what the suit gives when it sends data, a 4 byte type, right now, request, response and status update only.
SRESPONSE = 'resp'
SREQUEST  = 'rqst'
SSTATUS   = 'stat'

class suit(object):
    '''
    sid == suit identification descriptor, each suit is unique.
    '''
    def __init__(self,sid):
        self.sid=sid
        
    def _read_sock(self):
        if self.sid in su_dict:
            if not su_dict[self.sid].outq.empty():
                #data to get and read/parse
                logger.info(su_dict[self.sid].outq.get())
        else:
            logger.warn('suit %s read requested, but suit not connected')


class suit_con_handler(SocketServer.BaseRequestHandler):
    '''handle a reconnecting suit, put new descriptor in the su_dict, if the list of suits does not have the relevant SID create new.'''
    def __init__(self, request, client_address, server):
        self.request = request
        self.client_address = client_address
        self.server = server
        
        try:
            self.setup()
            self.handle()
            self.finish()
        except Exception as e:
            self.finnish_ex(e)
        finally:
            sys.exc_traceback = None    # Help garbage collection

    
    def setup(self):
        '''
        create queue's and get the SID. place handler in su_dict
        '''
        self.inq = Queue.Queue(10) #read from suit
        self.outq= Queue.Queue(10) #headed to suit
        logger.info('handling new suit connection from %s'%(self.client_address))
        self.request.settimeout(0.5)
        self.getSID()
        logger.info('suit %s connected'%self.SID)
    def handle(self):
        while True:
            inputready,outputready,exceptionready = select.select([self.request],[],[])
            
            for streamobj in inputready:
                if streamobj == self.request:
                    #we have new data to read from suit, read it and append to outq
                    self.outq.put(self.read())
                    
    def read(self):
        '''time to define the data packet protocall we are using.
        data is sent with a header of 8 bytes.
        first 4 tell us how long the message is (aka content-length)
        next tell us what type of data it is (a request or a response)
        
        TODO:this sucks at large data, probably a good idea to find some way to limmit it...
        '''
        try:
            header = self.request.recv(8, socket.MSG_DONTWAIT)
        except socket.error, e:
            if e[0] != 11:
                raise
            #we did no yet recv our header? but it should be here! GAH!!
            raise Exception('header not recieved, was the socket really ready?')
        content_len = int(header[:4])
        ##type is 'resp' or 'rqst' or 'stat'
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
        #a nice mesage asking for the suits SID
        
        self.request.send('gsid')
        
        #block waiting for the response, but block nicly using select
        inputready,outputready,exceptionready = select.select([self.request],[],[])
            for streamobj in inputready:
                if streamobj == self.request:
                    tpye = None
                    while True:
                        type,data = self.read()
                        if type == SRESPONSE:
                            #data now holds sub-header of 4 bytes again.
                            if data[:4] == 'rsid':
                                #now that our data is here, and it was from this request, parse!
                                #simple expresion here btw
                                self.SID = sum([ord(i) for i in data[4:6]])
                                return
    def finnish(self):
        logger.warn('suit %s requested connection closed.'%self.SID)
    def finnish_ex(self,ex):
        buff=sio()
        traceback.print_exc(file=buff)
        logger.error('suit communication error! %s'%buff.getvalue())
        buff.close()
        del buff#stupid GC hates me
def init():
    '''start su_server thread, and watch thing-a-ma-jigs'''
    su_server_thread.start()


