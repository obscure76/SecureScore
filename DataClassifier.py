__author__ = 'obscure'
import time
import socket
import dpkt
from sklearn.feature_extraction import DictVectorizer
from sklearn import svm


fields = {'vlan', 'len', 'data_length', 'type', 'nw_src', 'nw_dst', 'icmp_type', 'icmp_code',
          'nw_tos', 'nw_proto', 'time'}

flow_attr = {'src', 'dst', 'len', 'type', 't1', 't2', 't3', 't4', 't5'}
gPkts = list()
perTypePkts = {'ARP': [], 'ICMP': [], 'IPV4': []}
arpFlows = list()
icmpFlows = list()
ipFlows = list()
arpDicts = list()
icmpDicts = list()
ipDicts = list()
arpY = list()
icmpY = list()
ipY = list()
hosts = dict()
vec = DictVectorizer()
clfsvm = svm.LinearSVC(C=30.0)

def ether_decode(p):
    return ':'.join(['%02x' % ord(x) for x in str(p)])

class Host:

    def __init__(self, ip):
        self.ip = ip
        self.score = 0

    def getScore(self):
        return self.score


class Flow:

    def __init__(self, s, d, t):
        self.src = s
        self.dst = d
        self.len = 0
        self.type = t
        self.t1 = 0
        self.t2 = 0
        self.t3 = 0
        self.t4 = 0
        self.t5 = 0
        self.lastSeen = 0
        self.match = 0

    def equals(self, f2):
        if self.src == f2.src and self.dst == f2.dst:
            return True
        return False


class FlowClassifier:

    def __init__(self, src, dst):
        self.src = src
        self.dst = dst

    def storeFlow(self, pkt):
        pass

    def trainData(self):
        pass

    def classify(self):
        pass

    def getScore(self):
        pass

    def assignScore(self):
        pass


