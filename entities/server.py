import logging
logger = logging.getLogger('entities.server')


import socketserver


import select
import queue
from io import StringIO as sio
import traceback    
import sys
import struct
import string
import json
import time

#local
import lib.cfg
import threading

#abs layer imports, used for the creation of objects and finding the obj list for the relevent items
from .base import Entity



class con_handler(socketserver.BaseRequestHandler):
    '''handle a reconnecting object, put new descriptor in the relevent connection dict, if the relevent list does not have the relevant OID create new.
    
    the interface that connects this to all other objects (eg the abs.suit.suit):
        call obj.objlist[object ID][0].runpacket(func name,json data) for from obj->server data
        read self.outgoingq and parse to send over the network to the suit/tile/gamething/debug session
        
        these are the only ways that data is sent/received
        
    '''
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
            #no matter what, if we are here, it is time to clear our netobj from the relevent connection dict
            #look into possibly creating a dummy netobj that wont crash the other objects?
            if self.OID != None:
                logger.debug('removed connection from suit "%s"'%self.OID)
                self.server.entities_dict[self.OID][1]=None
        finally:
            self.make_event({"name":"disconnect_event",
                         "address":self.client_address,
                         "version":self.entversion,
                         "id":self.OID})

            
    
    def setup(self):
        '''
        create queue's and get the OID. place handler in suits
        
        queue's are in self.qu{first_tpye:queue}
        
        note that because we have no data yet for internal use we have to repeat much of the network code here
        if any problems occur with network code, please check both places due to this repeat that is difficult to remove
        '''
        #suit version: 16 char string representing version, start with 'lzr'
        self.OID=None
        self.entversion=self.request.recv(16)
        if not self.entversion.startswith(b'lzr'):
            raise Exception('connection not from suit to suit server!')
        
        #OID is the second thing sent over the wire
        self.OID=struct.unpack('q',self.request.recv(8))[0]
        #after OID is the single object type byte
        self.objtype = self.request.recv(1)
        
        logger.info('handling new suit connection from:%s\n \
                     suit software version............:%s\n \
                     suit ID..........................:%s'%(self.client_address,self.entversion,self.OID))
        
        #set up queue's
        self.incomingq = queue.Queue(10) #read from suit
        self.outgoingq= queue.Queue(10) #headed to suit
        
        
        #set timeout for network latency
        self.request.settimeout(0.5)
        self.run_handler=True
        
        #set up and start write thread
        self.write_thread = threading.Thread(target=self.writer)
        self.write_thread.setDaemon(True)
        self.write_thread.start()
                
        if self.OID in self.get_objlist() and self.get_objlist()[self.OID][1] is not None:
            logger.warn('new connection for %s is already connected, overwriting old with new'%self.OID)
            
            #as quickly as possible set up the new connection, after set up then we close the old connection
            #TODO:: find if an error in closing old will block/error the new connection
            old_conn=self.get_objlist()[self.OID][1]
            old_conn.close()
            self.get_objlist()[self.OID][1]=self
            
        elif self.OID in self.get_objlist() and self.get_objlist()[self.OID][1] is None:
            logger.warn('re-establishing closed connection from %s'%self.OID)
            self.get_objlist()[self.OID][1]=self
        else:
            logger.info('new netobj object being created for %s'%self.OID)
            s=Entity(self.OID)
            self.get_objlist()[self.OID]=[s,self]

        #now we are clear to fire a "hey new connection event!"
        self.make_event({"name":"connect_event",
                         "address":self.client_address,
                         "version":self.entversion,
                         "id":self.OID})

    def make_event(self,data):
        self.get_objinst().run_packet('evnt',data)
            
    def get_objlist(self):
        '''always used to make refrences as weak as possible without weakref's
        returns the obj dict (meaning it is not actually a list!)
        '''
        return self.server.entities_dict
        
    def get_objinst(self):
        '''get the object instance for this net instance, we dont store the ref because we want to be weak incase of problems'''
        return self.server.entities_dict[self.OID][0]
        
    def close(self):
        self.run_handler=False
        time.sleep(0.25)#wait for the handlers to close normally, but we can force it as well...
        self.request.close()#and if the handler is still open, this kills it with socket errors
        self.get_objlist()[self.OID][1]=None #remove ourselves from the EDICT
    def handle(self):
        while self.run_handler:
            readready,writeready,exceptionready = select.select([self.request],[],[],0.25)
            for streamobj in readready:
                if streamobj == self.request:
                    self.handle_one()
        self.close()

                    
    def handle_one(self):
        header = self.request.recv(8)
        content_len = struct.unpack('I',header[:4])[0]
        #see description above for header layout
        short_func = header[4:].decode("latin-1")
        for ch in short_func:
            if ch not in string.ascii_letters:
                raise Exception('received bad call function, must be ascii_letters. got:"%s"'%short_func)
        ##read data in 1024 byte chunks, but once under, use actual size
        ##TODO: rate limit the input, as is we read more and more data till we run out of ram. we need a max packet size and handler
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
        data=data.decode("UTF-8")
        jdata=json.loads(data)#must always have json data, of none/invalid let loads die
        
        if short_func == b'dcon':
            #dcon==disconnect request, do not pass up the layers, we handle that elsewhere...
            self.run_handler = False
            return
        self.get_objinst().run_packet(short_func,jdata)
        
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
        if not isinstance(data, str):
            data = json.dumps(data)
        header=struct.pack('I',len(data))+action
        return header+data
    
    def writer(self):
        '''eats things from the outgoing queue.
        format of outgoing data: tuple(action,jsonabledata)'''
        while self.run_handler:
            try:
                short_func,data=self.outgoingq.get(5)
            except:
                continue
            packet=self.make_packet(short_func,data)
            ##todo::: add to stack for reliability the logging of all data out
            self.request.sendall(packet)
    def finnish(self):
        logger.warn('OBJECT %s requested connection closed.'%self.OID)
        
        
    def finnish_ex(self):
        buff=sio()
        traceback.print_exc(file=buff)
        if self.OID is not None:
            buff.write('OBJECT ID: %s\n'%self.OID)
        logger.error('network communication error! %s'%buff.getvalue())
        buff.close()
        del buff#stupid GC hates me
        

server=None
server_thread=None
def init():
    global server
    global server_thread
    def run_server():
        try:
            server.serve_forever()
        finally:
            server.server.close()
    #set up our server. doesnt start yet, only when abs.suit.init() is called
    server=socketserver.ThreadingTCPServer(
        (
            lib.cfg.main['net_server']['host'],
            lib.cfg.main['net_server'].getint('port')
        ),
        con_handler)
    server.daemon_threads = True
    server_thread = threading.Thread(target=run_server)
    server_thread.setDaemon(True)
    server.entities_dict={}
    return server.entities_dict