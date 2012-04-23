

main_content = '''<form method='POST' enctype='multipart/form-data' action='/ajax/netobj/main.py' onsubmit="netobj_post(this,'newobj'); return false;">
<input type="text" name="OID" value="9001" size="20"> </Input> 
<br />
<input type="text" name="objtype" maxlength="1" value="s" size="20"> </Input> 
<br />
<input type=submit value="send" >new settings</Input>''' #note: use str.format() to finnish before sending to client

buttons = '''<div class="option1" > <button type="button" onclick="netobj_update_form()">update FORM </button></div>
    <div class="option2" > <button type="button" onclick="netobj_reset_form()"> reset FORM  </button></div>
    <div class="option1"> option 3 </div>
    <div class="option2"> option 4 </div>'''
    
import cgi
import json
import pprint
import net

import __main__
if 'netobjs' not in __main__.debugdata:
    __main__.debugdata['netobjs']={}

def main(self):
    ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
    if ctype == 'application/json':
        length, pdict = cgi.parse_header(self.headers.getheader('content-length'))
        self.send_response(200)
        self.send_header('Content-type',    'text/plain')
        self.end_headers()
        jdata = json.loads(self.rfile.read(int(length)))
        
        if jdata == u"get buttons":
            self.wfile.write(buttons)
        elif jdata == u"get form":
            self.wfile.write(main_content.format(host=net.HOST,port=net.PORT))
            
        elif type(jdata) == dict:
            if jdata.has_key('type') and jdata['type'] == u'newobj':
                #we have gotten a post from the client asking to make a new netobject
                oid=int(jdata['oid'])
                objtype=jdata['objtype']
                if len(objtype) > 1:
                    return #bail out, objtype was a illegal value
                __main__.debugdata['netobjs'][oid] = net.con(oid,objtype)
            pprint.pprint(jdata,stream=self.wfile)
    else:
        print ctype