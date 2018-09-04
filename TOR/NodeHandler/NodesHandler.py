#! /usr/bin/env python3

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

'''
Gather Eixt nodes and store them in a JSON file
'''
class NodesHandler:

    def __init__(self, mode='none'):
        script_dir = os.path.dirname(__file__)  # <-- absolute dir the script is in
        self.NODES_PATH = ('../ConnectionsHandler/Nodes/GatheredExitNodesJSON.json')
        self.NODES_PATH = os.path.join(script_dir, self.NODES_PATH)
        self.mode = '-none' #mode

    def run(self):
        self.ExitNode()
        node_Number = self.GetJOSNInfo(Node_DATA.Address)
        return node_Number

    def ExitNode(self):
        count = 0
        exit_Nodes = []
        stem_Nodes=stem.descriptor.remote.get_server_descriptors()


        for desc in stem_Nodes:
            # CheckingRequest if the Node is an exit one
            if desc.exit_policy.is_exiting_allowed():
                count = count + 1
                # Print nodes
                Helper.printOnScreen('  %s %s' % (desc.nickname, desc.address) ,MSG_TYPES.RESULT.value, self.mode)
                exit_Nodes.append({
                    'ExitNode': {
                        'Address': desc.address,
                        'Fingerprint': desc.fingerprint,
                        'Nickname': desc.nickname,
                        'Dir_port': desc.or_port,
                        'Or_port': desc.dir_port
                    }
                })

        # For testing purposes
        '''if nodeCount == 0:
            break'''
        # Write into Json file
        with open(self.NODES_PATH, 'w') as outfile:
            json.dump(exit_Nodes, outfile)

    def GetJOSNInfo(self,exit_node):
        count = 0
        with open(self.NODES_PATH) as f:
            json_Objects = json.load(f)
        # print the whole obj

        node_number =len(json_Objects)
        for obj in tqdm(json_Objects, ncols=80, desc='Storing ExitNodes'):
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
