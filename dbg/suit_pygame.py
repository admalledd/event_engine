import socket
import sys
import threading
import select
import Queue
import random
import json
import struct
import os
import textwrap
import time
import collections

import pygame
pygame.init()
from pygame.locals import *

sys.path.insert(0,os.path.join(os.getcwd(),'..'))
import lib.decorators
HOST, PORT = "localhost", 1987
SID = 127

class con(object):
    def __init__(self):
        
        self.incomingq = Queue.Queue(10) #read from sserver
        self.outgoingq= Queue.Queue(10) #headed to server
        self.is_connected=False
        
    def connect(self):
        # Create a socket (SOCK_STREAM means a TCP socket)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setblocking(1)
        # Connect to server and send data
        self.sock.connect((HOST, PORT))
        #send SuitSoftware version, first thing, size 16
        self.sock.send('lzr debug pygame')
        #send SID next
        self.sock.send(struct.pack('q',SID))
        
        self.w_thread = threading.Thread(target=self.write)
        self.w_thread.setDaemon(True)
        self.w_thread.start()
        self.r_thread = threading.Thread(target=self.handle)
        self.r_thread.setDaemon(True)
        self.r_thread.start()
        
        self.is_connected=True
        
    def close(self):
        self.sock.close()
        self.is_connected=False
        
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
class text_box(object):
    def __init__(self,**kwargs):
        self.options = Config(kwargs,
                              ['rect','pygame.Rect((0,0),(0,0))'],
                              ['font', 'pygame.font.Font(os.path.join(os.getcwd(),"data","fonts","freesansbold.ttf"), 12)'],
                              ['color', '(0,0,0)'],
                              ['max_lines', '-1'],
                              ['max_lines_mode', '"last_lines"'],#how to cut the lines, save the top $number or last $number
                              ['text', '"default text"'],
                              ['indent','""']
                             )
        self.debug = False
        self.__old_rect = self.options.rect
        
        self.textwraper=textwrap.TextWrapper()
        self.textwraper.initial_indent=''
        
        self.render()
    def render(self):
        self.textwraper.initial_indent=self.options.indent
        txt=[]
        line_num=0#what line we are on for the final output
        #split the text across new lines
        for index,text in enumerate(self.options.text.split('\n')):
            if len(text)==0:
                #our text is '', so skip it,
                ##TODO:: make this add a blank line
                temp_var=self.options.font.render(text,True,self.options.color).convert_alpha()
                #get the rect, we have to position it...
                rect=temp_var.get_rect()
                topleft=self.options.rect.topleft
                #set topleft postion
                topleft=(topleft[0],topleft[1]+(rect.height*line_num))
                rect.topleft=topleft
                line_num+=1
                #add to our list the current txt line...
                txt.append((temp_var,rect))
                
                continue
            #average letter size?
            let_size=(float(self.options.font.size(text)[0])/float(len(text)))
        
            #how big is our box?
            box_size=float(self.options.rect.width)
        
            #after how many letters must we wrap the line?
            wrap=box_size/let_size
        
            if self.debug==True:
                #print way too much info:letters per line (lpl), box width, and average letter size...
                print 'main::txt_box_render::lpl:%s   box_size:%s   letsize:%s\n>>>"%s"'%(wrap,box_size,let_size,text)
            #use the textwrap modual (yay for bateries included...)
            self.textwraper.width=int(wrap)
            for num,line in enumerate(self.textwraper.wrap(text)):
                #render a line of text
                temp_var=self.options.font.render(line,True,self.options.color).convert_alpha()
                #get the rect, we have to position it...
                rect=temp_var.get_rect()
                topleft=self.options.rect.topleft
                #set topleft postion
                topleft=(topleft[0],topleft[1]+(rect.height*line_num))
                rect.topleft=topleft
                line_num+=1
                #add to our list the current txt line...
                txt.append((temp_var,rect))
        #return a list of img's to blit and thier rects...
        self.txt_surf_list=txt
        
    def blit(self,screen,rect=None):
        if rect == None:
            rect = self.options.rect
        if rect != self.__old_rect:
            self.options.rect=rect
            self.render()
        for line in self.txt_surf_list:
            screen.blit(line[0],line[1])
        pygame.draw.rect(screen,(255,255,255),self.options.rect,1)
                
