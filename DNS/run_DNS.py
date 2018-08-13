'''
DNS Server - UCL - Amer Joudiah
Mini DNS server for resolving our website 'dnstestsuite.space'.
https://bitbucket.org/AmerJoudiah/dns_project/
Note: Still private project.
'''
import logging
import socket
import sys
import traceback
import os
import time

from stem.util import term

from Helper import DNSFunctions
from Helper.Helper import Helper

from Helper.Helper import MODE_TYPES
from Helper.Helper import MSG_TYPES



VERSION = '1.12 b'
MODIFY_DATE = '- Last modified: 11/08/2018'
IP_ADDRESS_LOCAL = '127.0.0.1'
IP_ADDRESS_SERVER = '172.31.16.226'
DEBUG = False
PORT = 53  # 53 Default port

ADVERSARY_MODE = False
FIX_PORT = True  # True # try all the possible port
FIX_REQUESTID = False   # False  # try all the possible request ID
NUMBER_OF_TRIES = 10000

def printPortAndIP(ip,port):
    print("\n                                            Host: %s | Port: %s \n" % (ip, port))

def printNcase():
    Helper.printOnScreenAlways("                                        Change Domain Name letter case is enabled",term.Color.GREEN)

def printModifiedDate():
    try:
        filename = os.path.basename(__file__)
        os.path.abspath(os.path.dirname(__file__))
        (mode, ino, dev, nlink, uid, gid, size, atime, mtime, ctime) = os.stat(filename)
        return time.ctime(mtime)
    except Exception as ex:
        Helper.printOnScreenAlways("run_DNS -printModifedDate: %s"%ex , MSG_TYPES.ERROR)


def main(argv,IP):
    # gather Zone info and store it into memory
    # DNSFunctions.loadZone()
    case_sensitive = False
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    opts = argv
    if opts[0] == '-s':
        sock.bind((IP, PORT))
        printPortAndIP(IP, PORT)
        if opts.__len__() > 1:
            if opts[1] == '-Ncase':
                printNcase()
                case_sensitive = True

    elif opts[0] == '-l' or opts == '':
        sock.bind((IP_ADDRESS_LOCAL, PORT))
        printPortAndIP(IP_ADDRESS_LOCAL, PORT)
        if opts.__len__() > 1:
            if opts[1] == '-Ncase':
                printNcase()
                case_sensitive = True


    try:
        if ADVERSARY_MODE is False:
            # keep listening
            while 1:
                data, addr = sock.recvfrom(512)
                response = DNSFunctions.getResponse(data, addr,case_sensitive)
                sock.sendto(response, addr)
        elif ADVERSARY_MODE is True:
            # keep listening
            while 1:
                data, addr = sock.recvfrom(512)
                if FIX_REQUESTID is True:  ## try all the possible Port Number 1  to 65556
                    response = DNSFunctions.getResponse(data, addr, case_sensitive=False,adversaryMode=ADVERSARY_MODE,withoutRequestId=False)  # we get the correct response.
                    DNSFunctions.generateResponseWithPortNumber(response, sock, addr, NUMBER_OF_TRIES)  # brute force all the possible port number

                elif FIX_PORT is True:  ## try all the possible request IDs 1  to 65556
                    response = DNSFunctions.getResponse(data, addr, case_sensitive=False,adversaryMode=ADVERSARY_MODE,withoutRequestId=True)  # forge response without request ID, later we forge the ID and combine it with the whole response
                    DNSFunctions.generateResponseWithRequestId(response, sock, addr, NUMBER_OF_TRIES)  # brute force # we get the response once without Tre_id
                #sock.sendto(response,addr)

    except Exception as ex:
        DNSFunctions.loggingError('ERROR: main ' + traceback.format_exc())
        Helper.printOnScreenAlways("\nERROR: Terminated!!! :" + str(ex),term.Color.RED)

# TODO: need to be refactored
def main_test():
    # gather Zone info and store it into memory

    print("Testing ....  ")
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    #sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((IP_ADDRESS_LOCAL, PORT))
    print("Host: %s | Port: %s " % (IP_ADDRESS_LOCAL,PORT ))
    # open socket and
    # keep listening
    while 1:
        data, addr = sock.recvfrom(512)
        #response = DNSFunctions.getResponse(data, addr,case_sensitive=True)
        #sock.sendto(response, addr)

        # forge port number
        #response = DNSFunctions.getResponse(data, addr, case_sensitive=False,adversaryMode=ADVERSARY_MODE,withoutRequestId=False)  # we get the correct response.
        #DNSFunctions.generateResponseWithPortNumber(response, sock, addr, NUMBER_OF_TRIES)  # brute

        # forge ID
        # response,Realresponse = DNSFunctions.getResponse(data, addr,case_sensitive = False, withoutRequestId = True)  # we get the correct response.
        # DNSFunctions.generateResponseWithRequestId(response, sock, addr, NUMBER_OF_TRIES)  # brute

        #print("test 1")
        #print(str(response))


# TODO: need to be deleted
def main_test_local():
    # gather Zone info and store it into memory

    DNSFunctions.loadZone()
    '''
    try:
        opts, args = getopt.getopt(argv, 'l:s')
    except getopt.GetoptError:
        print('test.py -l')
        sys.exit(2)
    '''
    print("Testing ....  ")
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((IP_ADDRESS_LOCAL, PORT))

    print("\n                           Host: %s | Port: %s " % (IP_ADDRESS_LOCAL,PORT ))

    # testing
    #BYTES =b'\xe8H\x84\x00\x00\x01\x00\x00\x00\x00\x00\x00\x02ns\x0cdnstEStsuiTe\x05SpACE\x00\x00\x01'
    BYTES =b'\\$\x00\x10\x00\x01\x00\x00\x00\x00\x00\x01\x02ns\x0cdnStEstSuITE  \x05SpACe\x00\x00\x1c\x00\x01\x00\x00)\x10\x00\x00\x00\x80\x00\x00\x00'

    response = DNSFunctions.getResponse(BYTES, '127.0.0.2')
    print("response:")
    print(str(response))

if __name__ == '__main__':
    modifiedDate =printModifiedDate()
    DNSFunctions.loadRealZone()

    DNSFunctions.makeDirectories()
    Helper.initLogger(level=logging.ERROR,enableConsole=False)
    DNSFunctions.printLogo(version=VERSION,modifyDate=modifiedDate)
    DNSFunctions.killprocess(PORT)
    DNSFunctions.setDebuggingMode(DEBUG)
    #DNSFunctions.setAdversaryMode(ADVERSARY_MODE)

    if ADVERSARY_MODE is True:
        Helper.printOnScreenAlways('                                         ***** ADVERSARY MODE IS ACTIVATED *****', MSG_TYPES.YELLOW)
        DNSFunctions.loadFakeZone()
    try: # on the server
        if len(sys.argv) != 1:
            ip = socket.gethostbyname(socket.gethostname())
            main(sys.argv[1:], ip)
            #main(['-s','-Ncase'], ip)

        else:
            #print('ERROR:i argv....')
            #main_test_local()
            ip = socket.gethostbyname(socket.gethostname())
            main(['-l','-Ncase'], ip)
            #main_test()
    except Exception as ex: # locally
        print('ERROR:o argv.... %s' %ex)
        #main_test_local()
        main_test()