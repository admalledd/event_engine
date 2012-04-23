

buttons = '''<div class="option1" > <button type="button" onclick="test_POST()">test POST </button></div>
    <div class="option2" > <button type="button" onclick="test_GET()"> test GET  </button></div>
    <div class="option1"> option 3 </div>
    <div class="option2"> option 4 </div>'''
    
import cgi
import json

def main(self):
    ctype, pdict = cgi.parse_header(self.headers.getheader('content-length'))
    self.send_response(200)
    self.send_header('Content-type',    'text/plain')
    self.end_headers()
    
    jdata = self.rfile.read(int(ctype))
    jdata = json.loads(jdata)
    
    if jdata == u"get buttons":
        self.wfile.write(buttons)
    
    elif type(jdata) == dict:
        #we have more than the normal use, most likely we have button presses :D
        if jdata.has_key('button'):
            print jdata['button'] #placeholder, send the button to the server console