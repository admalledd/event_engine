#import lib.common
import socket
import sys

SID=input('sid=>>')
def main():
    HOST, PORT = "localhost", 1986
    
    def send(type,dat):
        
    # Create a socket (SOCK_STREAM means a TCP socket)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect to server and send data
    sock.connect((HOST, PORT))
    
    recv = sock.recv(4)
    if recv == 'gsid':
        send('resp','rsid'+str(SID))
        print "SID %s sent"%SID

    sock.close()
def pack_fmt(data):
    '''data is a dictionary with 'type' and 'data' values'''
    
    #first we calculate content_len
    content_len = str(len(data['data']))
    if len(content_len) >4:
        print '\n**ERROR too long of mesg\n**'
    while len(content_len) <4:
        content_len='0'+content_len
    s=content_len+type+dat
    print s
    return s
#main()
pack_fmt({ 'type':'ss','data':'sid:%d'%(SID) })