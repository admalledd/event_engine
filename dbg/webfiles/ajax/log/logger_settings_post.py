import pprint
import cgi
import json

import logreader
import __main__
def main(self):
    ctype, pdict = cgi.parse_header(self.headers.getheader('content-length'))
    self.send_response(200)
    self.send_header('Content-type',    'text/plain')
    self.end_headers()
    
    jdata = self.rfile.read(int(ctype))
    jdata = json.loads(jdata)
    if jdata == u"open log":
        __main__.debugdata['logreader']=logreader.logreader()
        if __main__.debugdata['logreader']._running:
            self.wfile.write("log already open")
        else:
            __main__.debugdata['logreader'].open()
            self.wfile.write("opened log")
    
    elif jdata == u"close log":
        #if 'logreader' not in __main__.debugdata:
        __main__.debugdata['logreader']=logreader.logreader()
        if not __main__.debugdata['logreader']._running:
            self.wfile.write("log already closed")
        else:
            __main__.debugdata['logreader'].close()
            self.wfile.write("closed log")