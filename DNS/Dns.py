import datetime
import getopt
import json
import os
import socket
import glob
import sys
import logging

VERSION = '0.6'

DEBUG = False
PORT = 53
IP_ADDRESS_LOCAL = '127.0.0.1'
IP_ADDRESS_SERVER = '172.31.16.226'
COUNTER = 0
JsonRequestsPATH = 'JSON/DNSRequestNodes'


RECORD_TYPES = {
    '\x00\x01': 'A',
    '\x00\x05': 'CNAME',
    '\x00\x0f': 'MX',
    '\x00\x02': 'NS',
    '\x00\x10': 'TXT',
    '\x00\x1c': 'AAAA',
    '\x00\xff': 'ANY',
}

# TODO: Need refactor- NOT IMPORTANT
def printDebugMode(values):
    if DEBUG is True:  # Debug mode only
        for string in values:
            print(string)

# option: 1 full (time+date)
# option: 2 date
# option: 3 time
def getTime(opt = 1):
    date = datetime.datetime.now()
    if opt == 1:    # full
        return (((str(date)).split('.')[0]).split(' ')[1] + ' ' + ((str(date)).split('.')[0]).split(' ')[0])
    if opt == 2:    # date
        return (((str(date)).split('.')[0]).split(' ')[0])
    if opt == 3:    # time
        return (((str(date)).split('.')[0]).split(' ')[1])
def int_to_hex(value, zfill=None):
    h = hex(value)  # 300 -> '0x12c'
    h = h[2:].zfill((zfill or 0) * 2)  # '0x12c' -> '00012c' if zfill=3
    return h.decode('hex')
