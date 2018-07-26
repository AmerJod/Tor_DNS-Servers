import glob
import json
import random
import matplotlib.pyplot as plt
from collections import Counter



plt.style.use('seaborn')
Requests = []   # to store all the requests from text file
AllLINE = []    # to store all the lines from text file
DNSs = []
MAXNUMBER = -1 ## -1 means parse all the files

# TODO: Need to be Dynamic
FILR_PATH ='C:\\DNS9_back_new_logo_3/*.txt'

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
    request  = RequestInfo(RequestId_,SrcIP_,SrcPort_)
    # Add the instance to  Requests List
    Requests.append(request)

def findValue(value):
    info = value.split(':')
    return info[1].strip() # get the second part of the list, For exmaple: portNumber : 39879

# get info form text file and store it in list and return the total numbe
def getInfoFormTextFiles():
    totalLines = 0
    first = True
    # TODO: this should be dynamic
    txtFiles = glob.glob(FILR_PATH)
    previousPortNumber = ''
    previousRequestId = ''
    for txtfile in txtFiles:
        with open(txtfile) as file:
            for line in file:
                if 'RecordType' in line  or 'Domain' in line or 'RequestId' in line:
                    # get all the legitimate/reasonable records/lines from the text fileS
                    AllLINE.append(line) # all the records
                    info = line.split('|')
                    # filter line, get request, IP and port number form the text.
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
                    if first is True: # To avoid request repetation
                        previousPortNumber = SrcPort_
                        previousRequestId =RequestId_
                        first= False
                        filterLine(info)
                        totalLines += 1
                    elif previousPortNumber != SrcPort_ and previousRequestId != RequestId_:
                        filterLine(info)
                        previousPortNumber = SrcPort_
                        previousRequestId = RequestId_
                        totalLines += 1
    return totalLines

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
        index+=1
    #

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

    #print(json.dumps(listDNS, default=dumper))
    with open('JSON/DnsFilterList.json', 'w') as F:
        # Use the json dumps method to write the list to disk
        F.write(json.dumps(listDNS, default=dumper))
        print('writing listDNS is done')


def drawGraph(objects, option): # Draw Request Id 1/ Port Nnumber 2
    list = []
    graphName = ''
    graphTitle = ''

    if(option == 1):
        for i in objects:
            list.append(i.requestId)
            graphName ='Request Id'
            graphTitle= 'Request IDs Distribution'

    elif(option == 2):
        for i in objects:
            list.append(i.srcPort)
            graphName ='Port Numbers'
            graphTitle = 'Port Number Distribution'
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

    list.sort()
    list2 = Counter(list)
    set(list2)
    x = []
    y = []

    for i in list2:
        newVal = int(i)
        newValFeq = random.uniform(-0.5,0.5) + float(list2[i]) # add some noise to help to read the graph
        #newValFeq = float(list2[i])
        x.append(newVal)
        y.append(newValFeq)

    plt.plot(x, y, linestyle='', marker='o', markersize=0.7)
    plt.xlabel(graphName)
    plt.ylabel("Frequency")
    plt.title(graphTitle)
    plt.savefig("Graphs/%s.png" % graphName)
    plt.show()


# write all the files into json file
def writeAllTextFiles():
    with open('JSON/AllTextFiles.json', 'w') as F:
        # Use the json dumps method to write the list to disk
        print(AllLINE.__len__())
        F.write(json.dumps(AllLINE, default=dumper))
        print('writing AllRequestsInfo is done')

# write all the Requests into json file
def writeAllRequests():
    with open('JSON/AllRequestsInfo.json', 'w') as F:
        # Use the json dumps method to write the list to disk
        F.write(json.dumps(Requests, default=dumper))
        print('writing AllRequestsInfo is done')

#   write the Requests into json file - for espicall port/Ip - for debugging purposes
#   unfortunately this method is not accurate, because we check if ID/PORT are in the text but we can't tell which one is the PORT or which one is ID
def writeInfoForSpicalIP(IP,ID=None,PORT=None):
    list =[]

    txtFiles = glob.glob(FILR_PATH)
    if ID is not None and  PORT is not None:
        ID = ' '+ID+' '
        PORT = ' '+PORT+' '
        filename = ('JSON/IP_%s_ID_%s_PORT_%s.json' % (IP, ID, PORT))
        for txtfile in txtFiles:
            with open(txtfile) as file:
                for line in file:
                    if IP in line and ID in line and PORT in line:  # unfortunately this method is not accurate
                        list.append(line)

    elif ID is not None:
        filename = ('JSON/IP_%s_ID_%s.json' % (IP, ID))
        ID = ' '+ID+' '
        for txtfile in txtFiles:
            with open(txtfile) as file:
                for line in file:
                    if IP in line and ID in line:   # unfortunately this method is not accurate
                        list.append(line)

    elif PORT is not None:
        filename = ('JSON/IP_%s_PORT_%s.json' % (IP, PORT))
        PORT = ' '+PORT+' '
        for txtfile in txtFiles:
            with open(txtfile) as file:    # unfortunately this method is not accurate
                for line in file:
                    if IP in line and PORT in line:
                        list.append(line)
    else:
        filename = ('JSON/IP_%s.json' % IP)
        for txtfile in txtFiles:
            with open(txtfile) as file:  # accurate
                for line in file:
                    if IP in line:
                        list.append(line)

    with open(filename, 'w') as F:
        # Use the json dumps method to write the list to disk
        F.write(json.dumps(list, default=dumper))
        print('writing AllRequestsInfo is done')

if __name__ == '__main__':

    total = getInfoFormTextFiles()
    print('Text files: '+ str(total))
    print(Requests.__len__())

    #writeAllTextFiles()
    # write all the Requests into json file
    #writeAllRequests()

    # match DNS with its port/ID they used.
    #normalizeDNSRequests(Requests)

    # for getting info for especial ip, port and ID
    #writeInfoForSpicalIP('23.129.64.1',ID='51025')
    #writeInfoForSpicalIP('23.129.64.1',ID='51025')
    #writeInfoForSpicalIP('23.129.64.1',ID='51025')
    ##writeInfoForSpicalIP('62.210.17.74')
    #writeInfoForSpicalIP('62.210.17.74',ID='8691')
    #writeInfoForSpicalIP('62.210.17.74',ID='39838')
    #writeInfoForSpicalIP('62.210.17.74',ID='18093')
    #writeInfoForSpicalIP('23.129.64.1',ID='57739')

    writeInfoForSpicalIP('149.20.48.31',ID='49324')
    writeInfoForSpicalIP('149.20.48.31',ID='49589')
    writeInfoForSpicalIP('149.20.48.31',ID='48774')
    writeInfoForSpicalIP('149.20.48.31',ID='59194')





    #drawGraph(Requests, 1) # Request Ids
    #drawGraph(Requests, 2) # port Number
    #drawGraph(Requests, 3) # port + number
    #drawMix(Requests, 4) # port - number