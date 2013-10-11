
import pygame
pygame.init()
from pygame.locals import *

#define early so that others can import it
SID = 127


from net import con
from gui import text_box
from logreader import logreader



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
    btn_do_ping=text_box(
                   rect=pygame.Rect((128,0),(64,64)),
                   color=(255,255,255),
                   text='ping server'
                        )
    log_box   =text_box(
                   rect=pygame.Rect((0,64),(640,480-64)),
                   color=(255,255,255),
                   text='blank',
                   indent='    '
                       )
    log_reader=logreader()
    
    while True:
        pygame.time.wait(100)
        screen.fill((0, 0, 0))
        for event in pygame.event.get():
            if event.type == QUIT:
                suit.outgoingq.put(('dcon',json.dumps({'reason':'test over'})))
                pygame.time.wait(250)
                pygame.quit()
                return None
            elif event.type == MOUSEBUTTONDOWN and event.button==1:
                print(('click %s'%(event.pos,)))
                #connect/disconnect
                if btn_connect.options.rect.collidepoint(event.pos):
                    if suit.is_connected:
                        print("closing server connection")
                        suit.close()
                        log_reader.close()
                        suit.is_connected=False
                        btn_connect.options.text='connect to server'
                        btn_connect.render()
                    else:
                        print("connecting")
                        suit.connect()
                        suit.outgoingq.put(('stup',{'arena':1}))
                        log_reader.open()
                        suit.is_connected=True
                        btn_connect.options.text='disconnect from server'
                        btn_connect.render()
                #send hit packet
                if btn_do_hit.options.rect.collidepoint(event.pos):
                    suit.outgoingq.put(('ghit',{'weapon':'basic','team':'teamblu','from':7589}))
                elif btn_do_ping.options.rect.collidepoint(event.pos):
                    suit.outgoingq.put(('ping',{'pingdata':'randomstring','team':'teamblu','from':7589}))
        screen.fill((0, 0, 0))
        
        btn_connect.blit(screen)
        btn_do_hit.blit(screen)
        btn_do_ping.blit(screen)
        #log list stuff
        log_list=''.join(log_reader.get_text())
        if log_list!=log_box.options.text:
            log_box.options.text=log_list
            log_box.render()
        log_box.blit(screen)
        pygame.display.flip()
if __name__=='__main__':
    main()