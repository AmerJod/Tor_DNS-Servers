import glob
import random
import matplotlib.pyplot as plt
from collections import Counter

plt.style.use('seaborn')
Requests = []

class RequestInfo():
    def __init__(self,requestId, srcIp,srcPort):
        self.requestId = requestId
        self.srcIp = srcIp
        self.srcPort = srcPort

def filterLine(info):
    RequestId = 're'
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
    # TODO: this should be dynamic
    txtFiles = glob.glob('C:\\DNS9_back_new2-logs2/*.txt')
    for txtfile in txtFiles:
        with open(txtfile) as file:
            for line in file:
                if 'RecordType' in line  or 'Domain' in line or 'RequestId' in line:
                    info = line.split('|')
                    # filter line, get request, IP and port number form the text.
                    filterLine(info)
                    totalLines += 1
    return totalLines

def draw(objects , option): # Draw Request Id 1/ Port Nnumber 2
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

    list.sort()
    list2 = Counter(list)
    set(list2)
    x = []
    y = []


    for i in list2:
        newVal = int(i)
        newValFeq = random.uniform(-0.5,0.5) + float(list2[i]) # add some noise to help to read the graph
        x.append(newVal)
        y.append(newValFeq)

    plt.plot(x, y, linestyle='', marker='o', markersize=0.7)
    plt.xlabel(graphName)
    plt.ylabel("Frequency")
    plt.title(graphTitle)
    plt.savefig("Graphs/%s.png" % graphName)
    plt.show()


if __name__ == '__main__':
    total = getInfoFormTextFiles()
    print('Text files: '+ str(total))
    print(Requests.__len__())

    draw(Requests, 1) # Request Ids
    draw(Requests, 2) # port Number



