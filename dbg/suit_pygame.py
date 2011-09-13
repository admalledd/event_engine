import socket
import sys
import threading
import select
import Queue
import random

import pygame
pygame.init()
from pygame.locals import *

HOST, PORT = "localhost", 1987
SID = 127

class con(object):
    def __init__(self):
        
        # Create a socket (SOCK_STREAM means a TCP socket)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Connect to server and send data
        self.sock.connect((HOST, PORT))
        
        self.inq = Queue.Queue(10) #read from server
        self.outq= Queue.Queue(10) #headed to server
        
        
        self.w_thread = threading.Thread(target=self.write)
        self.w_thread.setDaemon(True)
        self.w_thread.start()
        self.r_thread = threading.Thread(target=self.handle)
        self.r_thread.setDaemon(True)
        self.r_thread.start()
    def parse_put(self,type,data):
        if type=='rqid':
            if data[:4] == 'sidx':
                self.inq.put(('srid','sidx%s'%SID))
                return #because we already took care of this, dont add to output, but not all needs to be blocked from output
        self.outq.put((type,data))
        
        
    def handle(self):
        '''here we wait forever waiting for data. once it arrives, send control to self.read(), and pass data to self.parse_put()'''
        while True:
            self.handle_one()
    def handle_one(self):
        '''handle one data packet from suit to server'''
        readready,writeready,exceptionready = select.select([self.sock],[],[])
        for streamobj in readready:
            if streamobj == self.sock:
                #we have new data to read from suit, read it and pass to self.parse_put()
                type,data=self.read()
                self.parse_put(type,data)
    def make_packet(self,type,data):
        content_len = str(len(data))
        if len(content_len) > 4:
            raise Error('data packet too large for protocall')
        while len(content_len) <4:
            content_len='0'+content_len
        if len(type) !=4:
            raise Error('type must be 4 bytes long')
        
        pak=''.join((content_len,type,data))
        print pak
        return pak
        
        
    def read(self):
        header = self.sock.recv(8)
        content_len = int(header[:4])
        #see description above for header layout
        type = header[4:]
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
        return type,data
        
        
    def write(self):
        '''write same protocall as the read, but now we use it for output'''
        while True:
            type,data=self.inq.get()
            packet=self.make_packet(type,data)
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
                pygame.quit()
                return None
            elif event.type == MOUSEBUTTONDOWN and event.button==1:
                print 'click'
                suit.inq.put(('ssxx','{shot:%s,%s,%s,%s}'%('wep','teamblu','97',SID)))
        screen.fill((0, 0, 0))
        screen.blit(text, text.get_rect())
        pygame.display.flip()
if __name__=='__main__':
    main()