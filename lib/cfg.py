import lib.configobj as cj
import lib.common
from lib import logger

import os

server = cj.ConfigObj(os.path.join(lib.common.curdir,'config.ini'))
logger.debug('server config opened and loaded')

abs_suit = cj.ConfigObj(os.path.join(lib.common.curdir,'abs','cfg','suit.ini'))
logger.debug('abs.suit config opened and loaded')
