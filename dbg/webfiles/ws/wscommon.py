
import hashlib
import base64
import struct
import socket
import array

# Frame opcodes defined in the spec.
OPCODE_CONTINUATION = 0x0
OPCODE_TEXT = 0x1
OPCODE_BINARY = 0x2
OPCODE_CLOSE = 0x8
OPCODE_PING = 0x9
OPCODE_PONG = 0xa

WEBSOCKET_ACCEPT_UUID = '258EAFA5-E914-47DA-95CA-C5AB0DC85B11'

class frame(object):

    def __init__(self, fin=1, rsv1=0, rsv2=0, rsv3=0,opcode=None, payload=''):
        '''opcode is set to None to force an error if something uses this without preperation'''
        self.fin = fin
        self.rsv1 = rsv1
        self.rsv2 = rsv2
        self.rsv3 = rsv3
        self.opcode = opcode
        self.payload = payload
    def __str__(self):
        'for printing'
        return 'FRAME: fin=%s, rsv1=%s, rsv2=%s, rsv3=%s,opcode=%s, payload=%r'%(self.fin, self.rsv1, self.rsv2, 
                                                                                 self.rsv3, self.opcode ,self.payload)

class websocket(object):
    def __init__(self,handler):
        '''called on the loading/creation of a WebSocket. this class does
        the handshake as well as the de-masking of the client data.

        handler is a instance of webserv.py:MyHandler (so that we can get connection and config info)
        '''
        self.handler=handler
        self.success = self.handshake()

    #short helpers first, because they are an easy intro to the stuff here
    def close(self,message=''):
        '''send close frame, with optional message. must not fragment due to message'''
        self.send_data(message,OPCODE_CLOSE)

    def send_data(self,payload, opcode=OPCODE_TEXT):
        '''short cut for sending data to the socket.'''
        self.handler.connection.send(self.create_header(opcode,len(payload))+payload)

    #advanced helpers
    def handshake(self):
        '''try to negotiate for a WebSocket Protocol change, also check for valid headers. if 
        the headers are not corret then return a 405 (Method not allowed)'''

        if self.handler.headers.get('Connection').lower() == 'keep-alive, upgrade' and \
                self.handler.headers.get('Upgrade').lower() == 'websocket':
            
            #request headers are valid, send response
            #origin = self.handler.headers.get('Origin')##TODO: use the origin headers for safety
            key = self.handler.headers.get('Sec-WebSocket-key')
            #send headers
            self.handler.send_response(101, "Web Socket Protocol Handshake")
            self.handler.send_header('Upgrade',     'WebSocket')
            self.handler.send_header('Connection',  'Upgrade')
            #self.handler.send_header('WebSocket-Origin','http://localhost:8081')#TODO: use the origin from the headers
            #self.handler.send_header('WebSocket-Location','ws://localhost:8081/ws/ws.py')

            newkey = base64.b64encode(hashlib.sha1(key+WEBSOCKET_ACCEPT_UUID).digest())
            self.handler.send_header('Sec-WebSocket-Accept',newkey)


            self.handler.end_headers()
            return True
        else:
            self.handler.send_response(405, 'not a WebSocket Upgrade request')
            return False

    #now down to stuff that should not really be run by normal users (frame building)
    def create_header(self,opcode, payload_length, fin=1, rsv1=0, rsv2=0, rsv3=0, mask=False):
        """Creates a frame header. http://tools.ietf.org/html/rfc6455#section-5.2 """

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

    def create_length_header(self,length, mask):
        """Creates a length header."""

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

    #have to read that data in somewhere
    def receive_bytes(self, length):
        """Receives multiple bytes. Retries read when we couldn't receive the specified amount."""

        allbytes = []
        while length > 0:
            new_bytes = self.handler.connection.recv(length)
            if not new_bytes:
                raise socket.error(
                'Receiving %d byte failed. Peer (%r) closed connection' %
                (length, (self.handler.connection.remote_addr,)))
            allbytes.append(new_bytes)
            length -= len(new_bytes)
        
        return ''.join(allbytes)

    #the meat of the object, decoding of client to server frames.
    def get_frame(self):
        """Parses a frame. Returns a frame object containing all relevent frame info
        lots of randome bit fiddling magic going on, have http://tools.ietf.org/html/rfc6455#section-5.3
        open near by for refrence please :D

        needs testing for large frames, it is unknown if they will break things due to size

        """
        received = self.receive_bytes(2)
        first_byte = ord(received[0])
        fin = (first_byte >> 7) & 1
        rsv1 = (first_byte >> 6) & 1
        rsv2 = (first_byte >> 5) & 1
        rsv3 = (first_byte >> 4) & 1
        opcode = first_byte & 0xf

        second_byte = ord(received[1])
        mask = (second_byte >> 7) & 1
        payload_length = second_byte & 0x7f

        valid_length_encoding = True
        length_encoding_bytes = 1

        if payload_length == 127:

            extended_payload_length = self.receive_bytes(8)
            payload_length = struct.unpack(
                '!Q', extended_payload_length)[0]
            if payload_length > 0x7FFFFFFFFFFFFFFF:
                raise ValueError('Extended payload length >= 2^63')
            if payload_length < 0x10000:
                valid_length_encoding = False
                length_encoding_bytes = 8

        elif payload_length == 126:

            extended_payload_length = self.receive_bytes(2)
            payload_length = struct.unpack(
                '!H', extended_payload_length)[0]
            if payload_length < 126:
                valid_length_encoding = False
                length_encoding_bytes = 2

        
        if mask == 1:
            masking_nonce = map(ord,self.receive_bytes(4))
            
            raw_payload_bytes = self.receive_bytes(payload_length)

            _count = 0
            _mask_size = len(masking_nonce)

            result = array.array('B')
            result.fromstring(raw_payload_bytes)

            for i in xrange(len(result)):
                result[i] ^= masking_nonce[_count]
                _count = (_count + 1) % _mask_size
            bytes = result.tostring()

        else:
            raw_payload_bytes = self.receive_bytes(payload_length)
            bytes = raw_payload_bytes

        return frame(fin=fin, rsv1=rsv1, rsv2=rsv2, rsv3=rsv3, opcode=opcode, payload=bytes)