#This class takes care of packet classification
class DataClassifier():
    globals()

    def __init__(self):
        self.ddict = None

    def handle(self, dd):
        globals()
        curr = {}
        for f in fields:
            if f in dd:
                curr[f] = dd[f]
            else:
                curr[f] = None
        curr['time'] = time.time()
        gPkts.append(curr)
        if dd['type'] == 'ARP':
            tempFlow = Flow(dd['nw_src'], dd['nw_dst'], dd['type'])
            match = 0
            for f in arpFlows:
                if tempFlow.equals(f):
                    match = 1
                    if tempFlow.equals(f):
                        match = 1
                        if f.t2 == 0:
                            if time.time() - f.lastSeen > 5:
                                f.t1 = 0
                                f.lastSeen = time.time()
                            else:
                                f.t2 = time.time() - f.lastSeen
                            continue
                        elif f.t3 == 0:
                            if time.time() - f.lastSeen > 5:
                                f.t1 = f.t2 = 0
                                f.lastSeen = time.time()
                            else:
                                f.t3 = time.time() - f.lastSeen
                            continue
                        elif f.t4 == 0:
                            if time.time() - f.lastSeen > 5:
                                f.t1 = f.t2 = f.t3 = 0
                                f.lastSeen = time.time()
                            else:
                                f.t4 = time.time() - f.lastSeen
                            continue
                        elif f.t5 == 0:
                            if time.time() - f.lastSeen > 5:
                                f.t1 = f.t2 = f.t3 = f.t4 =0
                                f.lastSeen = time.time()
                            else:
                                f.t5 = time.time() - f.lastSeen
                            continue
                        else:
                            ldict = list()
                            self.covertToDicts([f], ldict)
                            tX = self.vectorize(ldict)
                            if self.predict(tX)[0] == 'bad' and f.match ==0:
                                print 'ARP broadcast attack detected'
                                f.match = 1
            if match == 0:
                tempFlow.t1 = 0
                tempFlow.lastSeen = time.time()
                tempFlow.len = dd['len']
                arpFlows.append(tempFlow)
        if dd['type'] == 'ICMP':
            perTypePkts[dd['type']].append(curr)
            perTypePkts['ICMP'].append(curr)
            self.assignScores(curr)
            if dd['type'] != 'ICMP':
                src = dd['nw_src']
                dst = dd['nw_dst']
                key = str(src) + str(dst)
                if key not in FlowClassifier.flows:
                    FlowClassifier.flows[key] = 0
                else:
                    #Update score
                    FlowClassifier.flows[key] += 0.2
        if dd['type'] == 'IPV4':
            pass
        else:
            pass
    #"vlan":-1,"len":1530,"data_length":1494,"type":"IPV4","nw_src":"10.0.0.3","nw_dst":"10.0.0.1","nw_tos":0,"nw_proto":17

    def parseData(self, fPath = 'polo'):
        globals()
        #Select features
        cap = open(fPath, 'r')
        counter = 0
        ipcounter = 0
        tcpcounter = 0
        udpcounter = 0
        icmpcounter = 0
        for ts, pkt in dpkt.pcap.Reader(cap):
            if counter == 0:
                ts0 = ts
                pkt0 = pkt
            #print(ts)
            counter += 1
            plen = len(pkt)
            eth = dpkt.ethernet.Ethernet(pkt)
            if pkt[12] == '\x08' and pkt[13] == '\x06':
                #its ARP
                ptype = 'ARP'
                dlen = plen
                vlan = -1
                #print('ARP')
                #print(plen-4, pkt[plen-11], pkt[plen-12], pkt[plen-13],pkt[plen-14])
                nw_src = str(10) + '.' + str(map(ord, pkt[plen-13])[0]) \
                         + '.' + str(map(ord, pkt[plen-12])[0]) + '.' + str(map(ord, pkt[plen-11])[0])
                nw_dst = str(10) + '.' + str(map(ord, pkt[plen-3])[0]) \
                         + '.' + str(map(ord, pkt[plen-2])[0]) + '.' + str(map(ord, pkt[plen-1])[0])
                #print(nw_src, nw_dst)
                tempFlow = Flow(nw_src, nw_dst, 'ARP')
                match = 0
                for f in arpFlows:
                    if tempFlow.equals(f):
                        match = 1
                        if f.t2 == 0:
                            f.t2 = ts - f.lastSeen
                            continue
                        elif f.t3 == 0:
                            f.t3 = ts - f.lastSeen
                            continue
                        elif f.t4 == 0:
                            f.t4 = ts - f.lastSeen
                            continue
                        elif f.t5 == 0:
                            f.t5 = ts - f.lastSeen
                            continue
                        else:
                            continue
                if match == 0:
                    tempFlow.t1 = 0
                    tempFlow.lastSeen = ts
                    tempFlow.len = plen
                    arpFlows.append(tempFlow)
            elif pkt[12] == '\x08' and pkt[13] == '\x00':
                icmpcounter += 1
                ip = eth.data
                vlan = -1
                nw_src = socket.inet_ntoa(ip.src)
                nw_dst = socket.inet_ntoa(ip.dst)
                ptype = 'ICMP'
                dlen = len(ip.data)
                tempFlow = Flow(nw_src, nw_dst, 'ICMP')
                match = 0
                for f in icmpFlows:
                    if tempFlow.equals(f):
                        match = 1
                        if f.t2 == 0:
                            f.t2 = ts - f.lastSeen
                            continue
                        elif f.t3 == 0:
                            f.t3 = ts - f.lastSeen
                            continue
                        elif f.t4 == 0:
                            f.t4 = ts - f.lastSeen
                            continue
                        elif f.t5 == 0:
                            f.t5 = ts - f.lastSeen
                            continue
                        else:
                            continue
                if match == 0:
                    tempFlow.t1 = 0
                    tempFlow.lastSeen = ts
                    tempFlow.len = plen
                    icmpFlows.append(tempFlow)
                    #print('Icmp flow new ', tempFlow.src, tempFlow.dst)
            elif eth.type == dpkt.ethernet.ETH_TYPE_IP:
                ip = eth.data
                #tcp = ip.data
                vlan = eth.vlan
                dlen = len(ip.data)
                ptype = 'IPV4'
                nw_src = socket.inet_ntoa(ip.src)
                nw_dst = socket.inet_ntoa(ip.dst)
                #print('IP', socket.inet_ntoa(ip.src), socket.inet_ntoa(ip.dst), tcp.sport, tcp.dport)
                tempFlow = Flow(nw_src, nw_dst, 'IPV4')
                match = 0
                for f in ipFlows:
                    if tempFlow.equals(f):
                        match = 1
                        if f.t2 == 0:
                            f.t2 = ts - f.lastSeen
                            continue
                        elif f.t3 == 0:
                            f.t3 = ts - f.lastSeen
                            continue
                        elif f.t4 == 0:
                            f.t4 = ts - f.lastSeen
                            continue
                        elif f.t5 == 0:
                            f.t5 = ts - f.lastSeen
                            continue
                        else:
                            self.predict()
                if match == 0:
                    tempFlow.t1 = 0
                    tempFlow.lastSeen = ts
                    tempFlow.len = plen
                    ipFlows.append(tempFlow)
                ipcounter += 1
                if ip.p == dpkt.ip.IP_PROTO_TCP:
                    tcpcounter += 1
                if ip.p == dpkt.ip.IP_PROTO_UDP:
                    udpcounter += 1
            else:
                continue
        #print(icmpcounter)

    def covertToDicts(self, flows, listOfDicts):
        for f in flows:
            tempDict = {}
            tempDict['src'] = f.src
            tempDict['dst'] = f.dst
            tempDict['len'] = f.len
            tempDict['type'] = f.type
            tempDict['t1'] = f.t1
            tempDict['t2'] = f.t2
            tempDict['t3'] = f.t3
            tempDict['t4'] = f.t4
            tempDict['t5'] = f.t5
            listOfDicts.append(tempDict)

    def dataToDicts(self, state):
        globals()
        self.covertToDicts(arpFlows, arpDicts)
        self.covertToDicts(icmpFlows, icmpDicts)
        self.covertToDicts(ipFlows, ipDicts)
        for x in arpFlows:
            arpY.append(state)
        for x in icmpFlows:
            icmpY.append(state)
        for x in ipFlows:
            ipY.append(state)

    def resetFlows(self):
        del arpFlows[:]
        del icmpFlows[:]
        del ipFlows[:]

    def printARP(self):
        print(len(arpFlows), len(arpDicts))

    def vectorizeTestSets(self):
        arpX = vec.fit_transform(arpDicts)
        #print(vec.get_feature_names())
        print(vec)
        return arpX, arpY

    def vectorize(self, nList):
        fnames = vec.get_feature_names()
        for f in fnames:
            if f not in flow_attr:
                nList[0][f] = 0
        arpX = vec.fit_transform(nList)
        print(arpX.shape)
        return arpX

    def trainData(self, X, Y):
        globals()
        clfsvm.fit(X, Y)
        print(clfsvm)

    def predict(self, X):
        #Using the filter after training classify the current pkt
        return clfsvm.predict(X)

    def assignScores(self, pkt):
        globals()
        if pkt['nw_src'] not in hosts:
            h = Host(pkt['nw_src'])
            hosts[pkt['nw_src']] = 0
        else:
            #Calculated Score
            hosts[pkt['nw_src']] += 0.2




