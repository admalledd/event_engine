
import json
import struct

import threading
import select
import queue
import socket
import string
import time

HOST, PORT = "localhost", 1980

class con(object):
    def __init__(self,sid,objtype):
        '''   TODO::: have incomingq tack a callback paramiter so that when data is recv'd we call that function with the data'''
    
        self.sid=sid
        self.objtype=objtype.encode('ascii')
        self.incomingq = queue.Queue(10) #read from sserver
        self.outgoingq= queue.Queue(10) #headed to server
        self.is_connected=False
        
    def connect(self):
        # Create a socket (SOCK_STREAM means a TCP socket)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setblocking(1)
        # Connect to server and send data
        self.sock.connect((HOST, PORT))
        #send SuitSoftware version, first thing, size 16
        self.sock.send(b'lzr debug pygame')
        #send SID next
        self.sock.send(struct.pack('q',self.sid))
        self.sock.send(self.objtype)
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
        while True:
            header = self.sock.recv(8)
            if len(header) < 8 and not self.is_connected:
                return #we disconnected
                
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
        data = json.dumps(data)
        header=struct.pack('I',len(data))+action.encode('ascii')
        #remove if debuging network data
        ##print (header,data)

        return header+data.encode('ascii')
        
    def write(self):
        '''eats things from the outgoing queue.
        format of outgoing data: tuple(action,jsonabledata)'''
        while True:
            short_func,data=self.outgoingq.get()
            packet=self.make_packet(short_func,data)
            ##todo::: add to stack for reliability the logging of all data out
            self.sock.sendall(packet)