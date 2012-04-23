

main_content = '''<form method='POST' enctype='multipart/form-data' action='/ajax/settings/main.py' onsubmit="settings_post(this,'net'); return false;">
<input type="text" name="host_ip" value="{host}" size="20"> </Input> 
<br />
<input type="text" name="host_port" value="{port}" size="20"> </Input> 
<br />
<input type="text" name="logname" value="{logname}" size="20"> </Input> 
<br />
<input type=submit value="send" >new settings</Input>''' #note: use str.format() to finnish before sending to client

buttons = '''<div class="option1" > <button type="button" onclick="settings_update_form()">update FORM </button></div>
    <div class="option2" > <button type="button" onclick="settings_reset_form()"> reset FORM  </button></div>
    <div class="option1"> option 3 </div>
    <div class="option2"> option 4 </div>'''
    
import cgi
import json
import pprint
import net
import logreader

def main(self):
    ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
    if ctype == 'application/json':
        length, pdict = cgi.parse_header(self.headers.getheader('content-length'))
        self.send_response(200)
        self.send_header('Content-type',    'text/plain')
        self.end_headers()
        jdata = self.rfile.read(int(length))
        jdata = json.loads(jdata)
        
        if jdata == u"get buttons":
            self.wfile.write(buttons)
        elif jdata == u"get form":
            self.wfile.write(main_content.format(host=net.HOST,port=net.PORT,logname=logreader.logfile))
            
        elif type(jdata) == dict:
            #we have more than the normal use, most likely we have button presses :D
            if jdata.has_key('button'):
                print jdata['button'] #placeholder, send the button to the server console
                
            if jdata.has_key('type') and jdata['type'] == u'post net form':
                #we have gotten a post from the client asking to update the server settings
                net.HOST = jdata['host_ip']
                net.PORT = int(jdata['host_port'])
                logreader.logfile=jdata['logname']
            pprint.pprint(jdata,stream=self.wfile)
    else:
        print ctype