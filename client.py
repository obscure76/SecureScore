__author__ = 'obscure'
import socket
import sys
import netifaces as ni

PORT =  9999
data = " ".join(sys.argv[1:])

ni.ifaddresses('eth0')
HOST = ni.ifaddresses('eth0')[2][0]['addr']

# Create a socket (SOCK_STREAM means a TCP socket)
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    # Connect to server and send data
    sock.connect((HOST, PORT))
    s = 'Hello'
    sock.send(bytes(s, 'UTF-8'))

    # Receive data from the server and shut down
    received = sock.recv(1024)
finally:
    sock.close()

print("Sent:     {}".format(data))
print("Received: {}".format(received))
