import logging
logger=logging.getLogger('lib.pluginloader')

import importlib
import os,sys
import traceback
import inspect
import types

import fs.osfs

import lib.common

import events

LocalPlugins = fs.osfs.OSFS(os.path.join(lib.common.curdir,"plugins"))
RemotePlugins = fs.osfs.OSFS(os.path.join(lib.common.curdir,"remote"))
MainModule = "__init__"
plugins=[]
def get_plugins(pdir,prefix):
    possibleplugins = pdir.listdir()
    for location in possibleplugins:
        if not pdir.isdir(location) or not MainModule + ".py" in pdir.listdir(location):
            continue
        if location.endswith(".py"):
            location=os.path.splitext(location)[0]
        yield {"name": "%s.%s"%(prefix,location)}

def load_plugin(plugin):
    '''TODO: change to importlib.SourceFileLoader()...
    this is to eventually support that a game is simply a load_plugins(gamedir) and overwrite 
    the current event tree/listener tree.
    '''
    logger.info('loading plugin "{plugin[name]}"'.format(plugin=plugin))
    pl = importlib.import_module("%s"%plugin['name'])
    if hasattr(pl,'onload'):
            pl.onload()
    return pl

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


def load_plugins():
    unload_plugins()
    for plugin in get_plugins(LocalPlugins,'plugins'):
        plugins.append(load_plugin(plugin))
    for plugin in get_plugins(RemotePlugins.opendir('remote'),'remote'):
        plugins.append(load_plugin(plugin))
    logger.info("plugins loaded")
    init_listeners()

def unload_plugins():
    global plugins
    plugins = []
    for plugin in [p for p in sys.modules.keys() if p.startswith(('plugins','remote'))]:
        try:
            p = sys.modules[plugin]
            if hasattr(p,"unload"):
                p.unload()
        except Exception as e:
            logger.critical("plugin '%s' failed unloading:%s"%(plugin,traceback.format_exc()))
        del sys.modules[plugin]


class remImporter:
    def __init__(self,remfs):
        self.remfs=remfs
    def find_module(self,fullname,package_path=None):
        if not fullname.startswith('remote'):
            #logger.debug("fail finding module '%s', not in plugpath"%fullname)
            return None
        if '.' in fullname:
            mod_parts = fullname.split('.')
            module_name = mod_parts[-1]
            package = '.'.join(mod_parts[:-1])
            path=fs.path.join(*mod_parts)
        else:
            package = None
            mod_parts=None
            module_name = fullname
            path=fullname
        if self.remfs.isdir(path):
            path = fs.path.join(path,'__init__.py')
        if self.remfs.exists(path+'.py'):
            path = path+'.py'

        # logger.debug("remImporter:pinfo:%s"%{
        #     "fullname":fullname,
        #     "mod_parts":mod_parts,
        #     "package":package,
        #     "package_path":package_path,
        #     "path":path,
        #     "module_name":module_name })
        
        if self.remfs.exists(path):
            return remLoader(self.remfs, module_name, package, mod_parts,path)
        return None

class remLoader:
    def __init__(self,remfs,module_name,package,mod_parts,path):
        self.remfs= remfs
        self.module_name=module_name
        self.package = package
        self.mod_parts=mod_parts
        self.path = path

    def load_module(self,fullname):
        with self.remfs.open(self.path) as f:
            code = f.read()
        newmod = types.ModuleType(fullname)
        sys.modules[fullname]=newmod
        newmod.__name__=fullname
        newmod.__file__="remfs://"+self.path
        newmod.__package__=None#TODO::: wat?
        newmod.__loader__=self
        newmod.__path__=['rempy://'+fullname] #this is what lets python.importlib know that we can do other imports...
        exec(code,newmod.__dict__)
        return newmod

sys.meta_path.append(remImporter(RemotePlugins))