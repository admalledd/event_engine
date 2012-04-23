import __main__
def main(self):
    self.send_html_header()
    self.wfile.write('<HTML><BODY><PRE>\n\n')
    if 'bad-idea' not in __main__.debugdata:
        __main__.debugdata['bad-idea']=0
    __main__.debugdata['bad-idea'] += 1
    self.wfile.write('current hit count: %s\n'%__main__.debugdata['bad-idea'])
    self.wfile.write('\n\n</HTML></BODY></PRE>\n')
    