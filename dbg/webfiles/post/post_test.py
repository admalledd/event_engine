import pprint
import cgi
def main(self):
    '''returns all data posted to the file, good way to check what the server thinks it is getting'''
    ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
    if ctype == 'multipart/form-data':
        self.query=cgi.parse_multipart(self.rfile, pdict)
    self.send_response(200)
    self.end_headers()
    self.wfile.write("<HTML>\r\n<BODOY>POST OK.<BR><BR> <PRE>")
    pprint.pprint(self.query,stream=self.wfile)
    self.wfile.write("</PRE></BODY></HTML>")