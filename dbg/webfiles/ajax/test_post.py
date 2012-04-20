import pprint
import cgi
import json

def main(self):
    ctype, pdict = cgi.parse_header(self.headers.getheader('content-length'))
    self.send_response(200)
    self.end_headers()
    
    jdata = self.rfile.read(int(ctype))
    jdata = json.loads(jdata)
    
    self.wfile.write("<PRE>")
    pprint.pprint(jdata,stream=self.wfile)
    self.wfile.write("</PRE>")