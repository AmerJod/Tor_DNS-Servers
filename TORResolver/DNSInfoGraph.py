#! /usr/bin/env python3

import glob
import json
import random
import os
import time
from builtins import print
import socket

import matplotlib.pyplot as plt
from collections import Counter
from mpl_toolkits.mplot3d import Axes3D
from enum import Enum

from TOR.Helper.Helper import Helper
from TOR.Helper.Helper import MSG_TYPES
from TOR.Helper.Helper import MODE_TYPES

from subprocess import DEVNULL, STDOUT, check_call, check_output

plt.style.use('seaborn')
Requests = []   # to store all the requests from text file
AllLINE = []    # to store all the lines from text file
DNSs = []
MAXNUMBER = 30000 ## -1 means parse all the files
MINNUMBER_DrawGraph = 3000 #000 #2000  ## -1 means parse all the files

# TODO: Need to be Dynamic
#FILE_PATH ='C:\\DNS9_back_new_logo_6/*.txt'
FILE_PATH ="C:/Users/Amer Jod/Desktop/UCL/Term 2/DS/DNS_Project/TOR/GatheredFiles/Logs/*.txt"

class GRAPHS(Enum):
    ALL = 0
    HISTOGRAM = 1
    SCATTER = 2

class DNSInfo():
    def __init__(self,DNSIP):
        self.DNSIP = DNSIP
        self.listIDs = []
        self.listPortNumbers = []
        self.listPortNumberAndId = [] # find anyrelastionship between them
        self.count = 0

    def insertPortAndID(self,RequestId,PortNumber):
        RequestId_ = int(RequestId)
        PortNumber_ = int(PortNumber)
        self.listIDs.append(RequestId_)
        self.listPortNumbers.append(PortNumber_)
        self.listPortNumberAndId.append((RequestId_,PortNumber_))

class RequestInfo():
    def __init__(self, requestId, srcIP, srcPort):
        self.requestId = requestId
        self.srcIP = srcIP
        self.srcPort = srcPort
        self.Mix = int(requestId) + int(srcPort)
        self.Min = int(requestId) - int(srcPort)

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

    RequestId_ = findValue(RequestId)
    SrcIP_ = findValue(SrcIP)
    SrcPort_ = findValue(SrcPort)

    # Create instance form RequestInfo class
    request = RequestInfo(RequestId_,SrcIP_,SrcPort_)
    # Add the instance to  Requests List
    #Requests.append(sendRequests)
    return request

def findValue(value):
    info = value.split(':')
    return info[1].strip() # get the second part of the ExitNodelist, For exmaple: portNumber : 39879

# get info form text file and store it in ExitNodelist and return the total numbe
def getInfoFormTextFiles(PATH=FILE_PATH):
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
                if 'RecordType' in line  or 'Domain' in line or 'RequestId' in line:
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

def dumper(obj):
    try:
        return obj.toJSON()
    except:
        return obj.__dict__

def normalizeDNSRequests(objects): # Draw Request Id 1/ Port Nnumber 2
    listDNSTemp = []
    listDNS = []
    graphName = ''
    graphTitle = ''

    print(1)
    for obj in objects:
        listDNSTemp.append(obj.srcIP)

    print(listDNSTemp.__len__())
    listDNSTemp = set(listDNSTemp)
    #print(listDNSTemp.__len__())

    print(2)
    try:
        for IP in listDNSTemp:
            listDNS.append(DNSInfo(IP))

        print(3)
        index = 0
        for dns in listDNS:
            print(index)
            for obj in objects:
                if obj.srcIP == dns.DNSIP:
                    dns.insertPortAndID(obj.requestId,obj.srcPort)
            if index == MAXNUMBER:
                break
            index += 1

        print(4)
        index = 0
        for dns in listDNS:
            dns.listIDs.sort()
            dns.listPortNumbers.sort()
            dns.listIDs = Counter(dns.listIDs)
            dns.listPortNumbers = Counter(dns.listPortNumbers)
            if index == MAXNUMBER:
                break
        print(0)
    except Exception as ex:
        print(ex) # add  it to the log

        #print(json.dumps(listDNS, default=dumper))
    with open('JSON/DnsFilterList.json', 'w') as F:
        # Use the json dumps method to write the ExitNodelist to disk
        F.write(json.dumps(listDNS, default=dumper))
        print('writing listDNS is done')

