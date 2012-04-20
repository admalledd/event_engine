#!/usr/bin/python

'''
web front end to the debug session data for the lazer tag server. has the capability for more flexable debug tools over the old method

note that this is copied from an old dynamic webserver project, minimal cleaning has taken place. more is recomended.


'''
import string,cgi,time,os,sys
import os
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import imp
import traceback

import magic #acess lib magic for MIME types

mimer = magic.Magic(mime=True)

#note that fs is from python filesystem (easy_install fs), I only have it installed on pypy
import fs.osfs
webfiles = fs.osfs.OSFS(os.path.join(os.getcwd(),'webfiles'))

class MyHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        BaseHTTPRequestHandler.log_message(self, format, *args)
        
    def realfile(self):
        rawdata = webfiles.getcontents(self.path) #if we are here we assume the file exists, therefor we can read the contents like this
        ##TODO: handle buffering so that we dont try to read a 4 gig file and choke on the RAM usage
        
        #find mimetype of file
        mime = mimer.from_buffer(rawdata)
        #send headers
        self.send_response(200)
        self.send_header('Content-type',mime)
        self.end_headers()
        self.wfile.write(rawdata)
        
    def pyfile(self):
        self.send_response(200)#yes, we are forcing the use of these headers, might be better to have a normal convieniance function then...
        self.send_header('Content-type',    'text/html')
        self.end_headers()
        try:
            modual = imp.load_source('', os.path.join(os.getcwd(),'webfiles',self.path[1:]))

            modual.main(self)
        except:
            self.wfile.write('<HTML><BODY><PRE>\n\n')
            self.wfile.write("Exception in user code:\n")
            self.wfile.write(str('-'*60)+'\n\n')
            traceback.print_exc(file=self.wfile)
            self.wfile.write(str('-'*60)+'\n\n')
            self.wfile.write('\n\n</HTML></BODY></PRE>\n')
        
    def is_webfile(self,path=None):
        '''called only after the args have been parsed from self.path
        checks if the file is on disk, and in a real area on disk at that.
        
        '''
        if path == None: path=self.path #allow calls using self.is_webfile(path) or use self.path
        return webfiles.exists(path)
        
    def do_GET(self):
        try:
            if '?' in self.path:
                #we have some url parsing to do, split that other stuff into raw data...
                self.path,self.path_args = self.path.split('?',1)
                ##todo: parse the args down even more into usable data chunks. ignore for now
                
                
            if self.path.endswith('/'): #handle index of a directory with this
                
                #check for index.py, then try index.html, if none work, 404
                
                #test index.py
                if self.is_webfile(self.path+'index.py'):
                    self.path=self.path+'index.py'
                    self.pyfile()
                    return
                #test index.html
                elif self.is_webfile(self.path+'index.html'):
                    self.path=self.path+'index.html'
                    self.realfile()
                    return
                #no matches, we fall through to 404
            
            elif self.path.endswith('.py') and self.is_webfile(): #python dynamic code?
                self.pyfile()
                return
                
            elif self.is_webfile(): #final chance at returning a file, check for a real file called self.path
                self.realfile()
                return
                
            self.send_error(404,'File Not Found: %s' % self.path)
            return
                
        except IOError:
            self.send_error(404,'File Not Found: %s' % self.path)
     

    def do_POST(self):
        try:
            ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
            if ctype == 'multipart/form-data':
                query=cgi.parse_multipart(self.rfile, pdict)
            self.send_response(200)#POST OK
            self.end_headers()
            try:
                modual = imp.load_source('', os.path.join(os.getcwd(),'webfiles',self.path[1:]))
                modual.main(self,query)
            except:
                self.wfile.write('<HTML><BODY><PRE>\n\n')
                self.wfile.write("Exception in user code:\n")
                self.wfile.write(str('-'*60)+'\n\n')
                traceback.print_exc(file=self.wfile)
                
                self.wfile.write(str('-'*60)+'\n\n')
                self.wfile.write('path::%s'%self.path)
                self.wfile.write('\n\n</HTML></BODY></PRE>\n')
            
                return
        except :
            pass

PORT = 8081
welcome='''\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/
httpserver started on port: %i
\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/
''' % (PORT)

def main():
    import time
    time.sleep(0.1)
    server = HTTPServer(('', PORT), MyHandler)
    print welcome
    server.serve_forever()
if __name__ == '__main__':
    main()

