'''
this is the heart of the main page, it will automatically be called by the page using a setTimeout() call

this allows us to push data to the user, most likly to be hit data, score updates, and the server log

'''
import json

import logreader
import __main__

def main(self):

    self.send_response(200)
    self.send_header('Content-type',    'text/plain')
    self.end_headers()
    if 'logreader' not in __main__.debugdata:
        pass
        
        __main__.debugdata['logreader']=logreader.logreader()
    if     __main__.debugdata['logreader']._running:
        self.wfile.write(json.dumps({
        "log_update": {"text":__main__.debugdata['logreader'].get_text()}
        
        }))
    else:
        self.wfile.write(json.dumps({'no_data':None}))