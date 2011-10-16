import socket
import sys
import threading
import select
import Queue
import random
import json
import struct

import pygame
pygame.init()
from pygame.locals import *

HOST, PORT = "localhost", 1987
SID = 127

class con(object):
    def __init__(self):
        
        # Create a socket (SOCK_STREAM means a TCP socket)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setblocking(1)
        # Connect to server and send data
        self.sock.connect((HOST, PORT))
        #send SuitSoftware version, first thing, size 16
        self.sock.send('lzr debug pygame')
        #send SID next
        self.sock.send(struct.pack('q',SID))
        
        self.incomingq = Queue.Queue(10) #read from sserver
        self.outgoingq= Queue.Queue(10) #headed to server
        
        self.w_thread = threading.Thread(target=self.write)
        self.w_thread.setDaemon(True)
        self.w_thread.start()
        self.r_thread = threading.Thread(target=self.handle)
        self.r_thread.setDaemon(True)
        self.r_thread.start()
        
        
    def handle(self):
        while True:
            header = self.sock.recv(8)
            print repr(header)
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
                    data.append(self.sock.recv(1024))
                    tcon = tcon-1024
                data.append(self.sock.recv(tcon))
                data = ''.join(data)
            else:
                data = self.sock.recv(content_len)
        
            data=json.loads(data)
        
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
        print header+data
        return header+data
        
    def write(self):
        '''eats things from the outgoing queue.
        format of outgoing data: tuple(action,jsonabledata)'''
        while True:
            short_func,data=self.outgoingq.get()
            packet=self.make_packet(short_func,data)
            ##todo::: add to stack for reliability the logging of all data out
            self.sock.sendall(packet)
            
def main():
    screen = pygame.display.set_mode((640, 480))
    font = pygame.font.Font(None, 18)
    text = font.render('hello world',True,(255,0,255)).convert_alpha()
    suit=con()
    while True:
        pygame.time.wait(10)
        for event in pygame.event.get():
            if event.type == QUIT:
                suit.outgoingq.put(('dcon',json.dumps({'reason':'test over'})))
                pygame.time.wait(250)
                pygame.quit()
                return None
            elif event.type == MOUSEBUTTONDOWN and event.button==1:
                print 'click'
                suit.outgoingq.put(('ghit',json.dumps({'weapon':'basic','team':'teamblu','from':7589})))
        screen.fill((0, 0, 0))
        screen.blit(text, text.get_rect())
        pygame.display.flip()
if __name__=='__main__':
    main()