def drawGraphScattor(objects,option, mode=0): # Draw Request options :Id 1/ Port Nnumber 2 ||| mode: 0:normal / 1: one DNS
    list = []
    graphName = ''
    graphTitle = ''
    requestCount = objects.__len__()
    store_Path = ''
    if requestCount > MINNUMBER_DrawGraph:
        if(option == 1):  # ID graph
            for i in objects:
                list.append(i.requestId)
            graphName ='Request Id'
            graphTitle= 'Request IDs Distribution  -  Requests: ' + str(requestCount)

        elif(option == 2):   # Port number graph
            for i in objects:
                list.append(i.srcPort)
            graphName ='Port Numbers'
            graphTitle = 'Port Number Distribution  -  Requests: ' + str(requestCount)
        elif (option == 3):
            for i in objects:
                list.append(i.Mix)
            graphName = 'Mix Numbers'
            graphTitle = ' Distribution'
        elif (option == 4):
            for i in objects:
                list.append(i.Min)
                graphName = 'Mix Numbers'
                graphTitle = ' Distribution'
        try:
            if mode == 1: # draw grphs for every DNS IP
                graphTitle += ' ' + objects[0].srcIP + '  Requests: ' + str(requestCount)
                if (option == 1):
                    store_Path = "Graphs/DNS_Graphs/ByID/%s.png" % (graphName + '_' + objects[0].srcIP)
                elif (option == 2):
                    store_Path = "Graphs/DNS_Graphs/ByPort/%s.png" % (graphName + '_' + objects[0].srcIP)
            else:
                store_Path = "Graphs/%s.png" % (graphName)

            list.sort()
            unique_List = Counter(list)
            set(unique_List)
            x = []
            y = []
            markersize = 1
            if requestCount > 1500:
                for i in unique_List:
                    newVal = int(i)
                    newValFeq = random.uniform(-0.5,0.9) + float(unique_List[i]) # add some noise to help to read the graph
                    #newValFeq = float(unique_List[i])
                    x.append(newVal)
                    y.append(newValFeq)
                plt.plot(x, y, linestyle='', marker='o', markersize=0.7)
            else:
                for i in unique_List:
                    newVal = int(i)
                    newValFeq = float(unique_List[i])  # add some noise to help to read the graph
                    # newValFeq = float(unique_List[i])
                    x.append(newVal)
                    y.append(newValFeq)
                plt.plot(x, y, linestyle='', marker='o', markersize=2)

            plt.xlim([-500, 70000])    # fix the x axis
            plt.xlabel(graphName)
            plt.ylabel("Frequency")
            plt.title(graphTitle)
            if os.path.isfile(store_Path):
                print('found %s' % store_Path)
                os.remove(store_Path)  # Opt.: os.system("rm "+strFile)
            plt.savefig(store_Path)
            plt.clf()
            #plt.show()
        except Exception as ex:
            print('In drawGraph' + str(ex))

