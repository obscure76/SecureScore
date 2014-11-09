__author__ = 'obscure'
import socketserver
import netifaces as ni
import json
import time
import DataClassifier
from sklearn.cluster import KMeans

oldGlobalTypeCounter = {}
globalTypeCounter = {}
oldPerSwitchTypeCounter = {}
perSwitchTypeCounter = {}
PERIOD = 120

class OFMsgClassifier():

    def __init__(self):
        self.cluster = Cluster()
        self.cluster.trainGoodData()
        self.cluster.trainBadData()

    def findDistance(self, v1, v2):
        types = set(v1.keys())
        types.intersection(v2.keys())
        dist = {}
        sumOfSquares = 0.0
        for typ in types:
            dist[typ] = (v1[typ] - v2[typ]) * (v1[typ] - v2[typ])
            sumOfSquares += dist[typ]
        return sumOfSquares

    def classify(self, data):
        distGG = self.findDistance(self.cluster.globalGG, data)
        distBG = self.findDistance(self.cluster.globalBG, data)
        if distGG >= distBG:
            #Good data point
            pass
        else:
            #Bad data point
            pass


class Cluster():

    def __init__(self):
        self.globalGG = {}
        self.globalBG = {}

    def trainGoodData(self):
        #Train Good Data and find centroid
        pass

    def trainBadData(self):
        #Train Bad Data and find centroid
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
            for typ in oldGlobalTypeCounter:
                change[typ] = globalTypeCounter[typ] - oldGlobalTypeCounter[typ]
        for typ in  globalTypeCounter:
            oldGlobalTypeCounter[typ] = globalTypeCounter[typ]

    #This routine does the temporal analysis of switch statistics of OF messages
    def switchTemporalAnalysis(self):
        global oldPerSwitchTypeCounter, perSwitchTypeCounter
        if self.count == 0:
            for sw in perSwitchTypeCounter:
                oldPerSwitchTypeCounter[sw] = {}
                for typ in perSwitchTypeCounter[sw]:
                    oldPerSwitchTypeCounter[sw][typ] = perSwitchTypeCounter[sw][typ]
        else:
            change = {}
            for sw in oldPerSwitchTypeCounter:
                change[sw] = {}
                for typ in oldPerSwitchTypeCounter:
                    change[sw][typ] = perSwitchTypeCounter[sw][typ] - oldPerSwitchTypeCounter[sw][typ]


    #This does the correlation of each switch with rest of the switches
    def temporalCorrelation(self):
        global perSwitchTypeCounter
        correlation = {}
        for sw1 in perSwitchTypeCounter:
            for sw2 in perSwitchTypeCounter:
                correlation[sw1][sw2] = 0
                for typ in perSwitchTypeCounter[sw1]:
                    if typ in perSwitchTypeCounter[sw2]:
                        correlation[sw1][sw2] += perSwitchTypeCounter[sw1][typ]*perSwitchTypeCounter[sw2][typ]


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
    OFPORT = 9998
    DPORT = 9997
    # Create the server, binding to localhost on port 9999
    #ni.ifaddresses('wlan0')
    IP = ni.ifaddresses('eth0')[2][0]['addr']
    print ('Listening on ',IP, OFPORT)
    try:
        OFServer = socketserver.TCPServer((IP, OFPORT), MyTCPHandler)
    except:
        print('Cannot start OFServer on ', OFPORT)
        exit(-1)
    print ('Listening on ',IP, DPORT)
    try:
        dataServer = socketserver.TCPServer((IP, DPORT), DataClassifier.pktClassifier)
    except:
        print('Cannot start DataServer on', DPORT)
        OFServer.server_close()
        exit(-1)
    #Create the OFMsgClassifier
    try:
        classifier = OFMsgClassifier()
        OFServer.serve_forever(classifier)
    except:
        print('Could not server forever on ', OFPORT)
        OFServer.server_close()
        dataServer.server_close()
    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    try:
        pktClassifier = DataClassifier.pktClassifier()
        dataServer.serve_forever(pktClassifier)
    except:
        print('Could not serve forever on ', DPORT)
        OFServer.server_close()
        dataServer.server_close()

