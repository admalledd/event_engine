
import json
import struct

import threading
import select
import queue
import socket
import string
import time

HOST, PORT = "localhost", 1980

class connection:
    def __init__(self,sid,
            host="localhost",
            port=1980,
            objtype="s",
            version=b'lzr debug client'):

        self.sid=sid
        self.objtype=objtype
        self.version=version
        self.host=host
        self.port=port
        self.incomingq = queue.Queue(10) #read from sserver
        self.outgoingq= queue.Queue(10) #headed to server
        self.is_connected=False
        
    def connect(self):
        # Create a socket (SOCK_STREAM means a TCP socket)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setblocking(1)
        # Connect to server and send data
        self.sock.connect((host, port))
        #send SuitSoftware version, first thing, size 16
        self.sock.send(version)
        #send SID next
        self.sock.send(struct.pack('q',self.sid))
        self.sock.send(objtype.encode('ascii'))
        self.w_thread = threading.Thread(target=self.write)
        self.w_thread.setDaemon(True)
        self.w_thread.start()
        self.r_thread = threading.Thread(target=self.handle)
        self.r_thread.setDaemon(True)
        self.r_thread.start()
        
        self.is_connected=True
        
    def close(self):
        self.outgoingq.put(('dcon',{}))
        self.is_connected=False
        time.sleep(0.25)
        self.sock.close()
        
        
    def handle(self):
        while self.is_connected:
            header = self.sock.recv(8)
            if len(header) < 8 and not self.is_connected:

                break #we disconnected
                
            content_len = struct.unpack('I',header[:4])[0]
            #see description above for header layout
            short_func = header[4:].decode("ascii")
            for ch in short_func:
                if ch not in string.ascii_letters:
                    raise Exception('received bad call function, must be ascii_letters. got:"%s"'%short_func)
            ##read data in 1024 byte chunks, but once under, use actual size
            if content_len >1024:
                tcon = content_len
                data = []
                while tcon > 1024:
                    data.append(self.sock.recv(1024))
                    tcon = tcon-1024
                data.append(self.sock.recv(tcon))
                data = ''.join(data)
            else:
                data = self.sock.recv(content_len)
            data=json.loads(data.decode('UTF-8'))
            self.incomingq.put((header,data))
        logger.info("connection closed")
            
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
        if len(action.encode('ascii')) !=4:
            raise Exception('action must be 4 chars.')
        data = json.dumps(data,skipkeys=True,default=lambda o:str(o))
        header=struct.pack('I',len(data))+action.encode('ascii')
        #remove if debuging network data
        ##print (header,data)

        return header+data.encode('ascii')
        
    def writer(self):
        '''eats things from the outgoing queue.
        format of outgoing data: tuple(action,jsonabledata)'''
        while self.is_connected:
            try:
                short_func,data=self.outgoingq.get(timeout=1)
            except:
                logger.debug("writer outgoingq timeout")
                continue
            packet=self.make_packet(short_func,data)
            ##todo::: add to stack for reliability the logging of all data out
            self.request.sendall(packet)
        logger.debug("writer thread closed")

    def put(self,event):
        '''helper function to send data. errors if connection is closed'''
        if not self.is_connected:
            raise Exception("Connection was closed. Re-open or find out why we disconnected first!")
        self.put_raw('evnt',event)
    def put_raw(self,short_func,data):
        '''we assume that you already have checked self.is_connected, and such...'''
        self.outgoingq.put((short_func,data))