def drawGraph(objects, option, mode=0,graphType=GRAPHS.ALL): # Draw Request options :Id 1/ Port Nnumber 2 ||| mode: 0:normal / 1: one DNS
    list = []
    graphName = ''
    graphTitle = ''
    requestCount = objects.__len__()
    storePathHistogram = ''
    storePathScatter = ''
    if requestCount > MINNUMBER_DrawGraph:
        if(option == 1):  # ID graph
            for i in objects:
                list.append(int(i.requestId))
            graphName ='Request Id'
            graphTitle= 'Request IDs Distribution  -  Requests: ' + str(requestCount)

        elif(option == 2):   # Port number graph
            for i in objects:
                list.append(int(i.srcPort))
            graphName ='Port Numbers'
            graphTitle = 'Port Number Distribution  -  Requests: ' + str(requestCount)
        elif (option == 3):
            for i in objects:
                list.append(i.Mix)
            graphName = 'Mix Numbers'
            graphTitle = ' Distribution'
        elif (option == 4):
            for i in objects:
                list.append(i.Min)
                graphName = 'Mix Numbers'
                graphTitle = ' Distribution'
        try:
            srcIP = objects[0].srcIP
            if mode == 1: # draw grphs for every DNS IP
                graphTitle += '          - IP: ' + srcIP #+ '  Requests: ' + str(requestCount)
                if (option == 1):
                    storePathHistogram = "Graphs/DNS_Graphs/ByID/H_%s.png" % (graphName + '_' + srcIP)
                    storePathScatter = "Graphs/DNS_Graphs/ByID/S_%s.png" % (graphName + '_' + srcIP)
                elif (option == 2):
                    storePathHistogram = "Graphs/DNS_Graphs/ByPort/H_%s.png" % (graphName + '_' + srcIP)
                    storePathScatter = "Graphs/DNS_Graphs/ByPort/S_%s.png" % (graphName + '_' + srcIP)
            else:
                storePathHistogram = "Graphs/H_%s.png" % (graphName)
                storePathScatter = "Graphs/S_%s.png" % (graphName)

            list.sort()
            if graphType == GRAPHS.ALL:
                plt.hist(list, bins=10,rwidth=0.9)
                plt.xlim([-500, 70000])    # fix the x axis
                plt.xlabel(graphName)
                plt.ylabel("Frequency")
                plt.title(graphTitle)
                if os.path.isfile(storePathHistogram):
                    #print('found %s' % store_Path)
                    os.remove(storePathHistogram)  # Opt.: os.system("rm "+strFile)
                plt.savefig(storePathHistogram)
                Helper.printOnScreenAlways(' H_%s Saved' % srcIP, MSG_TYPES.RESULT)
                plt.clf()

                unique_List = Counter(list)
                set(unique_List)

                x = []
                y = []
                markersize = 1
                if requestCount > 1500:
                    for i in unique_List:
                        newVal = int(i)
                        newValFeq = random.uniform(-0.5,0.9) + float(unique_List[i]) # add some noise to help to read the graph
                        #newValFeq = float(unique_List[i])
                        x.append(newVal)
                        y.append(newValFeq)
                    plt.plot(x, y, linestyle='', marker='o', markersize=0.7)
                else:
                    for i in unique_List:
                        newVal = int(i)
                        newValFeq = float(unique_List[i])  # add some noise to help to read the graph
                        # newValFeq = float(unique_List[i])
                        x.append(newVal)
                        y.append(newValFeq)
                    plt.plot(x, y, linestyle='', marker='o', markersize=2)

                if os.path.isfile(storePathScatter):
                    # print('found %s' % store_Path)
                    os.remove(storePathScatter)  # Opt.: os.system("rm "+strFile)
                plt.xlim([-500, 70000])  # fix the x axis
                plt.xlabel(graphName)
                plt.ylabel("Frequency")
                plt.title(graphTitle)
                plt.savefig(storePathScatter)
                Helper.printOnScreenAlways(' S_%s Saved' % srcIP, MSG_TYPES.RESULT)
                #plt.show()
                plt.clf()

            elif graphType == GRAPHS.HISTOGRAM:
                plt.hist(list, bins=10,rwidth=0.9)
                plt.xlim([-500, 70000])    # fix the x axis
                plt.xlabel(graphName)
                plt.ylabel("Frequency")
                if os.path.isfile(storePathHistogram):
                    #print('found %s' % store_Path)
                    os.remove(storePathHistogram)  # Opt.: os.system("rm "+strFile)
                plt.savefig(storePathHistogram)
                Helper.printOnScreenAlways(' H_%s Saved' % srcIP,MSG_TYPES.RESULT)
                #plt.show()
                plt.clf()
            elif graphType == GRAPHS.SCATTER:
                unique_List = Counter(list)
                set(unique_List)
                x = []
                y = []
                markersize = 1
                if requestCount > 1500:
                    for i in unique_List:
                        newVal = int(i)
                        newValFeq = random.uniform(-0.5, 0.9) + float(
                            unique_List[i])  # add some noise to help to read the graph
                        # newValFeq = float(unique_List[i])
                        x.append(newVal)
                        y.append(newValFeq)
                    plt.plot(x, y, linestyle='', marker='o', markersize=0.7)
                else:
                    for i in unique_List:
                        newVal = int(i)
                        newValFeq = float(unique_List[i])  # add some noise to help to read the graph
                        # newValFeq = float(unique_List[i])
                        x.append(newVal)
                        y.append(newValFeq)
                    plt.plot(x, y, linestyle='', marker='o', markersize=2)

                plt.xlim([-500, 70000])  # fix the x axis
                plt.xlabel(graphName)
                plt.ylabel("Frequency")
                plt.title(graphTitle)
                if os.path.isfile(storePathScatter):
                    print('found %s' % storePathScatter)
                    os.remove(storePathScatter)  # Opt.: os.system("rm "+strFile)
                plt.savefig(storePathScatter)
                Helper.printOnScreenAlways(' H_%s Saved' % srcIP,MSG_TYPES.RESULT)
                plt.clf()

        except Exception as ex:
            print('In drawGraph' + str(ex))

