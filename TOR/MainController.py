#! /usr/bin/env python3

# RUN IT ONLY ON ANY UNIX DISTRIBUTION BUT NOT WINDOWS

import json
import os
import sys
import traceback
import stem.descriptor.remote

from enum import Enum
from pprint import pprint
from stem.util import term
from pathlib import Path

from TOR.ConnectionsHandler import TORConnector
from TOR.Helper.Helper import MSG_TYPES
from TOR.Helper.Helper import Helper
from TOR.Helper.Helper import MODE_TYPES
from TOR.NodeHandler import NodesHandler

VERSION = 1.8

#
def printLogo():
    #
    print(term.format(('\n                           Starting TOR MAPPER.. v%s' % VERSION), term.Color.YELLOW))
    with open('Logo/logo.txt', 'r') as f:
        line_Arr = f.read()
        print(term.format((line_Arr % str(VERSION)), term.Color.GREEN))
        print('\n')

#
def makeDirectories():
    '''
        Make the directories in case they are missing
    '''

    try:
        # TODO: Directories need more abtracte
        if not os.path.exists('GatheredFiles'):
            os.makedirs('GatheredFiles')
            os.makedirs('GatheredFiles/Logs')
            os.makedirs('GatheredFiles/JSON')
        else:
            if not os.path.exists('GatheredFiles/Logs'):
                os.makedirs('GatheredFiles/Logs')
            if not os.path.exists('GatheredFiles/JSON'):
                os.makedirs('GatheredFiles/JSON')


    except Exception as ex:
        Helper.printOnScreenAlways(ex, term.Color.RED)

#
def main(argv):

    mode = '-none'
    required_Nodes = 0
    printLogo()
    makeDirectories()
    if argv[1:] != []:  # on the server
        try:
            required_Nodes= -1
            opt = argv[1]
            error = False
            if len(argv) == 3:  # mode printing
                if argv[2] == MODE_TYPES.printing.value or argv[2] == MODE_TYPES.none.value:
                    mode = argv[2]

            elif len(argv) == 5:
                if argv[2] == '-n': # stop after certain nodes number
                    required_Nodes = argv[3]
                else:
                    error = True
                if argv[4] == MODE_TYPES.printing.value or argv[4] == MODE_TYPES.none.value:
                    mode = argv[4]
                else:
                    error = True

                if error is True:
                    Helper.printOnScreen('WRONG ......',color=MSG_TYPES.ERROR)
                    sys.exit(2)
            else:
                Helper.printOnScreen('WRONG Too Many arguments.', color=MSG_TYPES.ERROR)

            ###---------------------------------------

            try:
                Helper.printOnScreenAlways("Gathering Info ... ", MSG_TYPES.RESULT)
                nodes = NodesHandler.NodesHandler(mode=mode)
                nodes_Number = nodes.run()
                Helper.printOnScreenAlways(("DONE, %s nodes have been gathered" % str(nodes_Number)),MSG_TYPES.RESULT)
            except Exception as ex:
                Helper.printOnScreenAlways(("Exit nodes are not gathered.. :(, ERROR : %s" % str(ex)),MSG_TYPES.ERROR)
                sys.exit()

            if opt == '-r' or opt == '-c' or opt == '-cd' or opt=='-drc':    #   check the connections
                if(int(required_Nodes) > 0):
                    con = TORConnector.TORConnections(opt,mode,required_Nodes)
                    con.run()
                else:
                    con = TORConnector.TORConnections(opt,mode)
                    con.run()

        except Exception as ex:
            print(ex)
            sys.exit()


if __name__ == '__main__':

    try:  # on the server
        if len(sys.argv) != 1:
            main(sys.argv[1:])
        else:
            print('ERROR: argv....')
            main(['', '-drc','-n','9','-out'])
            sys.exit()

    except Exception as ex:  # locally
        print('ERROR: argv....  OR %s' % str(ex))
        main(['','-drc','-n','9','-out'])
        sys.exit()


