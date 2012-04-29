'''
this is the heart of the main page, it will automatically be called by the page using a setTimeout() call

this allows us to push data to the user, most likly to be hit data, score updates, and the server log

'''
import json

import logreader

import __main__

import imp #use imp to force a recompile of the source

aj_main     = imp.load_source('', __main__.webfiles.getsyspath('/ajax/main/main.py'))
aj_netobj   = imp.load_source('', __main__.webfiles.getsyspath('/ajax/netobj/main.py'))
aj_settings = imp.load_source('', __main__.webfiles.getsyspath('/ajax/settings/main.py'))
aj_log      = imp.load_source('', __main__.webfiles.getsyspath('/ajax/log/main.py'))
def main(self):

    self.send_response(200)
    self.send_header('Content-type',    'application/json')
    self.end_headers()
    if 'logreader' not in __main__.debugdata:
        __main__.debugdata['logreader']=logreader.logreader()
    if  __main__.debugdata['logreader']._running:
        self.wfile.write(json.dumps({
        "log_update": {"text":__main__.debugdata['logreader'].get_text()}
        
        }))
        return
    
    #ok, so now we are going to check the self.path_args and see if it has changed, if so, push anything relevent, and then start calling the autoupdate of that page
    if self.path_args in ('','undefined','Index') :
        #default landing page, push the user to #main
        jdata={'layout_update':{
                               "maincontent": "main content PUSH updated using auto_update.js",
                               "optionbar":aj_main.buttons,
                               "newpath":"#main",
                               "reason":"landing page PUSH"
                               }
        
        
              }
        self.wfile.write(json.dumps(jdata))
        return
    elif self.path_args == 'NetObjects':
        #time to run the netobj PUSH update code:
        print "running dyncode of Netobjects"
        aj_netobj.push(self)
        return
    else:
        self.wfile.write(json.dumps({'no_data':None}))