def drawGraphIDPORTNumber(objects,option, mode=0): # Draw Request options :Id 1/ Port Nnumber 2 ||| mode: 0:normal / 1: one DNS
    list = []
    graphName = ''
    graphTitle = ''
    requestCount = objects.__len__()
    store_Path = ''
    if requestCount > MINNUMBER_DrawGraph:
        if(option == 1):  # ID/PORT graph
            for obj in objects:
                list.append([obj.requestId,obj.srcPort])
            graphName ='Request Id-Port Number'
            graphTitle= 'Request ID and Port Number Distribution  -  Requests: ' + str(requestCount)

        try:
            graphName = graphName.replace(' ','_')
            store_Path = "Graphs/%s.png" % (graphName)
            list.sort()
            unique_List = list
            x = []
            y = []
            markersize = 0.167
            for obj in unique_List:
                portNumberVal = int(obj[1])
                requestIDVal = int(obj[0])
                x.append(portNumberVal)
                y.append(requestIDVal)

            plt.plot(x, y, linestyle='', marker='o', markersize=markersize)
            plt.ylim([-3000, 70000])  # fix the 8 axis
            plt.xlim([-2000, 70000])  # fix the x axis
            plt.xlabel("Port Number")
            plt.ylabel("Request Id")
            plt.title(graphTitle)
            if os.path.isfile(store_Path):
                print('found %s' % store_Path)
                os.remove(store_Path)  # Opt.: os.system("rm "+strFile)
            plt.savefig(store_Path)
            #plt.show()
            plt.clf()


        except Exception as ex:
            print('In drawGraph' + str(ex))

def drawGraphIDPORTNumber3D(objects,option, mode=0): # Draw Request options :Id 1/ Port Nnumber 2 ||| mode: 0:normal / 1: one DNS
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    list = []
    graphName = ''
    graphTitle = ''
    requestCount = objects.__len__()
    store_Path = ''
    if requestCount > MINNUMBER_DrawGraph:
        if(option == 1):  # ID/PORT graph
            for obj in objects:
                list.append((obj.requestId,obj.srcPort))
            graphName ='Request Id/PORT Number'
            graphTitle= 'Request IDs and Port Number Distribution  -  Requests: ' + str(requestCount)

        try:
            Path = "Graphs/%s.png" % (graphName)

            list.sort()
            unique_List = Counter(list)
            #unique_List = ExitNodelist
            #set(unique_List)
            x = []
            y = []
            z =[]
            markersize = 0.1
            index = 0


            for obj in unique_List:
                index += 1
                #print(index)
                portNumberVal = int(obj[0])
                requestIDVal = int(obj[1])
                freg = int(unique_List[obj])
                if freg > 3:
                    print(obj)
                x.append(portNumberVal)
                y.append(requestIDVal)
                z.append(freg)
                #if index ==10000:
                 #   break

            ax.scatter(x, y, z, c='r', marker='.' ,s=0.1)#, #markersize=markersize)
            #ax.ylim([-5000, 80000])  # fix the 8 axis
            #ax.xlim([-5000, 80000])  # fix the x axis
            #ax.xlabel("PORT")
            #ax.ylabel("ID")
            #ax.title(graphTitle)
            print('savefig0')

            if os.path.isfile(store_Path):
                print('found %s' % store_Path)
                os.remove(store_Path)  # Opt.: os.system("rm "+strFile)
                print(store_Path)
                print('d')

            print('savefig2')
            #plt.savefig(store_Path)
            print('savefig3')

            #plt.clf()
            print('savefig4')

            plt.show()
        except Exception as ex:
            print('In drawGraph: ' + str(ex))

