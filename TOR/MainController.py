import json
import stem.descriptor.remote
import sys
from enum import Enum
from pprint import pprint
from stem.util import term

# Define Variables
mode = 0  # = sys.argv[1]

class Node(Enum):
    Address  = 1
    AllData = 2

#dnstestsuite-two.space
#dnstestsuite.space - Main one



def ExitNode():
    count = 0
    ExitNodes = []
    for desc in stem.descriptor.remote.get_server_descriptors():
     # Check if the Node is an exit one
        if desc.exit_policy.is_exiting_allowed():
            count = count + 1
            #Print nodes
            if mode == 1:
             print('  %s %s' % (desc.nickname, desc.address))
            ExitNodes.append({
                'ExitNode': {
                    'Address': desc.address,
                    'Fingerprint': desc.fingerprint,
                    'Nickname': desc.nickname,
                    'Dir_port': desc.or_port,
                    'Or_port': desc.dir_port
                }
            })

    # For testing purposes
    '''if count == 0:
        break'''
    # Write into Json file
    with open('info/ExitNodesJSON.json', 'w') as outfile:
        json.dump(ExitNodes, outfile)

def GetJOSNInfo(_node):
    count = 0
    with open('info/ExitNodesJSON.json') as f:
        jsonObjects = json.load(f)
    # print the whole obj
    for obj in jsonObjects:
        if _node == Node.Address:
            pprint(obj['ExitNode']['Address'].encode("ascii"))
        elif _node == Node.AllData:
            pprint(obj)
        count = count + 1
    print("Done.")
    print(term.format('Found ' + str(count) + ' Exit nodes', term.Attr.BOLD))


if __name__ == '__main__':
    ExitNode()
    GetJOSNInfo(Node.Address)