class Config(object):
    """ A utility for configuration """
    def __init__(self, options, *look_for):
        assertions = []
        for key in look_for:
            if key[0] in options.keys(): exec('self.'+key[0]+' = options[\''+key[0]+'\']')
            else: exec('self.'+key[0]+' = '+key[1])
            assertions.append(key[0])
        for key in options.keys():
            if key not in assertions: raise ConfigError(key+' not expected as option')
class logreader(object):
    def __init__(self):
        self.text=collections.deque([],25)
        self.txt_lock=threading.Lock()
        
        
    def get_text(self):
        with self.txt_lock:
            return tuple(self.text)
    def open(self):
        
        self.r_thread = threading.Thread(target=self.reader)
        self.r_thread.setDaemon(True)
        self.__running=True
        self.r_thread.start()
        
    def close(self):
        self.__running=False
        self.text=collections.deque([],25)
    def reader(self):
    
        def follow(thefile):
            #thefile.seek(0,2)      # Go to the end of the file
            while self.__running:
                line = thefile.readline()
                if not line:
                    time.sleep(0.1)    # Sleep briefly
                    continue
                yield line
            print "ending logreader"

        logfile = open(os.path.join(os.getcwd(),'..','lazertag.log'))
        loglines = follow(logfile)
        for line in loglines:
            with self.txt_lock:
                self.text.append(line)
def main():
    screen = pygame.display.set_mode((640, 480))
    
    suit=con()
    
    btn_connect=text_box(
                   rect=pygame.Rect((0,0),(64,64)),#top left, size 32x32
                   color=(255,255,255),
                   text='connect to server'
                       )
    btn_do_hit=text_box(
                   rect=pygame.Rect((64,0),(64,64)),
                   color=(255,255,255),
                   text='get hit'
                       )
    log_box   =text_box(
                   rect=pygame.Rect((0,64),(640,480-64)),
                   color=(255,255,255),
                   text='blank',
                   indent='    '
                       )
    log_reader=logreader()
    
    while True:
        pygame.time.wait(25)
        screen.fill((0, 0, 0))
        for event in pygame.event.get():
            if event.type == QUIT:
                suit.outgoingq.put(('dcon',json.dumps({'reason':'test over'})))
                pygame.time.wait(250)
                pygame.quit()
                return None
            elif event.type == MOUSEBUTTONDOWN and event.button==1:
                print 'click %s'%(event.pos,)
                #connect/disconnect
                if btn_connect.options.rect.collidepoint(event.pos):
                    if suit.is_connected:
                        print "closing server connection"
                        suit.close()
                        log_reader.close()
                        suit.is_connected=False
                        btn_connect.options.text='connect to server'
                        btn_connect.render()
                    else:
                        print "connecting"
                        suit.connect()
                        log_reader.open()
                        suit.is_connected=True
                        btn_connect.options.text='disconnect from server'
                        btn_connect.render()
                #send hit packet
                if btn_do_hit.options.rect.collidepoint(event.pos):
                    suit.outgoingq.put(('ghit',json.dumps({'weapon':'basic','team':'teamblu','from':7589})))
        screen.fill((0, 0, 0))
        
        btn_connect.blit(screen)
        btn_do_hit.blit(screen)
        #log list stuff
        log_list=''.join(log_reader.get_text())
        if log_list!=log_box.options.text:
            log_box.options.text=log_list
            log_box.render()
        log_box.blit(screen)
        pygame.display.flip()
if __name__=='__main__':
    main()