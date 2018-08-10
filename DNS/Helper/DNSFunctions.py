'''

This file contains functions to DNS server to complete its tasks.

'''

import datetime
import os
import json
import glob
import random
import logging
import logging.config
import traceback

from stem.util import term
from enum import Enum

from .Helper import Helper
from .Helper import MSG_TYPES
from .Helper import LogData


JSON_REQUESTS_PATH = 'JSON/NormalRequests/DNSRequestNodes'
JSON_REQUESTS_PATH_CHECK = 'JSON/CheckingRequests/DNSRequestNodes' # store all the request about checkoing if the dns supports 0x20 code
ERRORS_LOG_PATH = 'Logs/Errors/'

DEBUG = False
COUNTER = 0


#<editor-fold desc="******************* General Tools *******************">

class RECORD_TYPES(Enum):
    A       = b'\x00\x01'  # specifies  IP4 Address
    CNAME   = b'\x00\x05'  # aliases
    MX      = b'\x00\x0f'  # mail exchange server for DNS
    NS      = b'\x00\x02'  # authoritative name server
    TXT     = b'\x00\x10'  # arbitrary non-formatted text string.
    AAAA    = b'\x00\x1c'  # specifies IP6 Address
    ANY     = b'\x00\xff'

# class TASK_MODE(Enum):
#     request = '-out'
#     TorconnectionChecking = '-none'
#
def setDebuggingMode(debug):
    DEBUG = debug

#
def setAdversaryMode(adversary_mode):
    ADVERSARY_MODE = adversary_mode

#
def loggingData(value):
    file = LogData(filename='incoming_request', mode='out')
    file.wirteIntoFile(value)

#
def killprocess(port):
    try:
        os.system('freeport %s' % port)
        #printOnScreenAlways('DNS port has been released',term.Color.GREEN)
    except Exception as ex:
        logging.error('DNSFunctions - killprocess: %s' % ex)

#
def printLogo(version,modifyDate):
    try:
        print(term.format(('\n                           Starting Mini DNS Server.. v%s ' % version + modifyDate), term.Color.YELLOW))
        with open('Logo/logo.txt', 'r') as f:
            lineArr = f.read()
            print(term.format(str(lineArr),term.Color.GREEN))
        with open('Logo/logo2.txt', 'r') as f:
            lineArr = f.read()
            print(term.format(str(lineArr),term.Color.RED))
    except Exception as ex:
        logging.error('printLogo - ' + str(ex))

# TODO: Need refactor- NOT IMPORTANT
# option: 1 full (time+date)
# option: 2 date
# option: 3 time
def printDebugMode(values):
    if DEBUG is True:  # Debug mode only
        for string in values:
            print(string)

#   make the directories in case they are missing
def makeDirectories():
    try:

        if not os.path.exists('JSON'):
            os.makedirs('JSON/CheckingRequests')
            os.makedirs('JSON/NormalRequests')
        else:
            if not os.path.exists('JSON/CheckingRequests'):
                os.makedirs('JSON/CheckingRequests')
            if not os.path.exists('JSON/NormalRequests'):
                os.makedirs('JSON/NormalRequests')

        if not os.path.exists('Logs'):
            os.makedirs('Logs')
            os.makedirs('Logs/Errors')

        if not os.path.exists('Logs/Errors'):
            os.makedirs('Logs/Errors')

    except Exception as ex:
        Helper.printOnScreenAlways(ex, term.Color.RED)
        logging.error('DNSFunctions - makeDirectories: %s' % traceback.format_exc())


#
def int_to_hex(value, zfill=None):
    h = hex(value)  # 300 -> '0x12c'
    h = h[2:].zfill((zfill or 0) * 2)  # '0x12c' -> '00012c' if zfill=3
    return h.decode('hex')

