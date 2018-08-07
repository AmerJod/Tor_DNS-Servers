'''
DNS Server - UCL - Amer Joudiah
Mini DNS server for resolving our website 'dnstestsuite.space'.
https://bitbucket.org/AmerJoudiah/dns_project/
Note: Still private project.
'''

import socket
import sys

from stem.util import term

from Helper import DNSFunctions
from Helper.Helper import Helper
from Helper.Helper import MODE_TYPES
from Helper.Helper import MSG_TYPES





VERSION = '0.998b'
MODIFY_DATE = '- Last modified: 06/08/2018'
IP_ADDRESS_LOCAL = '127.0.0.1'
IP_ADDRESS_SERVER = '172.31.16.226'
DEBUG = False
PORT = 53  # 53 Default port

ADVERSARY_MODE = False
FIX_PORT = True  #True # try all the possible port
FIX_REQUESTID = False #False  # try all the possible request ID
NUMBER_OF_TRYS = 10000

def main(argv,IP):
    # gather Zone info and store it into memory
    DNSFunctions.loadZone()
    case_sensitive = False
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    opts = argv
    if opts[0] == '-s':
        sock.bind((IP, PORT))
        print("\n                           Host: %s | Port: %s \n" % (IP, PORT))
        if opts.__len__() > 1:
            if opts[1] == '-Ncase':
                Helper.printOnScreenAlways("Change Domain Name letter case is enabled",term.Color.GREEN)
                case_sensitive = True

    elif opts[0] == '-l' or opts == '':
        sock.bind((IP_ADDRESS_LOCAL, PORT))
        print("\n                           Host: %s | Port: %s \n" % (IP_ADDRESS_LOCAL, PORT))
        if opts.__len__() > 1:
            if opts[1] == '-Ncase':
                Helper.printOnScreenAlways("Change Domain Name letter case is enabled", term.Color.GREEN)
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
                    response = DNSFunctions.getResponse(data, addr)  # we get the correct response.
                    DNSFunctions.generateResponseWithPortNumber(response, sock, addr,NUMBER_OF_TRYS)  # brute force all the possible port number

                elif FIX_PORT is True:  ## try all the possible request IDs 1  to 65556
                    response = DNSFunctions.getForgedResponse(data, addr,
                                                              case_sensitive=True)  # forge response without request ID, later we forge the ID and combine it with the whole response
                    DNSFunctions.generateResponseWithRequestId(response, sock,
                                                  addr,NUMBER_OF_TRYS)  # brute force # we get the response once without Tre_id
                sock.sendto(response,addr)

    except Exception as ex:
        DNSFunctions.loggingError(main,'ERROR: main ' + str(ex))
        Helper.printOnScreenAlways("\nERROR: Terminated!!! :" + str(ex),term.Color.RED)

def main_test():
    # gather Zone info and store it into memory
    DNSFunctions.loadZone()
    print("Testing ....  ")
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    #sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((IP_ADDRESS_LOCAL, PORT))
    print("Host: %s | Port: %s " % (IP_ADDRESS_LOCAL,PORT ))
    # open socket and
    # keep listening
    while 1:
        data, addr = sock.recvfrom(512)
        response = DNSFunctions.getResponse(data, addr,case_sensitive=True)

        print("test 1")
        print(str(response))
        sock.sendto(response, addr)

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

    DNSFunctions.makeDirectories()
    DNSFunctions.initLogger()
    DNSFunctions.printLogo(version=VERSION,modifyDate=MODIFY_DATE)
    DNSFunctions.killprocess(PORT)
    DNSFunctions.setDebuggingMode(DEBUG)
    #DNSFunctions.setAdversaryMode(ADVERSARY_MODE)

    if ADVERSARY_MODE is True:
        Helper.printOnScreenAlways('*****Adversary mode is activated*****', MSG_TYPES.YELLOW)
    try: # on the server
        if len(sys.argv) != 1:
            ip = socket.gethostbyname(socket.gethostname())
            main(sys.argv[1:], ip)
        else:
            print('ERROR: argv....')
            #main_test_local()
            main_test()
    except: # locally
        print('ERROR: argv....')
        #main_test_local()
        main_test()