def bin_to_hex(value):
    # http://stackoverflow.com/questions/2072351/python-conversion-from-binary-string-to-hexadecimal/2072384#2072384
    # '0000 0100 1000 1101' -> '\x04\x8d'
    value = value.replace(' ', '')
    h = '%0*X' % ((len(value) + 3) // 4, int(value, 2))
    return h.decode('hex')


class Log():
    def __init__(self, filename, mode='none'):
        date = getTime(2)
        self.file = 'Logs/'+filename+'_'+date+'.log'     # This is hard coded but you could make dynamic
        self.mode = mode
        if (os.path.exists(self.file)) != True:
            with open(self.file, 'w+') as file:
                file.write('Start - '+date +'\n')

        # TODO: need refactoring - make it more abstract
        self.file = 'Logs/'+filename+'_'+date+'_counter+.txt'
        if (os.path.exists(self.file)) != True:
            with open(self.file, 'w+') as file:
                file.write('Start - '+date +'\n')

    def wirteIntoFile(self,raw):
        if self.mode == 'out':
            data = ''
            raw = str(getTime(3)) + ': ' + raw
            with open(self.file, 'r') as file:
                data = file.read()
            with open(self.file, 'w+') as file:
                file.write(data)
                file.write(raw + '\n')

    def counter(self):
        pass

# TODO: need to implemant a class
def storeDNSRequestJSON(status,time,srcIP,srcPort,domain):
    """Help for the bar method of Foo classes"""
    date = getTime(2)
    # TODO: need refactoring - make it more abstract
    file = JsonRequestsPATH +'_'+ date + '.json'
    jsons = {}

    if (os.path.exists(file)) != True: # check if the file exist, if not create it.
        with open(file, 'w+') as jsonfile:
            json.dump(' ', jsonfile)
    else:
        with open(file, 'r') as jsonfile:
            jsons = json.load(jsonfile)

    with open(file,'w') as jsonfile:
        DNSRequestNodes = {
            'Request': {
                'Status': status,
                'ID':  str(len(jsons)+1),
                'Time': time,
                'SrcIP': srcIP,
                'SrcPort': srcPort,
                'Domain': domain
            }
        }
        jsons[ str(len(jsons)+1)] = DNSRequestNodes
        # Write into Json file
        json.dump(jsons, jsonfile)

#<editor-fold desc="Zone">

# load all zones that we have when the DNS server starts up, and put them into memory
def loadZone():
    jsonZone = {}   # dictionary
    zoneFiles = glob.glob('Zones/*.zone')

    printDebugMode(zoneFiles)   # Debug

    for zone in zoneFiles:
        with open(zone) as zonedata:
            data = json.load(zonedata)
            zoneName = data['$origin']
            jsonZone[zoneName] = data
    return jsonZone


def getZone(domain):
    global ZoneDATA
    try:
        zoneName = '.'.join(domain)
        return ZoneDATA[zoneName]
    except Exception as e:
        return ''

# </editor-fold>

def getFlags(flags):

    response_Flag = ''

    # First byte contains:  QR: 1 bit | Opcode: 4 bits  | AA: 1 bit | TC: 1 bit  |RD: 1 bit
    byte1 = bytes(flags[:1])
    # Second byte contains:  RA: 1 bit | Z: 3 bits  | RCODE: 4 bit
    byte2 = bytes(flags[1:2])

    QR = '1'    # query: 0 , response: 0.
    # OPCODE
    OPCODE = ''
    for bit in range(1,5):
        OPCODE += str(ord(byte1) & (1 << bit))  # to get option 1/0
    #   Authoritative Answer
    AA = '1'  # Always 1
    # TrunCation
    TC = '0'    # 0 because we always dealing with a short message
    # Recursion Desired
    RD = '0'    # 0 if it is not supported recurring
    # Recursion Available
    RA = '0'

    # Reserved for future use.  Must be zeros in all queries and responses.
    Z= '000'

    # Response code
    RCODE = '0000'

    response_Flag = int(QR+OPCODE+AA+TC+RD, 2).to_bytes(1, byteorder='big') + int(RA+Z+RCODE).to_bytes(1, byteorder='big')

    return response_Flag
def getQuestionDomain(data):
    state = 0
    expectedlength = 0
    domainstring = ''
    domainparts = []
    x = 0
    y = 0
    for byte in data:
        if state == 1:
            if byte != 0:
                domainstring += chr(byte)
            x += 1
            if x == expectedlength:
                domainparts.append(domainstring)
                domainstring = ''
                state = 0
                x = 0
            if byte == 0:
                domainparts.append(domainstring)
                break
        else:
            state = 1
            expectedlength = byte
        y += 1

    questiontype = data[y:y+2]

    return (domainparts, questiontype)
def getRecs(data):
    try:
        domain, questionType = getQuestionDomain(data)
        qt = ''
        if questionType == b'\x00\x01':
            qt = 'a'

        #print(domain)
        zone = getZone(domain)
        if DEBUG is True:  # Debug mode only
            print('-------------7')
            print(qt)
            '''
            print('Question Type: ' + str(qt))
            print('Zone: ' + str(zone[qt]))
            print('-------------5')
            print('Question Type: ' + str(qt))
            print('-------------6')
            '''

        return (zone[qt], qt, domain)
    except:
        return ('', 'ERROR', domain)
def buildQuestion(domainName, recordType): # convert str into byte
    questionBytes = b''

    for part in domainName:
        length = len(part)
        questionBytes += bytes([length])

        for char in part:
            questionBytes += ord(char).to_bytes(1, byteorder='big')

    if recordType == 'a':
        questionBytes += (1).to_bytes(2, byteorder='big')

    questionBytes += (1).to_bytes(2, byteorder='big')
    return questionBytes
def recordToBytes(domainName, recordType, recordTTL, recordValue):

    recordBytes = b'\xc0\x0c'
    if recordType == 'a':
        recordBytes = recordBytes + bytes([0]) + bytes([1])

    recordBytes = recordBytes + bytes([0]) + bytes([1])

    recordBytes += int(recordTTL).to_bytes(4 , byteorder='big')

    if recordType == 'a':
        recordBytes = recordBytes + bytes([0]) + bytes([4])

        for part in recordValue.split('.'):
            recordBytes += bytes([int(part)])

    return recordBytes
def getResponse(data, addr):

    # ********************************** DNS Header
    # Transaction ID
    TransactionID_Byte = data[:2]
    TransactionID = ''
    for byte in TransactionID_Byte:
        TransactionID += hex(byte)[2:]
    if DEBUG is True:  # Debug mode only
        print(TransactionID)


    # FLAGS
    Flags = getFlags(data[2:4])
    if DEBUG is True: # Debug mode only
        print(Flags)

    # Question Count, how many questions in the zone file
    QDCOUNT = b'\x00\x01'   # dns has one question

    # Answer Count
    ANCOUNT = len(getRecs(data[12:])[0]).to_bytes(2, byteorder='big')  # 12 bytes to skip the header

    # Name server count
    NSCOUNT = (0).to_bytes(2, byteorder='big')

    # Additional count
    ARCOUNT = (0).to_bytes(2, byteorder='big')

    DNSHeader = TransactionID_Byte + Flags + QDCOUNT + ANCOUNT + NSCOUNT + ARCOUNT
    if DEBUG is True:
        dnsH = ''
        print('DNS HEADER: ' + str(DNSHeader))
        for byte in DNSHeader:
            dnsH += hex(byte)[2:]

        print(dnsH)

    # ********************************** DNS Question

    records, recordType, domainName = getRecs(data[12:])

    global COUNTER
    COUNTER += 1

    domain = '.'.join(map(str, domainName))
    if recordType == 'ERROR':
        log_incoming(str(COUNTER)+'-** ERROR ** : SrcIP: ' + addr[0] + '  |  SrcPort: ' + str(addr[1]) + '  |  Domain: ' + domain)
        storeDNSRequestJSON('ERROR',getTime(3),addr[0] ,str(addr[1]),domain)
    else:
        log_incoming(str(COUNTER)+'- SrcIP: ' + addr[0] + '  |  SrcPort: ' + str(addr[1]) + '  |  Domain : ' + domain)
        storeDNSRequestJSON('Okay', getTime(3), addr[0], str(addr[1]), domain)


    print(str(COUNTER) +'- Request form: ' + addr[0] +'  - Domain : ' + '.'.join(map(str, domainName)) + '\n')

    DNSQuestion = buildQuestion(domainName, recordType)
    if DEBUG is True:
        print('DNSQuestion: ' + str(DNSQuestion))

    # ********************************** DNS Body

    DNSBody = b''

    for record in records:
        DNSBody += recordToBytes(domainName, recordType, record['ttl'], record['value'])

    if DEBUG is True:
        print(DNSBody)

    return DNSHeader + DNSQuestion + DNSBody

def main(argv):
    # gather Zone info and store it into memory
    global ZoneDATA
    ZoneDATA = loadZone()

    '''
    try:
        opts, args = getopt.getopt(argv, 'l:s')
    except getopt.GetoptError:
        print('test.py -l')
        sys.exit(2)
    '''
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    opts = argv

    for opt in opts:
        if opt == '-s':
            sock.bind((IP_ADDRESS_SERVER, PORT))
        elif opt == '-l' or opt == '':
            sock.bind((IP_ADDRESS_LOCAL, PORT))
    # open socket and

    # keep listening
    while 1:
        data, addr = sock.recvfrom(512)
        response = getResponse(data, addr)
        sock.sendto(response, addr)
def main_test():
    # gather Zone info and store it into memory
    global ZoneDATA
    ZoneDATA = loadZone()

    '''
    try:
        opts, args = getopt.getopt(argv, 'l:s')
    except getopt.GetoptError:
        print('test.py -l')
        sys.exit(2)
    '''
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((IP_ADDRESS_LOCAL, PORT))
    # open socket and

    # keep listening
    while 1:
        data, addr = sock.recvfrom(512)
        response = getResponse(data, addr)
        sock.sendto(response, addr)



def log_incoming(value):
    file = Log(filename='incoming_request',mode='out')
    file.wirteIntoFile(value)


if __name__ == '__main__':
    print('Starting Mini DNS Server.. v%s' % VERSION)
    main(sys.argv[1:])
    #main_test()
