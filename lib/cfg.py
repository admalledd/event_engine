import lib.configobj as cj
import lib.common
from lib import logger

import os

abs = cj.ConfigObj(os.path.join(lib.common.curdir,'abs','config.ini'))
logger.debug('server config opened and loaded')

