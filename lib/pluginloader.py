import logging
logger=logging.getLogger('lib.pluginloader')

import importlib
import os,sys
import traceback
import inspect

import fs.osfs

import lib.common

import events

PluginFolder = fs.osfs.OSFS(os.path.join(lib.common.curdir,"plugins"))
MainModule = "__init__"
plugins=[]
def get_plugins(pdir):
    possibleplugins = pdir.listdir()
    for location in possibleplugins:
        if not pdir.isdir(location) or not MainModule + ".py" in pdir.listdir(location):
            continue
        if location.endswith(".py"):
            location=os.path.splitext(location)[0]
        yield {"name": "plugins.%s"%location}

def load_plugin(plugin):
    '''TODO: change to importlib.SourceFileLoader()...
    this is to eventually support that a game is simply a load_plugins(gamedir) and overwrite 
    the current event tree/listener tree.
    '''
    return importlib.import_module("%s"%plugin['name'])

def init_listeners():
    logger.info("init_listeners")
    for event_name in events.listeners:
        for priority in events.listeners[event_name]:
            p=[]
            for listener in events.listeners[event_name][priority]:
                logger.debug("init listener:%s"%listener)
                if inspect.isclass(listener):
                    p.append(listener())
                else:
                    p.append(listener)
            events.listeners[event_name][priority]=p


def load_plugins(pdir=PluginFolder):
    unload_plugins(pdir)
    for plugin in get_plugins(pdir):
        logger.info('loading plugin "{plugin[name]}"'.format(plugin=plugin))
        plugins.append(load_plugin(plugin))
        if hasattr(plugins[-1],'onload'):
            plugins[-1].onload()
    logger.info("plugins loaded")
    init_listeners()

def unload_plugins(pdir=PluginFolder):
    global plugins
    plugins = []
    for plugin in [p for p in sys.modules.keys() if p.startswith('plugins')]:
        try:
            p = sys.modules[plugin]
            if hasattr(p,"unload"):
                p.unload()
        except Exception as e:
            logger.critical("plugin '%s' failed unloading:%s"%(plugin,traceback.format_exc()))
        del sys.modules[plugin]