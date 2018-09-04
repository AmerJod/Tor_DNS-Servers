import argparse
from TOR.MainController import main

import traceback
def parserArgs():
    parser = argparse.ArgumentParser(prog='TORMAPPER', description='TORMAPPER Tool',
                                     epilog="that's how my Tool works")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-r', action='store_true',
                       help='Send DNS reuqests - Map all the DNS resolvers & Data generation')
    group.add_argument('-cr', action='store_true', help='Check the connection reliability of the Tor exit nodes')
    group.add_argument('-cd', action='store_true', help='Check for DNS-0x20 bit encoding. *')
    group.add_argument('-pa', action='store_true', help='Check for DNS publicly Accessible. *')
    group.add_argument('-drc', action='store_true', help='Fouce the not response mode. *')


    parser.add_argument('-g', action='store_true', help='Graph generator')
    parser.add_argument('-m', metavar='number of requests needed to be sent', type=int,
                        help="how many request do you want to send over each exit node")

    parser.add_argument('-n', metavar='Number of nodes needed', type=int,
                        help="how many node do you want to try to connection through")

    parser.add_argument('-out', action='store_true', help='Print in details - use for debugging usually.')
    return parser.parse_args()


if __name__ == '__main__':
    try:
        args = parserArgs()
        # print(args)
        main(args)
    except Exception as ex:
        print(" ........... Testing .........")
        print(ex)
        print('runDns - MAIN: \n%s ' % traceback.format_exc())
        setArgs = argparse.Namespace(r=True,cr =False,cd=False,pa=False,drc=False, g=True, m=100, n=100000, out= False)
        #dnsServer.run(setArgs)
