import logging
logger=logging.getLogger('lib.pluginloader')

import importlib
import os,sys
import traceback

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
        if location.endswith(".py"):
            location=os.path.splitext(location)[0]
        yield {"name": "plugins.%s"%location}

def load_plugin(plugin):
    return importlib.import_module("%s"%plugin['name'])

def load_plugins():
    global plugins
    plugins=[]
    for plugin in get_plugins():
        logger.info('loading plugin "{plugin[name]}"'.format(plugin=plugin))
        plugins.append(load_plugin(plugin))

def unload_plugins():
    global plugins
    for plugin in [p for p in sys.modules.keys() if p.startswith('plugins')]:
        try:
            p = sys.modules[plugin]
            if hasattr(p,"unload"):
                p.unload()
        except Exception as e:
            logger.critical("plugin '%s' failed unloading:%s"%(plugin,traceback.format_exc()))
        del sys.modules[plugin]