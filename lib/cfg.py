import configparser
import lib.common

import os

#normally, config's are added via the lib.cfg.add() function
#however, here we must have the main cfg open early to set logfilename
#just trust that we can use os.getcwd() for this...
main=configparser.ConfigParser()
main.read(os.path.join(os.getcwd(),'config.ini'))
