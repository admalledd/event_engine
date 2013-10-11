import logging
logger=logging.getLogger('lib.pluginloader')

import imp
import os

import fs.osfs

import lib.common

PluginFolder = fs.osfs.OSFS(os.path.join(lib.common.curdir,"plugins"))
MainModule = "__init__"
plugins=[]
def get_plugins():
    possibleplugins = PluginFolder.listdir()
    for location in possibleplugins:
        if not PluginFolder.isdir(location) or not MainModule + ".py" in PluginFolder.listdir(location):
            continue
        info = imp.find_module(MainModule, [PluginFolder.getsyspath(location)])
        yield {"name": location, "info": info}

def load_plugin(plugin):
    return imp.load_module("plugins.%s"%plugin['name'], *plugin["info"])

def load_plugins():
    global plugins
    plugins=[]
    for plugin in get_plugins():
        #logger.debug("loading plugin {plugin[name]} from {plugin[info][1]}".format(plugin=plugin))
        logger.debug('loading plugin "{plugin[name]}"'.format(plugin=plugin))
        plugins.append(imp.load_module("plugins.%s"%plugin['name'], *plugin["info"]))