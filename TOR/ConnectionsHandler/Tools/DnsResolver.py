"""
This class is for DNS resolver

"""

# import datetime
# import functools
# import getopt
import glob

import json
import os
from TOR.Helper.Helper import Helper
from TOR.Helper.Helper import MSG_TYPES

from stem.util import term
from TOR.ConnectionsHandler.Models.DNSResolverInfo import DNSResolverInfo
from TOR.ConnectionsHandler.Models.DNSExitNode import DNSExitNode


NODES_PATH = 'TOR/ConnectionsHandler/Nodes/ExitNodesJSON.json'
PROCESSED_DNSDATA_PATH = 'ProcessedDNSDataJSON.json'  # gathered by NodeHandler class


class DNSResolver():

    def __init__(self,dir='DNS'):
        self.DNSObj = self.loadExitNodes(dir)

    def loadExitNodes(self,dir):
        jsonFiles = glob.glob(str('%s/*.json' % dir))
        with open(jsonFiles[0]) as f:
            jsonObjects = json.load(f)
            Helper.printOnScreenAlways('DNS records have been loaded\n',MSG_TYPES.YELLOW)
            return jsonObjects


    def Normalize(self,show='yes'):
        count = 0
        DNSouterList = []
        for obj in self.DNSObj: # get all the dns ip wittout repetation
            innerList = []

            dnsIP = self.DNSObj[obj]['Request']['SrcIP'] #.encode("ascii")
            dnsDomainfull = self.DNSObj[obj]['Request']['Domain']#.encode("ascii")
            dnsDomainfull = [x.strip() for x in dnsDomainfull.split('.')][0] # remove the domain: dnstestsuite.space
            temp = ''
            dnsExitnodeIP = [x.strip() for x in dnsDomainfull.split('_')][-1:][0] # get the ip of the exitnode
            if (dnsExitnodeIP.__contains__('-')):
                if dnsIP not in DNSouterList:
                    DNSouterList.append(dnsIP)
                    #print('DNS Resolver IP: %s' % dnsIP)

        DNSouterList= set(DNSouterList)
        DNSList= []
        for obj in DNSouterList:

            node = DNSResolverInfo(obj)
            DNSList.append(node)


        for DnsNodeObj in DNSList:
            tempNodeList =[]
            count = 1 + count
            for Dns in self.DNSObj:
                dnsIP = self.DNSObj[Dns]['Request']['SrcIP']
                if dnsIP == DnsNodeObj.DNSIP:
                    nodeDomainfull = self.DNSObj[Dns]['Request']['Domain']
                    nodeModifiedDomainfull = self.DNSObj[Dns]['Request']['modifiedDomain']
                    nodeDomain = [x.strip() for x in nodeDomainfull.split('.')][0]  # remove the domain: dnstestsuite.space
                    dnsExitnodeIP = [x.strip() for x in nodeDomain.split('_')][-1:][0]  # get the ip of the exitnode
                    if (dnsExitnodeIP.__contains__('-')):
                        dnsExitnodeIP = dnsExitnodeIP.replace("-", ".")

                        if dnsExitnodeIP not in tempNodeList:#DnsNodeObj.ExitNodelist.exitNodeIP:
                            tempNodeList.append(dnsExitnodeIP)
                            exitnode=DNSExitNode(dnsExitnodeIP,nodeDomain,nodeModifiedDomainfull)
                            DnsNodeObj.insertNode(exitnode)
                            DnsNodeObj.nodeCount += 1

        if show =='yes':
            for DnsNodeObj in DNSList:
                index = 0
                Helper.printOnScreenAlways('DNS Resolver IP: %s - Exitnode: %d ' % (DnsNodeObj.DNSIP, DnsNodeObj.nodeCount), MSG_TYPES.RESULT)
                for node in DnsNodeObj.ExitNodelist:
                    index += 1
                    Helper.printOnScreenAlways("      %d - %s " % (index, node.exitNodeIP),MSG_TYPES.YELLOW)
                print()

        Helper.printOnScreenAlways("We found %d DNS Resolvers " % count ,MSG_TYPES.RESULT)

        curpath = os.path.dirname(__file__)
        os.chdir(curpath)
        newJSONPath = os.path.join(curpath,PROCESSED_DNSDATA_PATH)
        Helper.storeDNSResolverData(objects=DNSList, path=newJSONPath)
        return DNSList

if __name__ == '__main__':
    DNS = DNSResolver()
    #DNSObj = DNS.loadExitNodes('DNS')
    #WEBObj = loadExitNodes('WEB')
    #print('DNSObj len: %d'% len(DNSObj))
    #print('WEBObj len: %d'% len(WEBObj))
    DNS.Normalize()
