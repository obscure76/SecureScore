__author__ = 'obscure'
import socketserver
import netifaces as ni
import codecs
import json
import requests


class MyTCPHandler(socketserver.BaseRequestHandler):
    """
    The RequestHandler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """

    def handle(self):
        # self.request is the TCP socket connected to the client
        self.data = self.request.recv(10200)
        #self.data = self.request.recv(1024)
        #print ("{} wrote:",format(self.client_address[0]))
        print (self.data)
        reader = codecs.getreader("utf-8")
        data = self.data.decode('utf-8')
        j = json.loads(data)
        # just send back the same data, but upper-cased
        #self.request.sendall(self.data.upper())

if __name__ == "__main__":
    HOST, PORT = "localhost", 9999
    # Create the server, binding to localhost on port 9999
    ni.ifaddresses('eth0')
    ip = ni.ifaddresses('eth0')[2][0]['addr']
    print (ip)  # should print "192.168.100.37"
    server = socketserver.TCPServer((ip, PORT), MyTCPHandler)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()

