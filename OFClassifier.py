__author__ = 'obscure'
import socketserver
import netifaces as ni
import codecs
import json
import time

globalTypeCounter = {}
perSwitchTypeCounter = {}

class OFMsgClassifier():

    def __init__(self):
        pass

    def classify(self, pkt):
        pass

class MyTCPHandler(socketserver.BaseRequestHandler):

    def __init__(self):
        self.time = time.time()

    def temporalAnalysis(self):
        pass

    def temporalCorrelation(self):
        pass

    def handle(self):
        globals()
        # self.request is the TCP socket connected to the client
        self.data = self.request.recv(10200)
        switch = 'switch'
        #print ("{} wrote:",format(self.client_address[0]))
        print (self.data)
        reader = codecs.getreader("utf-8")
        data = self.data.decode('utf-8')
        print(data)
        j = json.loads(data)
        for k in j:
            print(k,j[k])
        j = json.loads(data)

        if j[switch] not in perSwitchTypeCounter:
            perSwitchTypeCounter[j[switch]] = {}
        for k in j:
            if k != 'switch':
                if k not in globalTypeCounter:
                    globalTypeCounter[k] = 1
                else:
                    globalTypeCounter[k] += 1
                if k not in perSwitchTypeCounter[j[switch]]:
                    perSwitchTypeCounter[j[switch]][k] = 1
                else:
                    perSwitchTypeCounter[j[switch]][k] += 1
        print(globalTypeCounter)
        print(perSwitchTypeCounter)
        if self.time - time.time() > 120:
            self.time = time.time()
            self.temporalAnalysis()
            self.temporalCorrelation()


if __name__ == "__main__":
    HOST, PORT = "localhost", 9998
    # Create the server, binding to localhost on port 9999
    ni.ifaddresses('wlan0')
    ip = ni.ifaddresses('wlan0')[2][0]['addr']
    print (ip)  # should print "192.168.100.37"
    server = socketserver.TCPServer((ip, PORT), MyTCPHandler)
    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
