'''
    This class is for DNS Resolvers information
'''


import glob
import json
import random
import os
import time

import matplotlib.pyplot as plt

from builtins import print
from collections import Counter
from mpl_toolkits.mplot3d import Axes3D
from enum import Enum

from TOR.Helper.Helper import Helper
from TOR.Helper.Helper import MSG_TYPES
from TOR.Helper.Helper import MODE_TYPES


plt.style.use('seaborn')
Requests = []   # to store all the requests from text file
AllLINE = []    # to store all the lines from text file
DNSs = []
MAXNUMBER = 30000 ## -1 means parse all the files
MINNUMBER_DrawGraph = 3000 #000 #2000  ## -1 means parse all the files

FILE_PATH ="C:/Users/Amer Jod/Desktop/UCL/Term 2/DS/DNS_Project/TOR/GatheredFiles/Logs/*.txt"


#
class DNSInfo():
    #
    def __init__(self,DNSIP):
        self.DNSIP = DNSIP
        self.listIDs = []
        self.listPortNumbers = []
        self.listPortNumberAndId = [] # find anyrelastionship between them
        self.count = 0
    #
    def insertPortAndID(self,RequestId,PortNumber):
        RequestId_ = int(RequestId)
        PortNumber_ = int(PortNumber)
        self.listIDs.append(RequestId_)
        self.listPortNumbers.append(PortNumber_)
        self.listPortNumberAndId.append((RequestId_,PortNumber_))

#
class RequestInfo():
    def __init__(self, requestId, srcIP, srcPort,requestIP,domain,modifiedDomain):
        self.requestId = requestId
        self.srcIP = srcIP
        self.srcPort = srcPort
        self.requestIP =requestIP
        self.domain =domain
        self.modifiedDomain = modifiedDomain
        #self.Mix = int(requestId) + int(srcPort)
        #self.Min = int(requestId) - int(srcPort)

#
def filterLine(info):
    RequestId = 're'
    # TODO: Fix the repeation in PORT NUMBER and REQUEST ID:
    previousPortNumber = ''
    previousRequestId = ''
    for item in info:
        if 'RequestId' in item:
            RequestId = item
        elif 'SrcIP'   in item:
            SrcIP = item
        elif 'SrcPort' in item:
            SrcPort = item
        elif 'SrcIPs' in item:
            SrcIP = item
        elif 'SrcPorts' in item:
            SrcPort = item

    RequestId_ = findValue(RequestId)
    SrcIP_ = findValue(SrcIP)
    SrcPort_ = findValue(SrcPort)

    # Create instance form RequestInfo class
    request = RequestInfo(RequestId_,SrcIP_,SrcPort_)
    # Add the instance to  Requests List
    return request

def findValue(value):
    info = value.split(':')
    return info[1].strip() # get the second part of the ExitNodelist, For exmaple: portNumber : 39879


#
def writeAllTextFiles(all):
    '''
        Write/log all the files into json file - EVERYTHING
    '''

    with open('JSON/AllTextFiles.json', 'w') as F:
        # Use the json dumps method to write the ExitNodelist to disk
        F.write(json.dumps(all, default=dumper))
        print('writing all text files is done')

#
def writeAllRequests(requests):
    '''
        Write/logs all the Requests into json file - SEMI-FILTERED
    '''
    with open('JSON/AllRequestsInfo.json', 'w') as F:
        # Use the json dumps method to write the ExitNodelist to disk
        print(requests.__len__())
        F.write(json.dumps(requests, default=dumper))
        print('writing all requests info is done')

#
def getInfoFormTextFiles(PATH=FILE_PATH):
    '''
        Get info form text file and store it in ExitNodelist and return the total numbe
    '''

    temp_Requests =[]
    totalLines = 0
    first = True
    # TODO: this should be dynamic
    txtFiles = glob.glob(PATH)
    previousPortNumber = ''
    previousRequestId = ''

    for txtfile in txtFiles:
        with open(txtfile) as file:

            for line in file:
                if ('RecordType' in line  or 'Domain' in line or 'RequestId' in line) and 'check' in line.lower() :
                    # get all the legitimate/reasonable records/lines from the text fileS
                    AllLINE.append(line) # all the records
                    info = line.split('|')
                    # filter line, get sendRequests, IP and port number form the text.
                    for item in info:
                        if 'RequestId' in item:
                            RequestId = item
                        elif 'SrcIP' in item:
                            SrcIP = item
                        elif 'SrcPort' in item:
                            SrcPort = item

                    RequestId_ = findValue(RequestId)
                    SrcIP_ = findValue(SrcIP)
                    SrcPort_ = findValue(SrcPort)

                    if first is True: # To avoid sendRequests repetation
                        previousPortNumber = SrcPort_
                        previousRequestId =RequestId_
                        first= False
                        temp_Requests.append(filterLine(info))
                        totalLines += 1

                    elif previousPortNumber != SrcPort_ and previousRequestId != RequestId_:
                        temp_Requests.append(filterLine(info))
                        previousPortNumber = SrcPort_
                        previousRequestId = RequestId_
                        totalLines += 1

    return totalLines, temp_Requests,AllLINE
#
def dumper(obj):
    try:
        return obj.toJSON()

    except:
        return obj.__dict__