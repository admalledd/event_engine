#import coms
import threading
import time
import random


l={'l':[]}
def main():
    playerlist = coms.player.find()
    p=playerlist[0] #start with one player for now
    print p.stats

    
def target():
    i=0
    while True:
        time.sleep(0.025)
        l['l'].append(i)
        i+=1
def test():
    t=threading.Thread(target=target)
    t.daemon=True
    t.start()
    time.sleep(0.5)
    while True:
        for k in enumerate(l['l']):
            print k,len(l['l'])
            time.sleep(.02)
        l['l'] =[]
        time.sleep(0.1)
    
if __name__ == '__main__':
    test()
