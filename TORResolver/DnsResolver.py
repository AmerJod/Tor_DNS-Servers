# import datetime
# import functools
# import getopt
import glob

import json
# import os
# import pycurl
# import sys
# import time
# from pprint import pprint
# import certifi

#from tqdm import tqdm
from stem.util import term


NODES_PATH = 'TOR/ConnectionsHandler/Nodes/ExitNodesJSON.json'

class DNSObject():
    def __init__(self,DNSIP):
        self.DNSIP = DNSIP
        self.list = []
        self.count = 0
    def insertNode(self,NodeIp):
         self.list.append(NodeIp)

class ExitNodeObject():
    def __init__(self,nodeIP,nodeDomain,nodeModifiedDomainfull):
        self.nodeIP = nodeIP
        self.nodeDomian = nodeDomain
        self.nodeModifiedDomian = nodeModifiedDomainfull


def loadExitNodes(dir):
    jsonFiles = glob.glob(str('%s/*.json' % dir))
    with open(jsonFiles[0]) as f:
        jsonObjects = json.load(f)
        return jsonObjects

def fun3(DNSObj,WEBObj):
    count = 0
    DNSouterList = []
    for obj in DNSObj: # get all the dns ip wittout repetation
        innerList = []

        dnsIP = DNSObj[obj]['Request']['SrcIP'] #.encode("ascii")
        dnsDomainfull = DNSObj[obj]['Request']['Domain']#.encode("ascii")
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

        node = DNSObject(obj)
        DNSList.append(node)


    for DnsNodeObj in DNSList:
        tempNodeList =[]
        count = 1 + count
        for Dns in DNSObj:
            dnsIP = DNSObj[Dns]['Request']['SrcIP']
            if dnsIP == DnsNodeObj.DNSIP:
                nodeDomainfull = DNSObj[Dns]['Request']['Domain']
                nodeModifiedDomainfull = DNSObj[Dns]['Request']['modifiedDomain']
                nodeDomain = [x.strip() for x in nodeDomainfull.split('.')][0]  # remove the domain: dnstestsuite.space
                dnsExitnodeIP = [x.strip() for x in nodeDomain.split('_')][-1:][0]  # get the ip of the exitnode
                if (dnsExitnodeIP.__contains__('-')):
                    dnsExitnodeIP = dnsExitnodeIP.replace("-", ".")

                    if dnsExitnodeIP not in tempNodeList:#DnsNodeObj.ExitNodelist.exitNodeIP:
                        tempNodeList.append(dnsExitnodeIP)
                        exitnode=ExitNodeObject(dnsExitnodeIP,nodeDomain,nodeModifiedDomainfull)
                        DnsNodeObj.insertNode(exitnode)
                        DnsNodeObj.count += 1

    for DnsNodeObj in DNSList:
        index = 0
        print(term.format('DNS Resolver IP: %s - Exitnode: %d ' % (DnsNodeObj.DNSIP, DnsNodeObj.count) ,term.Color.GREEN))
        for node1 in DnsNodeObj.list:
            index += 1
            print(term.format("      %d - %s " % (index, node1.nodeIP),term.Color.YELLOW))
        print

    print(+count)



if __name__ == '__main__':
    DNSObj = loadExitNodes('DNS')
    WEBObj = loadExitNodes('WEB')
    print('DNSObj len: %d'% len(DNSObj))
    print('WEBObj len: %d'% len(WEBObj))
    fun3(DNSObj,WEBObj)
