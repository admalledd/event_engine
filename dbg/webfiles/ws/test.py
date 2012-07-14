import time
import imp
import __main__

wscommon      = imp.load_source('', __main__.webfiles.getsyspath('/ws/wscommon.py'))

def main(self):
    ws=wscommon.websocket(self)
    if not ws.success:
        #handshake failed, and we already sent a error document out
        return
    if self.path_args == 'con1':
        time.sleep(1)
        ws.send_data('hello'+self.path_args)
        #self.connection.send('hello')
        #self.connection.flush()
        time.sleep(1)
        ws.send_data('world'+self.path_args)
        #self.connection.send('world')
        #self.connection.flush()
        time.sleep(1)
    elif self.path_args == 'con2':
        #self.connection.settimeout(2.5)
        print repr(self.connection.recv(128))
        ws.send_data('con2 data gotten')
    ws.send_data('',0x8)
    print 'done with Socket'