# write/log all the files into json file - EVERYTHING
def writeAllTextFiles(all): #
    with open('JSON/AllTextFiles.json', 'w') as F:
        # Use the json dumps method to write the ExitNodelist to disk
        #print(AllLINE.__len__())
        F.write(json.dumps(all, default=dumper))
        print('writing all text files is done')

# write/logs all the Requests into json file - SEMI-FILTERED
def writeAllRequests(requests):
    with open('JSON/AllRequestsInfo.json', 'w') as F:
        # Use the json dumps method to write the ExitNodelist to disk
        print(requests.__len__())
        F.write(json.dumps(requests, default=dumper))
        print('writing all requests info is done')


def getAllDNSIPs(requests):
        listDNSTemp = []
        for obj in requests:
            listDNSTemp.append(obj.srcIP)
        listDNSTemp = set(listDNSTemp)
        #list = json.loads(listDNSTemp)
        with open('JSON/AllDNSIPsFiles.txt', 'w') as F:
            for obj in listDNSTemp:
                F.writelines(obj+'\n')

        print('writing all DNS IPs into a text file is done')

#   write the Requests into json file - for espicall port/Ip - for debugging purposes
#   unfortunately this method is not accurate, because we check if ID/PORT are in the text but we can't tell which one is the PORT or which one is ID
def writeInfoForSpicalIP(IP,requests,ID=None,PORT=None,DRAW=False,index=0):
    list = []
    temp_Requests = []

    txtFiles = glob.glob(FILE_PATH)
    if ID is not None and  PORT is not None:

        filename = ('JSON/ByIP/IP_%s_ID_%s_PORT_%s.json' % (IP, ID, PORT))
        for line in requests:
            if IP in line.srcIP and ID in line.requestId and PORT in line.srcPort:
                #temp_Requests.append(line)
                list.append(line)

        # ID = ' '+ID+' '
        # PORT = ' '+PORT+' '
        # filename = ('JSON/ByIP/IP_%s_ID_%s_PORT_%s.json' % (IP, ID, PORT))
        # for txtfile in txtFiles:
        #     with open(txtfile) as file:
        #         for line in file:
        #             if IP in line and ID in line and PORT in line:  # unfortunately this method is not accurate || 5% to 10%  error margin
        #                 list.append(line)

    elif ID is not None:
        filename = ('JSON/ByID/IP_%s_ID_%s.json' % (IP, ID))
        #ID = ' '+ID+' '
        for line in requests:
            if IP in line.srcIP and ID in line.requestId:
                temp_Requests.append(line)
                list.append(line)

    # elif PORT is not None:
    #     filename = ('JSON/ByPort/IP_%s_PORT_%s.json' % (IP, PORT))
    #     PORT = ' '+PORT+' '
    #     for txtfile in txtFiles:
    #         with open(txtfile) as file:    # unfortunately this method is not accurate
    #             for line in file:
    #                 if IP in line and PORT in line:
    #                     info = line.split('|')
    #                     temp_Requests.append(filterLine(info))
    #                     list.append(line)
    elif PORT is not None:
        filename = ('JSON/ByPort/IP_%s_PORT_%s.json' % (IP, PORT))
        for line in requests:
            if IP in line.srcIP and PORT in line.srcPort:
                temp_Requests.append(line)
                list.append(line)
    # else:
    #     filename = ('JSON/ByIP/IP_%s.json' % IP)
    #     for txtfile in txtFiles:
    #         with open(txtfile) as file:  # accurate 100%
    #             for line in file:
    #                 if IP in line:
    #                     info = line.split('|')
    #                     temp_Requests.append(filterLine(info))
    #                     list.append(line)
    else:
        filename = ('JSON/ByIP/IP_%s.json' % IP)
        for line in requests:
            if IP == line.srcIP:
                temp_Requests.append(line)
                list.append(line)

    if list.__len__() > MINNUMBER_DrawGraph:
        print("JSON file are stored %s" % filename)
        with open(filename, 'w') as F:
            # Use the json dumps method to write the ExitNodelist to disk
            F.write(json.dumps(list, default=dumper))
            print('Writing All Requests Info is done :  %s' % str(list.__len__()))


    if DRAW is True:
        # TODO: add enum
        requestCount = temp_Requests.__len__()
        if requestCount > MINNUMBER_DrawGraph:
            drawGraph(temp_Requests,option=1,mode=1) # Request Ids
            drawGraph(temp_Requests,option=2,mode=1) # port Number
        else:
            Helper.printOnScreenAlways('%d - Ignored: %s - Requests: %d' % (index,temp_Requests[0].srcIP, requestCount),
                                       MSG_TYPES.YELLOW)



