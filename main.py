print "hi!"

import coms

def main():
    playerlist = coms.player.find()
    p=playerlist[0] #start with one player for now
    print p.stats


if __name__ == '__main__':
    main()
