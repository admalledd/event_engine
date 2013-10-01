import time
import imp
import __main__
import socket

#use imp.load_source to force reloading of the code in this file making testing faster (no restarting)
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
        try:
            frame = ws.get_frame()
            print(frame)
            ws.send_data('con2 data gotten:%r'%frame.payload)
        except socket.timeout:
            print('con2 timeout')
    ws.close()
    print('done with Socket')