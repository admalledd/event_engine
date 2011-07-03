
import lib.common
import socket
import sys

HOST, PORT = "localhost", 1986

def send(type,dat):
    content_len = str(len(dat))
    if len(content_len) >4:
        print '\n**ERROR too long of mesg\n**'
    while len(content_len) <4:
        content_len='0'+content_len
    s=content_len+type+dat
    print s
    sock.send(s)
# Create a socket (SOCK_STREAM means a TCP socket)
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to server and send data
sock.connect((HOST, PORT))

recv = sock.recv(4)
if recv == 'gsid':
    sid=chr(55)+chr(128)
    send('resp','rsid'+sid)
    print 55+128

sock.close()