#
def bin_to_hex(value):
    # http://stackoverflow.com/questions/2072351/python-conversion-from-binary-string-to-hexadecimal/2072384#2072384
    # '0000 0100 1000 1101' -> '\x04\x8d'
    value = value.replace(' ', '')
    h = '%0*X' % ((len(value) + 3) // 4, int(value, 2))
    return h.decode('hex')

# TODO: need to implement a class
def storeDNSRequestJSON(status, time, recordType, transactionID, srcIP, srcPort, domain, modifiedDomain='none', mode='none'):
    """Help for the bar method of Foo classes"""
    date = Helper.getTime(2)
    pathDirt = ''
    if mode == 'check':
        path = JSON_REQUESTS_PATH_CHECK
    else:
        # TODO: need refactoring - make it more abstract
        path = JSON_REQUESTS_PATH

    pathFile = ('%s_%s.json' % (path,date))

    jsons = {}

    if (os.path.exists(pathFile)) != True:  # check if the file exist, if not create it.
        with open(pathFile, 'w+') as jsonfile: # not exist
            json.dump(' ', jsonfile)
    else:
        try:
            with open(pathFile, 'r') as jsonfile:
                jsons = json.load(jsonfile)

        except ValueError as er:
            logging.error('DNSFunction - storeDNSRequestJSON - JSON invalid - file: %s : %s' % (path,str(er)))
            os.rename(pathFile, ('%s_%s_error_%d.json' % (path,date,random.randint(1,50))))

            with open(pathFile, 'a+') as jsonfile:
                    json.dump(' ', jsonfile)

    if domain[-1:] == '.':
        domain = domain[:-1]

    with open(pathFile,'w') as jsonfile:
        DNSRequestNodes = {
            'Request': {
                'ID': str(len(jsons) + 1),
                'Time': time,
                'Status': status,
                'TransactionID':transactionID,
                'RecordType':recordType,
                'SrcIP': srcIP,
                'SrcPort': srcPort,
                'Domain': domain,
                'modifiedDomain' : modifiedDomain,
            }
        }
        jsons[ str(len(jsons)+1)] = DNSRequestNodes
        # Write into Json file
        json.dump(jsons, jsonfile)

#
def storeDNSRequestJSONText(status, time, recordType, transactionID, srcIP, srcPort, domain, modifiedDomain='none', mode='none'):
    """Help for the bar method of Foo classes"""
    date = Helper.getTime(2)

    if mode == 'check':
        file = JSON_REQUESTS_PATH_CHECK + '_' + date + '.json'
    else:
        # TODO: need refactoring - make it more abstract
        file = JSON_REQUESTS_PATH + '_' + date + '.json'


    jsons = {}

    if (os.path.exists(file)) != True:  # check if the file exist, if not create it.
        with open(file, 'w+') as jsonfile:
            json.dump(' ', jsonfile)
    else:
        with open(file, 'r') as jsonfile:
            jsons = json.load(jsonfile)


    if domain[-1:] == '.':
        domain = domain[:-1]


    row ='"%d": { "Request" : {' \
         '"ID" : str(len(jsons) + 1),"Time": %s,' \
         '"Status": %s,' \
         '"TransactionID": %s,' \
         '"RecordType": %s,' \
         '"SrcIP": %s,' \
         '"SrcPort": %s,' \
         '"Domain": %s,' \
         '"modifiedDomain": %s } },' %(id,time,status,transactionID,recordType,srcIP,srcPort,domain,modifiedDomain)


    with open(file,'w') as jsonfile:
        DNSRequestNodes = {
            'Request': {
                'ID': str(len(jsons) + 1),
                'Time': time,
                'Status': status,
                'TransactionID':transactionID,
                'RecordType':recordType,
                'SrcIP': srcIP,
                'SrcPort': srcPort,
                'Domain': domain,
                'modifiedDomain' : modifiedDomain,
            }
        }
        jsons[ str(len(jsons)+1)] = DNSRequestNodes
        # Write into Json file
        json.dump(jsons, jsonfile)

# </editor-fold>

#<editor-fold desc="******************* Zone File *******************">
# load all zones that we have when the DNS server starts up, and put them into memory
def loadZone():
    global ZONEDATA
    jsonZone = {}   # dictionary
    zoneFiles = glob.glob('Zones/*.zone')
    printDebugMode(zoneFiles) # Debug
    for zone in zoneFiles:
        with open(zone) as zonedata:
            data = json.load(zonedata)
            zoneName = data['$origin']
            jsonZone[zoneName] = data
    ZONEDATA = jsonZone
    Helper.printOnScreenAlways("\n              =--------------**Zone file has been loaded**--------------=",MSG_TYPES.RESULT)

#   get zone and domain name
def getZone(domain):
    global ZONEDATA
    try:
        zoneName = '.'.join(domain[-3:]).lower()
        return ZONEDATA[zoneName]
    except Exception as ex:
        logging.error('DNSFunctions - getZone: \n%s ' % traceback.format_exc())
        return ''

# </editor-fold>

#<editor-fold desc="******************* DNS Tools/Rspoonse *******************">
#
def getFlags(flags):
    response_Flag = ''

    # First byte contains:  QR: 1 bit | Opcode: 4 bits  | AA: 1 bit | TC: 1 bit  |RD: 1 bit
    byte1 = bytes(flags[:1])
    # Second byte contains:  RA: 1 bit | Z: 3 bits  | RCODE: 4 bit
    byte2 = bytes(flags[1:2])

    QR = '1'  # query: 0 , response: 0.
    # OPCODE
    OPCODE = ''
    for bit in range(1, 5):
        OPCODE += str(ord(byte1) & (1 << bit))  # to get option 1/0

    #   Authoritative Answer
    AA = '1'  # Always 1
    # TrunCation
    TC = '0'  # 0 because we always dealing with a short message
    # Recursion Desired
    RD = '0'  # 0 if it is not supported recurring
    # Recursion Available
    RA = '0'

    # Reserved for future use.  Must be zeros in all queries and responses.
    Z = '000'

    # Response code
    RCODE = '0000'

    response_Flag = int(QR + OPCODE + AA + TC + RD, 2).to_bytes(1, byteorder='big') + int(RA + Z + RCODE).to_bytes(1,byteorder='big')
    #response_Flag = int(QR + '0000' + AA + TC + RD, 2).to_bytes(1, byteorder='big') + int(RA + Z + RCODE).to_bytes(1,byteorder='big')

    return response_Flag

#
def getQuestionDomain(data):
    state = 1
    index=0
    first = True

    domainParts =[]
    domainString = ''
    domainTLD = ''

    expectedLength = 0
    TotalLength = 0
    parts = 0
    for byte in data:

        if byte == 0:
            break
        if state == 1:  # 1 get the domain name
            if first is True:  # first byte to get the length for the zone ~ 3 bytes
                first = False
                parts+=1
                expectedLength = byte
                continue
            domainString += chr(byte)
            index += 1
            if index == expectedLength:
                TotalLength += expectedLength
                state = 2
                index = 0
                domainParts.append(domainString)
                domainString=''
                first=True

        elif state == 2:  # 2 get the domain zone
            if first is True:  # first byte to get the length for the zone ~ 3 bytes
                first = False
                expectedLength = byte
                parts+=1 # how many parts
                continue
            domainString += chr(byte)
            index += 1
            if index == expectedLength:
                TotalLength += expectedLength
                state = 1
                index = 0
                domainParts.append(domainString)
                domainString = ''
                first = True
       # else: # get the domain length
        #    state = 1
         #   expectedLength = byte  # get the domain length

    # get question type
    questionTypeStartingIndex = TotalLength + parts
    questionType = data[questionTypeStartingIndex+1: questionTypeStartingIndex+3]
    if DEBUG is True: # Debug mode only
        print('Question Type: ' + str(questionType))
        print('Domain: '+domainString+'.'+domainTLD)

    domainParts.append('')

    #print(domainParts)


    return (domainParts, questionType)

#
def getQuestionDomain_temp(data):
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
            expectedlength = byte # get the lenght for the domain
        y += 1

    questiontype = data[y:y + 2]

    return (domainparts, questiontype)

#
def getLetterCaseSawped(dmoainParts):
    newParts =  dmoainParts[:-3] # save all the elements but  not the last 3  including ''
    dmoainParts = dmoainParts[-3:] # get only last 3 elemnets of the list exmaple.com.
    # modify randomly only in the domain and zone name
    for part in dmoainParts:
        part = "".join(random.choice([k.swapcase(), k ]) for k in part )
        newParts.append(part)
    return newParts

#
def getRecs(data):
    try:
        domain, questionType = getQuestionDomain(data)
        qt = ''
        if questionType == RECORD_TYPES.A.value:
            qt = 'A'
        elif questionType == RECORD_TYPES.AAAA.value:
            qt = 'AAAA'
        elif questionType == RECORD_TYPES.CNAME.value:
            qt = 'CNAME'
        elif questionType == RECORD_TYPES.MX.value:
            qt = 'MX'
        elif questionType == RECORD_TYPES.NS.value:
            qt = 'NS'
        elif questionType == RECORD_TYPES.TXT.value:
            qt = 'TXT'
        elif questionType == RECORD_TYPES.ANY.value:
            qt = 'ANY'

        # print(domain)
        zone = getZone(domain)
        if DEBUG is True:  # Debug mode only
            print('-------------7')

            print('Question Type: ' + str(qt))
            print('Zone: ' + str(zone[qt]))
            print('-------------5')
            print('Question Type: ' + str(qt))
            print('-------------6')


        return (zone[qt], qt, domain,'OKAY')
    except Exception as ex:
        logging.error('DNSFunctions - getRecs: \n%s ' % traceback.format_exc())
        return ('', qt , domain, 'ERROR')

#
def buildQuestion(domainName, recordType):  # convert str into byte
    questionBytes = b''

    for part in domainName:
        length = len(part)
        questionBytes += bytes([length])

        for char in part:
            questionBytes += ord(char).to_bytes(1, byteorder='big')

    if recordType == RECORD_TYPES.A.name or recordType == RECORD_TYPES.AAAA.name:
        questionBytes += (1).to_bytes(2, byteorder='big')

    questionBytes += (1).to_bytes(2, byteorder='big')
    return questionBytes

#
def recordToBytes(domainName, recordType, recordTTL, recordValue):
    recordBytes = b'\xc0\x0c'  # Pointer to domain name
    if recordType == RECORD_TYPES.A.name:
        recordBytes = recordBytes + bytes([0]) + bytes([1])

    # TODO: need to handle IP6-AAAA
    elif recordType == RECORD_TYPES.AAAA.name:
        recordBytes = recordBytes + bytes([0]) + bytes([1])

    recordBytes = recordBytes + bytes([0]) + bytes([1])

    recordBytes += int(recordTTL).to_bytes(4, byteorder='big')

    if recordType == RECORD_TYPES.A.name or recordType == RECORD_TYPES.AAAA.name:
        recordBytes = recordBytes + bytes([0]) + bytes([4])
        for part in recordValue.split('.'):
            recordBytes += bytes([int(part)])


    return recordBytes

#
def getResponse(data, addr,case_sensitive = False):
    # ********************************** DNS Header
    # Transaction ID
    TransactionID_Byte = data[:2]
    TransactionID = ''
    for byte in TransactionID_Byte:
        TransactionID += hex(byte)[2:]
    if DEBUG is True:  # Debug mode only
        print('ID:')
        print(TransactionID)

    # FLAGS
    Flags = getFlags(data[2:4])
    if DEBUG is True:  # Debug mode only
        print(Flags)

    # Question Count, how many questions in the zone file
    QDCOUNT = RECORD_TYPES.A.value #b'\x00\x01'  # dns has one question

    records, recordType, domainName, recStatus = getRecs(data[12:])


    # Answer Count
    #ANCOUNT = len(getRecs(data[12:])[0]).to_bytes(2, byteorder='big')  # 12 bytes to skip the header
    ANCOUNT = len(records).to_bytes(2, byteorder='big')  # 12 bytes to skip the header

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

    #records, recordType, domainName = getRecs(data[12:])

    global COUNTER
    COUNTER += 1
    transactionID= str(int(TransactionID,16))
    domain = '.'.join(map(str, domainName))[:-1]
    status = 'Okay'
    '''
    if recStatus == 'ERROR': # TODO: need to handle the exception in better way
        loggingData(str(COUNTER) + ': ** ERROR ** : RecordType: '+recordType+' | RequestId: '+transactionID+' | SrcIP: ' + addr[0] + '  |  SrcPort: ' + str(addr[1]) + '  |  Domain: ' + domain)
        status = 'ERROR'
        print(term.format(str(
            COUNTER) + ': ' + status + ' -  RecordType: ' + recordType + '  - RequestId: ' + transactionID + '   From: IP ' +  addr[0] + ' : Port: ' + str(addr[1]) + '  -  Domain : ' + domain + '\n',term.Color.RED))

    else:
        loggingData(str(COUNTER) + ': RecordType: '+recordType+' | RequestId: '+transactionID+' | SrcIP: ' + addr[0] + '  |  SrcPort: ' + str(addr[1]) + '  |  Domain : ' + domain)
        status = 'OKAY'
        print(term.format(str( COUNTER) + ': ' + status + ' -  RecordType: ' + recordType + '  - RequestId: ' + transactionID + '   From: IP ' +
                          addr[0] + ' : Port: ' + str(addr[1]) + '  -  Domain: ' + domain + '\n', term.Color.GREEN))

        #storeDNSRequestJSON(status=status, time=getTime(3),recordType=recordType,transactionID=transactionID, srcIP=addr[0], srcPort=str(addr[1]), domain=domain)
    '''
    time = Helper.getTime(3)
    if case_sensitive is True and 'check_' in domain.lower():  # need to be more dynamic
        modifiedDomain = domain # without permutation
        if 're_check_' not in domain.lower(): # re_check without permutation
            domainName = getLetterCaseSawped(domainName)
            modifiedDomain = '.'.join(map(str, domainName))[:-1]

        if recStatus == 'ERROR':  # TODO: need to handle the exception in better way
            loggingData(str(
                COUNTER) + ': ** ERROR ** : RecordType: ' + recordType + ' | RequestId: ' + transactionID + ' | SrcIP: ' + addr[0] + '  |  SrcPort: ' + str(addr[1]) + '  |  Domain: ' + domain +'  |  Modified Domain: ' + modifiedDomain)
            status = 'ERROR'
            print(term.format(str(COUNTER) + ': ' + status + ' -  RecordType: ' + recordType + '  - RequestId: ' + transactionID + '   From: IP ' + addr[0] + ' : Port: ' + str(addr[1]) + '  -  Domain : ' + domain + '  |  Modified Domain: ' + modifiedDomain +'\n', term.Color.RED))

        else:
            loggingData(str(COUNTER) + ': RecordType: ' + recordType + ' | RequestId: ' + transactionID + ' | SrcIP: ' + addr[0] + '  |  SrcPort: ' + str(addr[1]) + '  |  Domain: ' + domain + '  |  Modified Domain: ' + modifiedDomain)
            status = 'OKAY'
            print(term.format(str(COUNTER) + ': ' + status + ' -  RecordType: ' + recordType + '  - RequestId: ' + transactionID + '   From: IP ' + addr[0] + ' : Port: ' + str(addr[1]) + '  -  Domain : ' + domain + '  |  Modified Domain: ' + modifiedDomain + '\n',
                              term.Color.GREEN))

        if 'Check_' in domain:
            storeDNSRequestJSON(status=status, time=time,recordType=recordType,transactionID=transactionID, srcIP=addr[0], srcPort=str(addr[1]), domain=domain, modifiedDomain=modifiedDomain,mode='check')
        else:
            storeDNSRequestJSON(status=status, time=time,recordType=recordType,transactionID=transactionID, srcIP=addr[0], srcPort=str(addr[1]), domain=domain, modifiedDomain=modifiedDomain)

    else:
        if recStatus == 'ERROR':  # TODO: need to handle the exception in better way
            loggingData(str(COUNTER) + ': ** ERROR ** : RecordType: ' + recordType + ' | RequestId: ' + transactionID + ' | SrcIP: ' + addr[0] + '  |  SrcPort: ' + str(addr[1]) + '  |  Domain: ' + domain)
            status = 'ERROR'
            print(term.format(str(COUNTER) + ': ' + status + ' -  RecordType: ' + recordType + '  - RequestId: ' + transactionID + '   From: IP ' + addr[0] + ' : Port: ' + str(addr[1]) + '  -  Domain: ' + domain + '\n', term.Color.RED))

        else:
            loggingData(str(COUNTER) + ': RecordType: ' + recordType + ' | RequestId: ' + transactionID + ' | SrcIP: ' + addr[0] + '  |  SrcPort: ' + str(addr[1]) + '  |  Domain: ' + domain)
            status = 'OKAY'
            print(term.format(str(COUNTER) + ': ' + status + ' -  RecordType: ' + recordType + '  - RequestId: ' + transactionID + '   From: IP ' + addr[0] + ' : Port: ' + str(addr[1]) + '  -  Domain: ' + domain + '\n',
                              term.Color.GREEN))
        if 'Check_' in domain:
            storeDNSRequestJSON(status=status, time=time,recordType=recordType,transactionID=transactionID, srcIP=addr[0], srcPort=str(addr[1]), domain=domain, mode='check')
        else:
            storeDNSRequestJSON(status=status, time=time, recordType=recordType, transactionID=transactionID,
                                srcIP=addr[0], srcPort=str(addr[1]), domain=domain)

    DNSQuestion = buildQuestion(domainName, recordType)
    if DEBUG is True:
        print('DNSQuestion: ' + str(DNSQuestion))

    # ********************************** DNS Body
    # ********************************** DNS Body
    DNSBody = b''
    for record in records:
        DNSBody += recordToBytes(domainName, recordType, record['ttl'], record['value'])
    if DEBUG is True:
        print(DNSBody)
    return DNSHeader + DNSQuestion + DNSBody


# </editor-fold>

#<editor-fold desc="******************* DNS Forged *******************">
#
def getForgedResponse(data, addr, case_sensitive=True):
    # ********************************** DNS Header
    # Transaction ID
    TransactionID_Byte = data[:2]
    TransactionID = ''
    for byte in TransactionID_Byte:
        TransactionID += hex(byte)[2:]
    if DEBUG is True:  # Debug mode only
        print('ID:')
        print(TransactionID)

    # FLAGS
    Flags = getFlags(data[2:4])
    if DEBUG is True:  # Debug mode only
        print(Flags)

    # Question Count, how many questions in the zone file
    QDCOUNT = RECORD_TYPES.A.value  # b'\x00\x01'  # dns has one question

    records, recordType, domainName, recStatus = getRecs(data[12:])

    # Answer Count
    # ANCOUNT = len(getRecs(data[12:])[0]).to_bytes(2, byteorder='big')  # 12 bytes to skip the header
    ANCOUNT = len(records).to_bytes(2, byteorder='big')  # 12 bytes to skip the header

    # Name server count
    NSCOUNT = (0).to_bytes(2, byteorder='big')

    # Additional count
    ARCOUNT = (0).to_bytes(2, byteorder='big')

    Forged = True
    if Forged is True:
        pass
        #TransactionID_Byte = BruteFouceTransactionID(TransactionID_Byte)
    DNSHeader = Flags + QDCOUNT + ANCOUNT + NSCOUNT + ARCOUNT

#    DNSHeader = TransactionID_Byte + Flags + QDCOUNT + ANCOUNT + NSCOUNT + ARCOUNT
    if DEBUG is True:
        dnsH = ''
        print('DNS HEADER: ' + str(DNSHeader))
        for byte in DNSHeader:
            dnsH += hex(byte)[2:]
        print(dnsH)

    # ********************************** DNS Question

    # records, recordType, domainName = getRecs(data[12:])

    global COUNTER
    COUNTER += 1
    transactionID = str(int(TransactionID, 16))
    domain = '.'.join(map(str, domainName))[:-1]
    status = 'Okay'
    '''
    if recStatus == 'ERROR': # TODO: need to handle the exception in better way
        loggingData(str(COUNTER) + ': ** ERROR ** : RecordType: '+recordType+' | RequestId: '+transactionID+' | SrcIP: ' + addr[0] + '  |  SrcPort: ' + str(addr[1]) + '  |  Domain: ' + domain)
        status = 'ERROR'
        print(term.format(str(
            COUNTER) + ': ' + status + ' -  RecordType: ' + recordType + '  - RequestId: ' + transactionID + '   From: IP ' +  addr[0] + ' : Port: ' + str(addr[1]) + '  -  Domain : ' + domain + '\n',term.Color.RED))

    else:
        loggingData(str(COUNTER) + ': RecordType: '+recordType+' | RequestId: '+transactionID+' | SrcIP: ' + addr[0] + '  |  SrcPort: ' + str(addr[1]) + '  |  Domain : ' + domain)
        status = 'OKAY'
        print(term.format(str( COUNTER) + ': ' + status + ' -  RecordType: ' + recordType + '  - RequestId: ' + transactionID + '   From: IP ' +
                          addr[0] + ' : Port: ' + str(addr[1]) + '  -  Domain : ' + domain + '\n', term.Color.GREEN))

        #storeDNSRequestJSON(status=status, time=getTime(3),recordType=recordType,transactionID=transactionID, srcIP=addr[0], srcPort=str(addr[1]), domain=domain)
    '''
    time = Helper.getTime(3)
    if case_sensitive is True:
        domainName = getLetterCaseSawped(domainName)
        modifiedDomain = '.'.join(map(str, domainName))[:-1]
        if recStatus == 'ERROR':  # TODO: need to handle the exception in better way
            loggingData(str(
                COUNTER) + ': ** ERROR ** : RecordType: ' + recordType + ' | RequestId: ' + transactionID + ' | SrcIP: ' +
                        addr[0] + '  |  SrcPort: ' + str(
                addr[1]) + '  |  Domain: ' + domain + '  |  Modified Domain: ' + modifiedDomain)
            status = 'ERROR'
            print(term.format(str(
                COUNTER) + ': ' + status + ' -  RecordType: ' + recordType + '  - RequestId: ' + transactionID + '   From: IP ' +
                              addr[0] + ' : Port: ' + str(
                addr[1]) + '  -  Domain : ' + domain + '  |  Modified Domain: ' + modifiedDomain + '\n',
                              term.Color.RED))

        else:
            loggingData(
                str(COUNTER) + ': RecordType: ' + recordType + ' | RequestId: ' + transactionID + ' | SrcIP: ' + addr[
                    0] + '  |  SrcPort: ' + str(
                    addr[1]) + '  |  Domain : ' + domain + '  |  Modified Domain: ' + modifiedDomain)
            status = 'OKAY'
            print(term.format(str(
                COUNTER) + ': ' + status + ' -  RecordType: ' + recordType + '  - RequestId: ' + transactionID + '   From: IP ' +
                              addr[0] + ' : Port: ' + str(
                addr[1]) + '  -  Domain : ' + domain + '  |  Modified Domain: ' + modifiedDomain + '\n',
                              term.Color.GREEN))
        if 'Check_' in domain:
            storeDNSRequestJSON(status=status, time=time, recordType=recordType, transactionID=transactionID,
                            srcIP=addr[0], srcPort=str(addr[1]), domain=domain, modifiedDomain=modifiedDomain, mode='check')
        else:
            storeDNSRequestJSON(status=status, time=time, recordType=recordType, transactionID=transactionID,
                            srcIP=addr[0], srcPort=str(addr[1]), domain=domain, modifiedDomain=modifiedDomain)
    else:
        if recStatus == 'ERROR':  # TODO: need to handle the exception in better way
            loggingData(str(
                COUNTER) + ': ** ERROR ** : RecordType: ' + recordType + ' | RequestId: ' + transactionID + ' | SrcIP: ' +
                        addr[0] + '  |  SrcPort: ' + str(addr[1]) + '  |  Domain: ' + domain)
            status = 'ERROR'
            print(term.format(str(
                COUNTER) + ': ' + status + ' -  RecordType: ' + recordType + '  - RequestId: ' + transactionID + '   From: IP ' +
                              addr[0] + ' : Port: ' + str(addr[1]) + '  -  Domain : ' + domain + '\n', term.Color.RED))

        else:
            loggingData(
                str(COUNTER) + ': RecordType: ' + recordType + ' | RequestId: ' + transactionID + ' | SrcIP: ' + addr[
                    0] + '  |  SrcPort: ' + str(addr[1]) + '  |  Domain : ' + domain)
            status = 'OKAY'
            print(term.format(str(
                COUNTER) + ': ' + status + ' -  RecordType: ' + recordType + '  - RequestId: ' + transactionID + '   From: IP ' +
                              addr[0] + ' : Port: ' + str(addr[1]) + '  -  Domain : ' + domain + '\n',
                              term.Color.GREEN))
        if 'Check_' in domain:
            storeDNSRequestJSON(status=status, time=time, recordType=recordType, transactionID=transactionID,
                                srcIP=addr[0], srcPort=str(addr[1]), domain=domain, mode='check')
        else:
            storeDNSRequestJSON(status=status, time=time, recordType=recordType, transactionID=transactionID,
                            srcIP=addr[0], srcPort=str(addr[1]), domain=domain)

    DNSQuestion = buildQuestion(domainName, recordType)
    if DEBUG is True:
        print('DNSQuestion: ' + str(DNSQuestion))

    # ********************************** DNS Body
    # ********************************** DNS Body

    DNSBody = b''

    for record in records:
        DNSBody += recordToBytes(domainName, recordType, record['ttl'], record['value'])

    if DEBUG is True:
        print(DNSBody)

    return DNSHeader + DNSQuestion + DNSBody

#   generate Request Id
def generateResponseWithRequestId(response,sock,addr,times):
    try:
        r = 1
        while r <= 1:
            print("Round: " + str(r))
            requestIds = []
            requestIds = [random.randint(1, 65536) for i in range(times)]
            requestIds.sort()
            index = 0
            for requestId in requestIds:  #range (1, 10000): # 1000 time should be enoght

                index+=1
                print('R: '+str(r)+' - '+str(index) +'- Transaction ID: ' + str(requestId))
                TransactionID_Byte = (requestId).to_bytes(2, byteorder='big')
                response = TransactionID_Byte + response
                # print(str(response))
                # print('Response :)')
                # print(str(response))
                sock.sendto(response, addr)
            r = r+1
    except Exception as ex:
        logging.error('DNSFunctions - generateResponseWithRequestId:\n %s ' % traceback.format_exc())

#   generate Request Id
def generateResponseWithPortNumber(response,sock,addr,times):
    try:
        portNumbers = []
        portNumbers = [random.randint(1, 65536) for i in range(times)]
        portNumbers.sort()
        index=0
        for portNumber in portNumbers: #range (1, 10000): # 1000 time should be enoght
            index += 1
            print(str(index) +'- Port ' + str(portNumber))
            lst = list(addr)
            lst[1] = portNumber
            addr = tuple(lst)
            sock.sendto(response, addr)
    except Exception as ex:
        logging.error('DNSFunctions - generateResponseWithPortNumber: \n %s ' % traceback.format_exc())


# </editor-fold>