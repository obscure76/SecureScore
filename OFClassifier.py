__author__ = 'obscure'
#import socketserver
import SocketServer as socketserver
import netifaces as ni
import json
import time
import DataClassifier
import os
import socket
import sys
import pcap

#from sklearn.cluster import KMeans

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


class MessageHandler():

    def __init__(self):
        self.time = time.time()
        self.count = 0
        self.data = None
        self.ofc = OFMsgClassifier()
        self.dc = DataClassifier.DataClassifier()

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
        for typ in globalTypeCounter:
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

    def learnFromTestData(self):
         #Paths to datasets
        arpBad = '/home/obscure/PycharmProjects/SecureScore/datasets/arpattack/'
        arpGood = '/home/obscure/PycharmProjects/SecureScore/datasets/arpgood/'
        udpPath = '/home/obscure/PycharmProjects/SecureScore/datasets/udpattack.pcap'
        pingPath ='/home/obscure/PycharmProjects/SecureScore/datasets/pingattack.pcap'
        #print('PATH ', arpBad)
        dc = DataClassifier.DataClassifier()
        # Parse ARP bad files
        for root, subFolders, files in os.walk(arpBad):
            for filename in files:
                filePath = os.path.join(root, filename)
                #print(filePath)
                dc.parseData(filePath)
        dc.dataToDicts('bad')
        dc.resetFlows()
        print('len ARP bad dataset', len(DataClassifier.arpDicts))
        # Parse ARP good files
        for root, subFolders, files in os.walk(arpGood):
            for filename in files:
                filePath = os.path.join(root, filename)
                #print(filePath)
                dc.parseData(filePath)
        dc.dataToDicts('good')
        print('len ARP dataset', len(DataClassifier.arpDicts))
        arpX, arpY = dc.vectorizeTestSets()
        print(arpX.shape,  len(arpY))
        dc.trainData(arpX, arpY)
        dc.resetFlows()
        '''
        testFlowList = [{'src' : '10.0.0.1', 'dst' : '10.0.0.2', 'len' : '42', 'type' : 'ARP', 't1' : 0,
                     't2' : 0, 't3' :0, 't4' : 0, 't5' :0}]
        testX = dc.vectorize(testFlowList)
        print(dc.predict(testX))'''

    #This handles every pkt info received as json from the controller
    def handle(self, pkt):
        globals()
        # self.request is the TCP socket connected to the client
        self.data = pkt
        switch = 'switch'
        #print(self.data)
        datum = self.data.decode('utf-8')
        #print('Raw', datum)
        try:
            j = json.loads(datum)
        except ValueError:
            #print('Something wrong')
            return
        #print(len(j))
        if len(j) == 6:
            self.dc.handle(j)
        try:
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
        except Exception:
            return
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

    def listenForever(self):
        OFPORT = 9998
        DPORT = 9997
         # Create the server, binding to localhost on port 9999
        #ni.ifaddresses('wlan0')
        IP = ni.ifaddresses('eth0')[2][0]['addr']
        print('Listening on ', IP, OFPORT)
        try:
            OFSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            OFSocket.bind((IP, 9998))
            OFSocket.listen(5)
        except IOError:
            sys.exit(-1)
        while True:
            print('waiting for a connection')
            connection, client_address = OFSocket.accept()
            try:
                print('client connected:', client_address)
                while True:
                    data = connection.recv(1600)
                    if data:
                        #connection.sendall(data)
                        self.handle(data)
                    else:
                        break
            except IOError:
                print(IOError)
            finally:
                connection.close()


if __name__ == "__main__":
    OFPORT = 9998
    DPORT = 9997
    start = time.time()
    mh = MessageHandler()
    mh.learnFromTestData()
    mh.listenForever()