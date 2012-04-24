

main_content = '''<form method='POST' enctype='multipart/form-data' action='/ajax/netobj/main.py' onsubmit="netobj_post(this,'newobj'); return false;">
<input type="text" name="OID" value="9001" size="20"> </Input> 
<br />
<input type="text" name="objtype" maxlength="1" value="s" size="20"> </Input> 
<br />
<input type=submit value="send" >new settings</Input>
</form>
<div id="netobj_form"><!-- select netobj to view, updated via the pushes of auto_update.js -->


</div>
<div id="netobj_data">



</div>

''' #note: use str.format() to finnish before sending to client

buttons = '''<div class="option1" > <button type="button" onclick="netobj_update_data()">update data</button></div>
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
def push(self):
    #called from auto_update.py
    
    #prep new options list based on the keys
    netlist =['asdf<select name="netobj_select" onChange="netobj_update_data();>']
    for obj in __main__.debugdata['netobjs'].keys():
        netlist.append('<option>%s</option>'%obj)
    netlist.append('</select>asdf')
    netlist = '\n'.join(netlist)
    
    
    jdata = {'netobjs':{'status':'<pre>'+pprint.pformat({'asdf':None})+'</pre>',#get the status of the last selected suit
             'netlist':netlist
    }}
    
    #now we also push a new netobjs list
    pprint.pprint(jdata)
    self.wfile.write(json.dumps(jdata))
    
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
            elif jdata.has_key('change_netobj'):
                #select new netobj for viewing status of. currently just pprint the net.__dict__ until we get debug code server-side
                __main__.debugdata['netobjs']['current'] = int(jdata['change_netobj'])
                #write the current data so we dont wait on the push of data
                self.wfile.write('<pre>'+pprint.pformat(None)+'</pre>')
                
            #pprint.pprint(jdata,stream=self.wfile)
            
        
    else:
        print ctype