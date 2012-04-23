'''
due to lib magic  not supporting some basic file types, we use thise loader to 
force the correct content-type header

'''
import os
import __main__ #for webfiles
def main(self):
    #ok, first thing we do is check for a real file from the self.path_args
    if not self.is_webfile(self.path_args):
        self.send_error(404,'File Not Found: %s' % self.path_args)
        return
    
    #find mimetype of file using the suffix (i know this is a bad idea...)
    mimetypes={
        '.js':'application/javascript',
        '.css':'text/css'
    }
    if os.path.splitext(self.path_args)[1] not in mimetypes:
        self.send_error(404,'File Not supported by loader.py: %s ::: %s' % (self.path_args,os.path.splitext(self.path_args)[1]))
        return
    mime = mimetypes[os.path.splitext(self.path_args)[1]]
    #send headers
    self.send_response(200)
    self.send_header('Content-type',mime)
    self.end_headers()
    rawdata = __main__.webfiles.getcontents(self.path_args) #if we are here we assume the file exists, therefor we can read the contents like this
    ##TODO: handle buffering so that we dont try to read a 4 gig file and choke on the RAM usage
    self.wfile.write(rawdata)