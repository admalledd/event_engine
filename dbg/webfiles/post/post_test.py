def main(self,query):
    self.wfile.write("<HTML>\r\n<BODOY>POST OK.<BR><BR>")
    self.wfile.write(query.get('upfile'))
    self.wfile.write(query.get('rd_button'))
    self.wfile.write(query.get('text_box'))
    self.wfile.write("</BODY></HTML>")