'''
DNS Server - UCL - Amer Joudiah
Mini DNS server for resolving our website 'dnstestsuite.space'.
https://bitbucket.org/AmerJoudiah/dns_project/
Note: Still private project.
'''

import logging
import socket
import traceback
import os
import time
import argparse

from Helper import DNSFunctions
from Helper.Helper import Helper
from Helper.Helper import MODE_TYPES
from Helper.Helper import MSG_TYPES
from Helper.Helper import ADVERSARY_TASK_MODE


VERSION = '1.15 b'
#MODIFY_DATE = '- Last modified: 11/08/2018'
IP_ADDRESS_LOCAL = '127.0.0.1'
IP_ADDRESS_SERVER = '172.31.16.226'
DEBUG = False
PORT = 53  # 53 Default port

RANDOMIZE_PORT = False  # True # try all the possible port
RANDOMIZE_REQUEST_ID = False  # False  # try all the possible request ID
RANDOMIZE_BOTH = False

NUMBER_OF_TRIES = 10000 #   bruteforcing

def printPortAndIP(ip,port):
    print("\n                                            Host: %s | Port: %s \n" % (ip, port))

def printNcase():
    Helper.printOnScreenAlways("                                        Change Domain Name letter case is enabled",MSG_TYPES.YELLOW)

def printModifiedDate():
    try:
        filename = os.path.basename(__file__)
        os.path.abspath(os.path.dirname(__file__))
        (mode, ino, dev, nlink, uid, gid, size, atime, mtime, ctime) = os.stat(filename)
        return time.ctime(mtime)
    except Exception as ex:
        Helper.printOnScreenAlways("run_DNS -printModifedDate: %s"%ex , MSG_TYPES.ERROR)



def setAdversaryModetask(value):
    global RANDOMIZE_PORT
    global RANDOMIZE_BOTH
    global RANDOMIZE_REQUEST_ID
    if value == ADVERSARY_TASK_MODE.RRANDOMIZE_PORT_NUMBER.value:
        RANDOMIZE_PORT = True
    elif value == ADVERSARY_TASK_MODE.RRANDOMIZE_REQUEST_ID.value:
        RANDOMIZE_REQUEST_ID = True
    elif value == ADVERSARY_TASK_MODE.RRANDOMIZE_BOTH.value:
        RANDOMIZE_BOTH = True


def main(argv,IP):

    global  FORCE_NOT_RESPONSE_MEG
    letterCaseRandomize = argv.rcase
    port = argv.port
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((IP, port))

    printPortAndIP(IP, port)
    if letterCaseRandomize:
        printNcase()
    ADVERSARY_Mode = argv.adversary
    FORCE_NOT_RESPONSE_MODE = argv.dont
    DNSFunctions.loadRealZone()

    try:
        if not ADVERSARY_Mode:
            # keep listening
            #DNSFunctions.loadRealZone()
            while 1:
                data, addr = sock.recvfrom(512)
                response, allowResponse = DNSFunctions.getResponse(data, addr,letterCaseRandomize,forceNotResponseMode=FORCE_NOT_RESPONSE_MODE )
                if allowResponse:
                    sock.sendto(response, addr)

        elif ADVERSARY_Mode: # attacking mode
            Helper.printOnScreenAlways(
                '                                         *****   ADVERSARY MODE IS ACTIVATED  *****', MSG_TYPES.YELLOW)
            DNSFunctions.loadFakeZone()
            setAdversaryModetask(argv.task)
            # keep listening
            while 1:
                data, addr = sock.recvfrom(512)

                if RANDOMIZE_PORT is True:  ## try all the possible Port Number 1  to 65556
                    response = DNSFunctions.getResponse(data, addr, case_sensitive=False,adversaryMode=ADVERSARY_Mode,withoutRequestId=False)  # we get the correct response.
                    DNSFunctions.generateResponseWithPortNumber(response, sock, addr, NUMBER_OF_TRIES)  # brute force all the possible port number

                elif RANDOMIZE_REQUEST_ID is True:  ## try all the possible request IDs 1  to 65556
                    response = DNSFunctions.getResponse(data, addr, case_sensitive=False,adversaryMode=ADVERSARY_Mode,withoutRequestId=True)  # forge response without request ID, later we forge the ID and combine it with the whole response
                    DNSFunctions.generateResponseWithRequestId(response, sock, addr, NUMBER_OF_TRIES)  # brute force # we get the response once without Tre_id

                elif RANDOMIZE_BOTH:
                    pass

    except Exception as ex:
        Helper.loggingError(str('ERROR: main ' + traceback.format_exc()))
        Helper.printOnScreenAlways("\nERROR: Terminated!!! :" + str(ex),MSG_TYPES.ERROR)

def run(argv):
    modifiedDate = printModifiedDate()
    DNSFunctions.makeDirectories()
    Helper.initLogger(level=logging.ERROR, enableConsole=False)
    DNSFunctions.printLogo(version=VERSION, modifyDate=modifiedDate)
    DNSFunctions.killprocess(PORT)
    DNSFunctions.setDebuggingMode(DEBUG)

    if argv.s is True:
        ip = socket.gethostbyname(socket.gethostname())
    else:
        ip = IP_ADDRESS_LOCAL
    main(argv, ip)


if __name__ == '__main__':
    try: # on the server
            #setArgs= {'s': True, 'l': False, 'rcase': False, 'adversary': False, 'task': 'rboth', 'port': 53}
            setArgs = argparse.Namespace(l=True,adversary=False, port=53, rcase=True, s=False, task='rport', dont=True)
            run(setArgs)
    except Exception as ex: # locally
        print('ERROR:o argv.... %s' %ex)


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
