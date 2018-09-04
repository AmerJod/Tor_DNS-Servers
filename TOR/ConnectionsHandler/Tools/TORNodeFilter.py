import json
import os

from TOR.Helper.Helper import Helper
from TOR.Helper.Helper import MODE_TYPES
from TOR.Helper.Helper import MSG_TYPES
#from TOR.Helper.Helper import ADVERSARY_TASK_MODE
from TOR.ConnectionsHandler.Models.Results import DOMAIN_STATUS


class ExitNodeFilter:
    listDNSConnected = []
    listTORConnected = []
    listTORAccessWebsite = []
    listTORREAccessWebsite = []
    listTORFullyAccessWebsite = []

    listTORNOTAccessWebsite = []
    listDNSNotConnected = []
    listDNSSupport0x20BitEncoding = []

    def __init__(self, nodePath='',mode=''):
        self.nodePath =nodePath
        self.nodePath2 ="C:/Users/Amer Jod/Desktop/UCL/Term 2/DS/DNS_Project/TOR/ConnectionsHandler/Nodes/ProcessedExitNodesJSON.json"

    def filterExitNode(self):
        allExitnodes = self.loadExitNodesFromJSON()

        total_Nodes = len(allExitnodes)
       # number_Of_Nodes = int(allExitnodes)

        print('Total nodes found: %d' % total_Nodes)

        for exitnode in allExitnodes:
            ip = str(exitnode['ExitNode']['Address'].encode("ascii"), 'utf-8')
            fingerprint = str(exitnode['ExitNode']['Fingerprint'].encode("ascii"), 'utf-8')
            nickname = str(exitnode['ExitNode']['Nickname'].encode("ascii"), 'utf-8')
            orPort = str(exitnode['ExitNode']['Or_port'])
            dirPort = str(exitnode['ExitNode']['Dir_port'])
            connectionStatus = exitnode['ExitNode']['Status']['ConnectionStatus']
            requestingDomainStatus= str(exitnode['ExitNode']['Status']['RequestingDomainStatus'])

            if connectionStatus is True:
                self.listTORConnected.append(exitnode)
                if requestingDomainStatus == DOMAIN_STATUS.ACCESSIBLE.value:
                    self.listTORAccessWebsite.append(exitnode)

                elif  requestingDomainStatus == DOMAIN_STATUS.RE_ACCESSIBLE.value:
                    self.listTORREAccessWebsite.append(exitnode)

                elif requestingDomainStatus == DOMAIN_STATUS.NOT_ACCESSIBLE.value:
                    self.listTORNOTAccessWebsite.append(exitnode)

            elif  connectionStatus is False:
                self.listDNSNotConnected.append(exitnode)

        self.listTORFullyAccessWebsite = self.listTORAccessWebsite + self.listTORREAccessWebsite

        #print('listTORConnected:   %d' % len(self.listTORConnected))
        #print('listTORAccessWebsite:   %d' % len(self.listTORAccessWebsite))
        #print('listTORREAccessWebsite:   %d'  % len(self.listTORREAccessWebsite))

        #print('listTORFullyAccessWebsite:   %d\n' % len(self.listTORFullyAccessWebsite))
        #print('listTORNOTAccessWebsite:   %d\n'  % len(self.listTORNOTAccessWebsite))

        #print('listDNSNotConnected:   %d' % len(self.listDNSNotConnected))

        return (self.listTORConnected, self.listTORAccessWebsite,
                self.listTORREAccessWebsite,self.listTORFullyAccessWebsite,self.listTORNOTAccessWebsite)


    def loadExitNodesFromJSON(self):
        cur_path = os.path.dirname(__file__)
        cwd = os.getcwd()
        # print(cwd)
        os.chdir(cur_path)
        # read all the nodes
        new_path = os.path.relpath(self.nodePath2, cur_path)

        # new_path1 = os.listdir(self.GATHERED_NODES_PATH)
        # os.chdir(new_path1)

        with open(new_path) as f:
            json_Objects = json.load(f)
            # Random
            return json_Objects


if __name__ == '__main__':
    filter = ExitNodeFilter()
    filter.filterExitNode()