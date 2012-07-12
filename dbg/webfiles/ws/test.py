import time
import hashlib
import base64
import struct

def create_length_header(length, mask):
    """Creates a length header.

    Args:
        length: Frame length. Must be less than 2^63.
        mask: Mask bit. Must be boolean.

    Raises:
        ValueError: when bad data is given.
    """

    if mask:
        mask_bit = 1 << 7
    else:
        mask_bit = 0

    if length < 0:
        raise ValueError('length must be non negative integer')
    elif length <= 125:
        return chr(mask_bit | length)
    elif length < (1 << 16):
        return chr(mask_bit | 126) + struct.pack('!H', length)
    elif length < (1 << 63):
        return chr(mask_bit | 127) + struct.pack('!Q', length)
    else:
        raise ValueError('Payload is too big for one frame')

def create_header(opcode, payload_length, fin=1, rsv1=0, rsv2=0, rsv3=0, mask=False):
    """Creates a frame header.

    Raises:
        Exception: when bad data is given.
    """

    if opcode < 0 or 0xf < opcode:
        raise ValueError('Opcode out of range')

    if payload_length < 0 or (1 << 63) <= payload_length:
        raise ValueError('payload_length out of range')

    if (fin | rsv1 | rsv2 | rsv3) & ~1:
        raise ValueError('FIN bit and Reserved bit parameter must be 0 or 1')

    header = ''

    first_byte = ((fin << 7)
                  | (rsv1 << 6) | (rsv2 << 5) | (rsv3 << 4)
                  | opcode)
    header += chr(first_byte)
    header += create_length_header(payload_length, mask)

    return header
def send_data(payload,connection, opcode=0x1):
    connection.send(create_header(opcode,len(payload))+payload)

def handshake(self):
    '''try to negotiate for a WebSocket Protocol change, also check for valid headers. if 
    the headers are not corret then return a 405 (Method not allowed)'''

    if self.headers.get('Connection').lower() == 'keep-alive, upgrade' and \
            self.headers.get('Upgrade').lower() == 'websocket':
        
        #request headers are valid, send response
        #origin = self.headers.get('Origin')##TODO: use the origin headers for safety
        key = self.headers.get('Sec-WebSocket-key')
        ##print origin,key
        #send headers
        self.send_response(101, "Web Socket Protocol Handshake")
        self.send_header('Upgrade',     'WebSocket')
        self.send_header('Connection',  'Upgrade')
        #self.send_header('WebSocket-Origin','http://localhost:8081')#TODO: use the origin from the headers
        #self.send_header('WebSocket-Location','ws://localhost:8081/ws/ws.py')

        newkey = base64.b64encode(hashlib.sha1(key+'258EAFA5-E914-47DA-95CA-C5AB0DC85B11').digest())
        self.send_header('Sec-WebSocket-Accept',newkey)


        self.end_headers()
        return True
    else:
        self.send_response(405, 'not a WebSocket Upgrade request')
        return False

def main(self):
    if not handshake(self):
        #handshake failed, and we already sent a error document out
        return

    time.sleep(1)
    send_data('hello'+self.path_args,self.connection)
    #self.connection.send('hello')
    #self.connection.flush()
    time.sleep(1)
    send_data('world'+self.path_args,self.connection)
    #self.connection.send('world')
    #self.connection.flush()
    time.sleep(1)
    send_data('',self.connection,0x8)
    print 'done with Socket'