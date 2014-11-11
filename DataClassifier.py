__author__ = 'obscure'
import socketserver
import json

fields = {'vlan', 'len', 'data_length', 'type', 'nw_src', 'nw_dst', 'icmp_type', 'icmp_code', 'nw_tos', 'nw_proto'}
gPkts = list()
lPkts = {'ARP':list, 'ICMP':list, 'IPV4':list}

hosts = dict()


class Host:

    def __init__(self, ip):
        self.ip = ip


class FlowClassifier:
    flows = dict()
    def __init__(self, src, dst):
        self.src = src
        self.dst = dst

    def storeFlow(self,pkt):
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
class PktClassifier(socketserver.BaseRequestHandler):

    def __init__(self):
        pass

    def handle(self):
        globals()
        # self.request is the TCP socket connected to the client
        self.data = self.request.recv(10200)
        print (self.data)
        data = self.data.decode('utf-8')
        print(data)
        j = json.loads(data)
        for k in j:
            print(k, j[k])
        j = json.loads(data)
        curr = {}
        for f in fields:
            if f in j:
                curr[f] = j[f]
            else:
                curr[f] = None
        gPkts.append(curr)
        if j['type'] == 'ARP' or j['type'] == 'ICMP' or j['type'] == 'IPV4':
            lPkts[j['type']].append(curr)
            self.assignScores(curr)
            if j['type'] != 'ICMP':
                src = j['nw_src']
                dst = j['nw_dst']
                key = str(src) + str(dst)
                if key not in FlowClassifier.flows:
                    FlowClassifier.flows[key] = 0
                else:
                    FlowClassifier.flows[key] += 0.2 #Update score


    def trainData(self):
        #Select features
        pass

    def classify(self, pkt):
        #Using the filter after training classify the current pkt
        pass

    def getScore(self):
        pass

    def assignScores(self, pkt):
        globals()
        if pkt['nw_src'] not in hosts:
            h = Host(pkt['nw_src'])
            hosts[pkt['nw_src']] = 0
        else:
            hosts[pkt['nw_src']] += 0.2 #Calc Score