def DrawGraphsForAll(requests):
    listDNSTemp = []
    for obj in requests:
        listDNSTemp.append(obj.srcIP)
    listDNSTemp = set(listDNSTemp)
    index = 1;
    for ip in listDNSTemp:
        writeInfoForSpicalIP(ip, requests,DRAW=True,index=index)
        index= index +1

# make the directories in case they are missing
def makeDirectories():

    if not os.path.exists('Graphs'):
        os.makedirs('Graphs/DNS_Graphs')
        os.makedirs('Graphs/DNS_Graphs/ByID')
        os.makedirs('Graphs/DNS_Graphs/ByPort')

    elif not os.path.exists('Graphs/DNS_Graphs'):
        os.makedirs('Graphs/DNS_Graphs')
        os.makedirs('Graphs/DNS_Graphs/ByID')
        os.makedirs('Graphs/DNS_Graphs/ByPort')
    else:
        if not os.path.exists('Graphs/DNS_Graphs/ByID'):
            os.makedirs('Graphs/DNS_Graphs/ByID')
        if not os.path.exists('Graphs/DNS_Graphs/ByPort'):
            os.makedirs('Graphs/DNS_Graphs/ByPort')

    if not os.path.exists('JSON'):
        os.makedirs('JSON/ByID')
        os.makedirs('JSON/ByIP')
        os.makedirs('JSON/ByPort')
    else:
        if not os.path.exists('JSON/ByID'):
            os.makedirs('JSON/ByID')
        if not os.path.exists('JSON/ByIP'):
            os.makedirs('JSON/ByIP')
        if not os.path.exists('JSON/ByPort'):
            os.makedirs('JSON/ByPort')

def timing(f):
    def wrap(*args):
        time1 = time.time()
        ret = f(*args)
        time2 = time.time()
        print('{:s} function took {:.3f} ms'.format(f.__name__, (time2-time1)*1000.0))

        return ret
    return wrap

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


def graphTask():
    # make the directories in case they are missing
    makeDirectories()

    DrawGraphsforALL = False
    # Helper.printOnScreenAlways("TEST",MSG_TYPES.RESULT)
    print('Files Directory: %s' % FILE_PATH)
    total, requests,all = getInfoFormTextFiles()
    print('Found %d records: ' % total)

    # TODO: need to be refactored/renamed- be more clear
    writeAllTextFiles(all)
    # write all the Requests into json file
    #writeAllRequests(all)
    writeAllRequests(requests)
    getAllDNSIPs(requests)

    # match DNS with its port/ID they used.
    # normalizeDNSRequests(Requests)

    # for getting info for especial ip, port and ID
    # draw graphs for all the DNS records
    if DrawGraphsforALL is True:
        # print('Draw Graphs for each DNS records that has more than %d records...' % MINNUMBER_DrawGraph)
        Helper.printOnScreenAlways('Draw Graphs for each DNS that has more than %d records...' % MINNUMBER_DrawGraph,
                                   MSG_TYPES.RESULT)
        DrawGraphsForAll(requests)
        Helper.printOnScreenAlways('Done, Graphs are stored in the following directory: Graphs/DNS_Graphs/',
                                   MSG_TYPES.RESULT)

    drawGraphIDPORTNumber(requests, 1)



    # writeInfoForSpicalIP('23.129.64.1',DRAW=True)
    # writeInfoForSpicalIP('23.129.64.1',ID='51025')
    # writeInfoForSpicalIP('23.129.64.1',ID='51025')

    ##writeInfoForSpicalIP('62.210.17.74')
    # writeInfoForSpicalIP('62.210.17.74',ID='8691')
    # writeInfoForSpicalIP('62.210.17.74',ID='39838')
    # writeInfoForSpicalIP('62.210.17.74',ID='18093')
    # writeInfoForSpicalIP('23.129.64.1',ID='57739')

    # writeInfoForSpicalIP('149.20.48.31',ID='49324')
    # writeInfoForSpicalIP('149.20.48.31',ID='49589')
    # writeInfoForSpicalIP('149.20.48.31',ID='48774')
    # writeInfoForSpicalIP('149.20.48.31',ID='59194')


    # drawGraphIDPORTNumber3D(requests,1)
    # drawGraph(requests, 1)  # Request Ids
    # drawGraph(requests, 2)  # port Number


    # drawGraph(Requests, 3) # port + number
    # drawMix(Requests, 4) # port - number


