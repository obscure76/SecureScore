__author__ = 'obscure'
import socketserver
import json

fields = {'vlan', 'len', 'data_length', 'type', 'nw_src', 'nw_dst', 'icmp_type', 'icmp_code', 'nw_tos', 'nw_proto'}

'''
sb.append("{");
    	                    	sb.append("\"Vlan\":");
    	                    	sb.append(eth.getVlanID());
    	                    	sb.append(",\"Len\":");
    	                    	sb.append(pi.getLengthU());
    	                    	sb.append(",\"data_length\":");
    	                    	sb.append(pi.getTotalLength() - OFPacketIn.MINIMUM_LENGTH);
    	                    	if (pkt instanceof ARP) {
    	                    		ARP p = (ARP) pkt;
        	                    	sb.append("\"Type\":");
        	                    	sb.append("\"ARP\"");
    	                    		sb.append(",\"nw_src\":");
    	                    		sb.append(IPv4.fromIPv4Address(IPv4.toIPv4Address(p.getSenderProtocolAddress())));
    	                    		sb.append(",\"nw_dst\":");
    	                    		sb.append(IPv4.fromIPv4Address(IPv4.toIPv4Address(p.getTargetProtocolAddress())));
    	                    	}
    	                    	else if (pkt instanceof ICMP) {
    	                    		ICMP icmp = (ICMP) pkt;
    	                    		sb.append("\"Type\":");
        	                    	sb.append("\"ICMP\"");
    	                    		sb.append(",\"icmp_type\":");
    	                    		sb.append(icmp.getIcmpType());
    	                    		sb.append(",\"icmp_code\":");
    	                    		sb.append(icmp.getIcmpCode());
    	                    	}
    	                    	else if (pkt instanceof IPv4) {
    	                    		IPv4 p = (IPv4) pkt;
    	                    		sb.append("\"Type\":");
        	                    	sb.append("\"IPV4\"");
    	                    		sb.append(",\"nw_src\":");
    	                    		sb.append(IPv4.fromIPv4Address(p.getSourceAddress()));
    	                    		sb.append(",\"nw_dst\":");
    	                    		sb.append(IPv4.fromIPv4Address(p.getDestinationAddress()));
    	                    		sb.append(",\"nw_tos\":");
    	                    		sb.append(p.getDiffServ());
    	                    		sb.append(",\"nw_proto\":");
    	                    		sb.append(p.getProtocol());
    	                    	}
'''


class flowClassifier:

    def __init__(self):
        pass

    def storeFlow(self):
        pass

    def trainData(self):
        pass

    def classify(self):
        pass

    def assignScore(self):
        pass


#This class takes care of packet classification
class pktClassifier(socketserver.BaseRequestHandler):

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
            print(k,j[k])
        j = json.loads(data)
        curr = {}
        for f in fields:
            if f in j:
                curr[f]= j[f]
            else:
                curr[f] = None

    def trainData(self):
        pass

    def classify(self):
        pass

    def assignScores(self):
        pass





