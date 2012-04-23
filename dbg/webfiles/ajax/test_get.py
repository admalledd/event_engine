import pprint
import time

def main(self):
    self.send_html_header()
    self.wfile.write("<PRE>")
    pprint.pprint(str(time.time()),stream=self.wfile)
    self.wfile.write("</PRE>")