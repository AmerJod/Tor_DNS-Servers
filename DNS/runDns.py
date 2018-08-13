import argparse
import dnsServer
from Helper.Helper import ADVERSARY_TASK_MODE

def parserArgs():
    defaultPort = 53
    set_Adv_Required = set([e.value for e in ADVERSARY_TASK_MODE])

    parser = argparse.ArgumentParser(prog='DNS',description='DNS server for a special needs :)',
                                     epilog="And that's how my DNS server works")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-s', action='store_true', help='Run on the server IP')
    group.add_argument('-l', action='store_true', help='Run on the local IP')
    parser.add_argument('-lc','--rcase',action = 'store_true', help='For randomizing lettercase in the dns reply')
    parser.add_argument('-v','--adversary',action = 'store_true', help="Activate ADVERSARY mode, you can specify '-t' option")
    parser.add_argument('-t','--task',nargs='?',choices=set_Adv_Required, default='rboth',const='rboth',
                        help='ADVERSARY mode task: rport: randomize Port Number || ' +
                             'rid: randomize Request Id || rboth: randomise both' +
                             ', default: rboth')
    parser.add_argument('-p', '--port',type=int,default=defaultPort,help=('Which port the DNS is going to use, default: %d' % defaultPort))
    return parser.parse_args()


if __name__ == '__main__':
    args = parserArgs()
    #args="[adv=True, l=False, opt='rboth', port=53, rcase=True, s=True]"
    print(args)
    dnsServer.run(args)
