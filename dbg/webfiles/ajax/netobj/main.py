

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
import Queue

import net

import __main__
if 'netobjs' not in __main__.debugdata:
    __main__.debugdata['netobjs']={}
def push(self):
    #called from auto_update.py
    
    #prep new options list based on the keys
    netlist =['<select onChange="netobj_update_data(this);">']
    for obj in __main__.debugdata['netobjs'].keys():
        netlist.append('<option>%s</option>'%obj)
    netlist.append('</select>')
    netlist = '\n'.join(netlist)
    
    #get current suit status, no matter what return, drop bad data with a error message if it occurs
    #first: get the current debug data object
    ##TODO::: get a setting from the settings dict that allows changing of the current debug object
    ##TODO::: each use of gathering new data should never run into the chance of coliding with other code access
    if __main__.debugdata['netobjs'].has_key(1337) and __main__.debugdata['netobjs'][1337].objtype == 'd':
        #we have the debug object, make the calls
        dobj = __main__.debugdata['netobjs'][1337] #simplify typing of the name (in case we need to change it)
        if __main__.debugdata['netobjs'].has_key('current'):
            dobj.outgoingq.put(('sget',{
                                        'oid':__main__.debugdata['netobjs']['current']
                                    
                                        }))
            ##im terrible, i do not check the returned status and check that it is really mine...
            try:
                status = dobj.incomingq.get(True,2.5)[1]
            except Queue.Empty:
                status = "status not returned in timeout limit"

        else:
            status = "no current object selected"
        
        
    else:
        status = "no debug object (create one with ID=1337)"
    
    
    
    
    
    jdata = {'netobjs':{'status':'<pre>'+pprint.pformat(status)+'</pre>',#get the status of the last selected suit
             'netlist':netlist
    }}
    
    #now we also push a new netobjs list
    ##pprint.pprint(jdata) debug line
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
                __main__.debugdata['netobjs'][oid].connect()
            elif jdata.has_key('change_netobj'):
                #select new netobj for viewing status of. currently just pprint the net.__dict__ until we get debug code server-side
                __main__.debugdata['netobjs']['current'] = int(jdata['change_netobj'])
                #write the current data so we dont wait on the push of data
                self.wfile.write('<pre>'+pprint.pformat(None)+'</pre>')
                
            #pprint.pprint(jdata,stream=self.wfile)
            
        
    else:
        print ctype
