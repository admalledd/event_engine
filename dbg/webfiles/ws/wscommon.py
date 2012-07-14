
import hashlib
import base64
import struct
import socket


# Frame opcodes defined in the spec.
OPCODE_CONTINUATION = 0x0
OPCODE_TEXT = 0x1
OPCODE_BINARY = 0x2
OPCODE_CLOSE = 0x8
OPCODE_PING = 0x9
OPCODE_PONG = 0xa

# UUIDs used by HyBi 04 and later opening handshake and frame masking.
WEBSOCKET_ACCEPT_UUID = '258EAFA5-E914-47DA-95CA-C5AB0DC85B11'


class websocket(object):
    def __init__(self,handler):
        '''called on the loading/creation of a WebSocket. this class does
        the handshake as well as the de-masking of the client data.

        handler is a instance of webserv.py:MyHandler (so that we can get connection and config info)
        '''
        self.handler=handler
        self.success = self.handshake()


    def handshake(self):
        '''try to negotiate for a WebSocket Protocol change, also check for valid headers. if 
        the headers are not corret then return a 405 (Method not allowed)'''

        if self.handler.headers.get('Connection').lower() == 'keep-alive, upgrade' and \
                self.handler.headers.get('Upgrade').lower() == 'websocket':
            
            #request headers are valid, send response
            #origin = self.handler.headers.get('Origin')##TODO: use the origin headers for safety
            key = self.handler.headers.get('Sec-WebSocket-key')
            ##print origin,key
            #send headers
            self.handler.send_response(101, "Web Socket Protocol Handshake")
            self.handler.send_header('Upgrade',     'WebSocket')
            self.handler.send_header('Connection',  'Upgrade')
            #self.handler.send_header('WebSocket-Origin','http://localhost:8081')#TODO: use the origin from the headers
            #self.handler.send_header('WebSocket-Location','ws://localhost:8081/ws/ws.py')

            newkey = base64.b64encode(hashlib.sha1(key+'258EAFA5-E914-47DA-95CA-C5AB0DC85B11').digest())
            self.handler.send_header('Sec-WebSocket-Accept',newkey)


            self.handler.end_headers()
            print 'handshake complete'
            return True
        else:
            self.handler.send_response(405, 'not a WebSocket Upgrade request')
            return False

    def create_length_header(self,length, mask):
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

    def send_data(self,payload, opcode=0x1):
        '''short cut for sending data to the socket.'''
        self.handler.connection.send(self.create_header(opcode,len(payload))+payload)

    def create_header(self,opcode, payload_length, fin=1, rsv1=0, rsv2=0, rsv3=0, mask=False):
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
        header += self.create_length_header(payload_length, mask)

        return header