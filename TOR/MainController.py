import json
import stem.descriptor.remote
import sys
from enum import Enum
from pprint import pprint
from stem.util import term
from pathlib import Path

from TOR.ConnectionsHandler import TORConnector
from TOR.Helper.Helper import MSG_TYPES
from TOR.Helper.Helper import Helper
from TOR.Helper.Helper import MODE_TYPES
from TOR.NodeHandler import NodesHandler


VERSION = 1.1

def printLogo():
    print(term.format(('\n                           Starting TOR MAPPER.. v%s' % VERSION), term.Color.YELLOW))
    with open('Logo/logo.txt', 'r') as f:
        lineArr = f.read()
        print(term.format((lineArr % str(VERSION)),term.Color.GREEN))
        print('\n')
        '''
        with open('Logo/logo2.txt', 'r') as f:
        lineArr = f.read()
        print(term.format(lineArr,term.Color.RED))
        '''

def main(argv):
    mode = '-none'
    requiredNodes = 0
    printLogo()

    if argv[1:] != []:  # on the server
        try:
            numberOFNodes= -1
            opt = argv[1]
            error = False
            if len(argv) == 3:  # mode printing
                if argv[2] == MODE_TYPES.print.value or argv[2] == MODE_TYPES.none.value:
                    mode = argv[2]

            elif len(argv) == 5:
                if argv[2] == '-n':
                    requiredNodes = argv[3]
                else:
                    error = True

                if argv[4] == MODE_TYPES.print.value or argv[4] == MODE_TYPES.none.value:
                    mode = argv[4]
                else:
                    error = True

                if error is True:
                    Helper.printOnScreen('WRONG ......',color=MSG_TYPES.ERROR.value)
                    sys.exit(2)
            else:
                Helper.printOnScreen('WRONG Too Many arguments .', color=MSG_TYPES.ERROR.value)


            ###---------------------------------------

            try:
                Helper.printOnScreenAlways("Gathering Info ... ", MSG_TYPES.RESULT.value)
                nodes = NodesHandler.NodesHandler(mode=mode)
                nodesNumber = nodes.run()
                Helper.printOnScreenAlways(("DONE, %s nodes have been gathered" % str(nodesNumber)),MSG_TYPES.RESULT.value)
            except Exception as ex:
                Helper.printOnScreenAlways(("Exit nodes are not gathered.. :(, ERROR : %s" % str(ex)),MSG_TYPES.ERROR.value)
                sys.exit()

            if opt == '-r' or opt == '-c':    #   check the connections
                if(int(requiredNodes) > 0):
                    con = TORConnector.TORConnections(opt,mode,requiredNodes)
                    con.run()
                else:
                    con = TORConnector.TORConnections(opt,mode)
                    con.run()


        except Exception as ex:
            Helper.printOnScreenAlways(ex,MSG_TYPES.ERROR)
            sys.exit()


if __name__ == '__main__':

    try:  # on the server
        if len(sys.argv) != 1:
            main(sys.argv[1:])
        else:
            print('ERROR: argv....')
            #main(['', '-c','-n','3','-out'])
            main(['', '-r','-none'])
            sys.exit()
            #main_test()
    except Exception as ex:  # locally
        print('ERROR: argv....  OR %s' % str(ex))
        #main(['','-c','-n','3','-out'])
        main(['', '-r', '-none'])

        sys.exit()