def GetAllResolversInfo():
    #pool = Pool(processes=4)
    #https://stackoverflow.com/questions/19080792/run-separate-processes-in-parallel-python

    # list = json.loads(listDNSTemp)
    list
    index = 1
    with open('JSON/AllDNSResolversInfo.json') as f:
        json_Objects = json.load(f)
        # Random
        #random.shuffle(json_Objects)

    accessible = 0
    inaccessible = 0
    for node in json_Objects:
        accesse = node[1]
        if accesse == True:
            accessible +=1
        elif accesse == False:
            inaccessible +=1

    print('%d DNS resolver can be accessible directly' % accessible)

    print('%d DNS resolver cannot be accessible directly' % inaccessible)


        #fingerprint = str(obj['ExitNode']['Fingerprint'].encode("ascii"), 'utf-8')



def ResolverTask():

    # Helper.printOnScreenAlways("TEST",MSG_TYPES.RESULT)
    print('Files Directory: %s' % FILE_PATH)
    total, requests, all = getInfoFormTextFiles()
    print('Found %d records: ' % total)

    # TODO: need to be refactored/renamed- be more clear
    #writeAllTextFiles(all)
    # write all the Requests into json file
    #writeAllRequests(requests)
    getAllDNSIPs(requests=requests)
    CheckForPubliclyAccessible()

from multiprocessing import Pool

def CheckForPubliclyAccessible():
    #pool = Pool(processes=4)
    #https://stackoverflow.com/questions/19080792/run-separate-processes-in-parallel-python
    listDNSTempIP = []
    listDNSTemp = []
    # list = json.loads(listDNSTemp)
    index = 1
    with open('JSON/AllDNSIPsFiles.txt', 'r') as file:
        for obj in file:
            obj= obj.rstrip()
            listDNSTempIP.append(obj)

    for IP in listDNSTempIP:
        connected = checkDNSIP(IP)
        print('%d - %s : %s' % (index, IP ,str(connected)))
        listDNSTemp.append([IP,connected])
        index += 1


    #print(listDNSTemp)
    with open('JSON/AllDNSResolversInfo.json', 'w') as F:
        # Use the json dumps method to write the ExitNodelist to disk
        F.write(json.dumps(listDNSTemp, default=dumper))
        print('writing all requests info is done')
    print('writing all DNS IPs into a text file is done')

def checkDNSIP(ip):
    #ip = '8.8.8.8'
    try:
        command = 'dig +short +tries=1 DNS_Checker.dnstestsuite.space @%s' % ip
        #print(command)
        #result = subprocess.check_call(command, stdout=devnull, stderr=subprocess.STDOUT)
        result = check_output(command,  shell=True) #stdout=DEVNULL, stderr=STDOUT)
        if result.decode("utf-8").rstrip() == '52.20.33.59': #ip address of the website
            return True
        else:
            return False
    except Exception as ex:
        return False
    return False


#   TODO: add options : 1- fetch the new files or process the old ones
if __name__ == '__main__':
    graphTask()
    #ResolverTask()
    #GetAllResolversInfo()