'''
    This class is for DNS Resolvers information
    DNS IP and its exitnodes
'''

#
class DNSResolverInfo():
    #
    def __init__(self,DNSIP):
        self.DNSIP = DNSIP
        self.ExitNodelist = []
        self.ExitNodelistJSON =[]
        self.nodeCount = 0

    #
    def insertNode(self,Node):
         self.ExitNodelist.append(Node)
         self.ExitNodelistJSON.append(Node.JSON)

    #
    def reprJSON(self):
        return dict(DNSIP=self.DNSIP, ExitNodelist=self.ExitNodelistJSON,count=self.nodeCount)