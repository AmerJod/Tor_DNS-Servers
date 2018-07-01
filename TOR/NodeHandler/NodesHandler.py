import json
import os
import time

import stem.descriptor.remote
import sys
from enum import Enum
from pprint import pprint
from stem.util import term
from pathlib import Path


from tqdm import tqdm

from TOR.Helper.Helper import Helper

class Node_DATA(Enum):
    Address = 1
    AllData = 2

class MSG_TYPES(Enum):
    RESULT = term.Color.GREEN
    ERROR = term.Color.RED
    YELLOW = term.Color.YELLOW


class NodesHandler:

    def __init__(self, mode='none'):
        script_dir = os.path.dirname(__file__)  # <-- absolute dir the script is in
        self.NODES_PATH = ('../ConnectionsHandler/Nodes/ExitNodesJSON.json')
        self.NODES_PATH= os.path.join(script_dir, self.NODES_PATH)
        self.mode = '-none' #mode

       # self.Helper = Helper()
    def run(self):
        self.ExitNode()
        nodeNumber = self.GetJOSNInfo(Node_DATA.Address)
        return nodeNumber

    def ExitNode(self):
        count = 0
        ExitNodes = []
        Stem_nodes=stem.descriptor.remote.get_server_descriptors()


        for desc in Stem_nodes:
            # Check if the Node is an exit one
            if desc.exit_policy.is_exiting_allowed():
                count = count + 1
                # Print nodes
                Helper.printOnScreen('  %s %s' % (desc.nickname, desc.address) ,MSG_TYPES.RESULT.value, self.mode)
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
        with open(self.NODES_PATH, 'w') as outfile:
            json.dump(ExitNodes, outfile)

    def GetJOSNInfo(self,exit_node):
        count = 0
        with open(self.NODES_PATH) as f:
            jsonObjects = json.load(f)
        # print the whole obj

        node_number =len(jsonObjects)
        for obj in tqdm(jsonObjects, ncols=80, desc='Storing ExitNodes'):
            if self.mode =='-out':
                if exit_node == Node_DATA.Address:
                    pprint(obj['ExitNode']['Address'].encode("ascii"))
                elif exit_node == Node_DATA.AllData:
                    pprint(obj)

            #   just for showing the progress bar
            time.sleep(0.005)
            count = count + 1
        #print("Done.")
        #print('\n')
        time.sleep(1)

        return count
