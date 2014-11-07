__author__ = 'obscure'
import socketserver
import netifaces as ni
import codecs
import json
import time

oldGlobalTypeCounter = {}
globalTypeCounter = {}
perSwitchTypeCounter = {}
PERIOD = 120

class OFMsgClassifier():

    def __init__(self):
        pass

    def classify(self, pkt):
        pass


class Cluster():
    pass


class MyTCPHandler(socketserver.BaseRequestHandler):

    def __init__(self):
        self.time = time.time()
        self.count = 0

    #This routine does the temporal analysis of global statistics of OF messages
    def globalTemporalAnalysis(self):
        global oldGlobalTypeCounter, globalTypeCounter
        if self.count == 0:
            for type in globalTypeCounter:
                oldGlobalTypeCounter[type] = globalTypeCounter[type]
        else:
            change = {}
            for type in oldGlobalTypeCounter:
                change[type] = globalTypeCounter[type] - oldGlobalTypeCounter[type]
        for type in  globalTypeCounter:
            oldGlobalTypeCounter[type] = globalTypeCounter[type]

    #This routine does the temporal analysis of switch statistics of OF messages
    def switchTemporalAnalysis(self):
        pass

    #This does the correlation of each switch with rest of the switches
    def temporalCorrelation(self):
        globals()
        pass

    #This handles evey pkt info received as json from the controller
    def handle(self):
        globals()
        # self.request is the TCP socket connected to the client
        self.data = self.request.recv(10200)
        switch = 'switch'
        #print ("{} wrote:",format(self.client_address[0]))
        print (self.data)
        data = self.data.decode('utf-8')
        print(data)
        j = json.loads(data)
        for k in j:
            print(k,j[k])
        j = json.loads(data)

        #Add an entry in case of a new switch
        if j[switch] not in perSwitchTypeCounter:
            perSwitchTypeCounter[j[switch]] = {}
        #Update pkt counters- Local and Global
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
        #Every 120
        if self.time - time.time() > PERIOD:
            print(globalTypeCounter)
            print(perSwitchTypeCounter)
            self.time = time.time()
            self.globalTemporalAnalysis()
            self.switchTemporalAnalysis()
            self.temporalCorrelation()
            if self.count == 0:
                self.count = 1



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
