import datetime
import functools
import getopt
import glob
import io
import json
import os
import pycurl
import sys
import time
from pprint import pprint
import certifi
import stem.process
from tqdm import tqdm



NODES_PATH = 'TOR/ConnectionsHandler/Nodes/ExitNodesJSON.json'

class NodeObject():
    def __init__(self,DNSIP):
        self.DNSIP = DNSIP
        self.list = []
        self.count = 0
    def insertNode(self,NodeIp):
         self.list.append(NodeIp)

def loadExitNodes(dir):
    jsonFiles = glob.glob(str('%s/*.json' % dir))
    with open(jsonFiles[0]) as f:
        jsonObjects = json.load(f)
        return jsonObjects

def fun3(DNSObj,WEBObj):
    count = 0
    outerList = []
    for obj in DNSObj:
        innerList = []


        DNSIP = DNSObj[obj]['Request']['SrcIP'].encode("ascii")
        EXITNODE = DNSObj[obj]['Request']['Domain'].encode("ascii")
        EXITNODE = [x.strip() for x in EXITNODE.split('.')][0]
        temp = ''

        if (EXITNODE.__contains__('-')):
            if temp != DNSIP:
                temp = DNSIP
                outerList.append(DNSIP)
                #print('DNS Resolver IP: %s' % DNSIP)

    outerList= set(outerList)
    DNSList= []
    for obj in outerList:
        node = NodeObject(obj)
        DNSList.append(node)

    EXITNODE=''

    for DnsNodeObj in DNSList:
        count = 1 + count
        for Dns in DNSObj:
            DNSIP = DNSObj[Dns]['Request']['SrcIP'].encode("ascii")
            if DNSIP == DnsNodeObj.DNSIP:
                EXITNODE = DNSObj[Dns]['Request']['Domain'].encode("ascii")
                EXITNODE = [x.strip() for x in EXITNODE.split('.')][0]
                if (EXITNODE.__contains__('-')):
                    EXITNODE = EXITNODE.replace("-", ".")
                    if EXITNODE not in DnsNodeObj.list:
                        DnsNodeObj.insertNode(EXITNODE)
                        DnsNodeObj.count += 1

    for DnsNodeObj in DNSList:
        index = 0
        print('DNS Resolver IP: %s - Exitnode: %d ' % (DnsNodeObj.DNSIP, DnsNodeObj.count))
        for node1 in DnsNodeObj.list:
            index += 1
            print("      %d - %s " % (index, node1))
        print

    print(+count)
if __name__ == '__main__':
    DNSObj = loadExitNodes('DNS')
    WEBObj = loadExitNodes('HTTP')
    fun3(DNSObj,WEBObj)
