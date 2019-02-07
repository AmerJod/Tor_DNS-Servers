#! /usr/bin/env python3

import datetime
import functools
import getopt
import io
import json
import os
import pickle
import pycurl
import sys,traceback
import time
import certifi
import stem.process
from tqdm import tqdm


import random
import argparse

from threading import Thread
from stem import StreamStatus, process
from stem.util import term
from enum import Enum
from tqdm import tqdm
import shlex

from TOR.ConnectionsHandler.Models.Results import CONNECTION_STATUS
from TOR.Helper.Helper import MSG_TYPES
from TOR.Helper.Helper import Helper
from TOR.Helper.Helper import MODE_TYPES
from TOR.Helper.Helper import TASK_MODE
from TOR.NodeHandler import NodesHandler

from TOR.ConnectionsHandler.Models import Results
from TOR.ConnectionsHandler.Models.Connection import Connection
from TOR.ConnectionsHandler.Models.ExitNode import ExitNode
from TOR.ConnectionsHandler import TORFunctions

class TORConnections:

    def __init__(self, opt='-r', mode='-none',requiredNodes=10000,runManyTimeMode=False):
        self.mode = mode
        self.opt = opt

        self.REQUIRED_NODES = requiredNodes
        self.SOCKS_PORT = 7000
        self.CONTROL_PORT = 9051

        self.DOMAIN_URL = 'dnstestsuite.space'
        self.DOMAIN_URL_CHECK = 'dnstestsuite.space/check'  # uses to check if the dns is supporting the 0x20 coding
        self.DOMAIN__CORRECT_MESSAGE_RESULT = 'Works DNStestsuite.space@12.13.14.1'  # should be the same message in check.html page
        self.TOR_CHECK_CONNECTION = 'https://icanhazip.com'
        self.FORCE_NOT_RESPONSE_MSG = 'tor_dont_response' # MUST BE THE SAME IN THE DNS SERVER
        self.OUTPUT_FILE = 'result.txt'
        self.GATHERED_NODES_PATH = 'Nodes/GatheredExitNodesJSON.json'  # gathered by NodeHandler class
        self.PROCESSED_NODES_PATH = 'Nodes/ProcessedExitNodesJSON.json'  # gathered by NodeHandler class
        self.TOR_CONNECTION_TIMEOUT = 30  # timeout before we give up on a circuit
        self.PYCURL_TIMEOUT = 40
        self.REQUEST_TIMES = 100
        self.RUN_MANYTIMES_MODE = runManyTimeMode

        self.CONSUMER_KEY = ""
        self.CONSUMER_SECRET = ""
        self.ACCESS_TOKEN = ""
        self.ACCESS_TOKEN_SECRET = ""
        self.Result_List = []
        self.ExitNodes_List = []

    #
    def loadExitNodesFromJSON(self):
        cur_path = os.path.dirname(__file__)
        cwd = os.getcwd()
        os.chdir(cur_path)
        # read all the nodes
        new_path = os.path.relpath(self.GATHERED_NODES_PATH, cur_path)

        with open(new_path) as f:
            json_Objects= json.load(f)
            # Random
            random.shuffle(json_Objects)
            return json_Objects

    # check Tor connection only, if the node is accessable
    def checkTorConnection(self, numberOfNodes=10000):   # check Tor connection
        start_time = time.time()
        nodes_Count = 0
        successfully_Connections = 0
        successfully_Connections_Checking_Failed = 0
        failed_Connections = 0

        # load
        json_Objects = self.loadExitNodesFromJSON()

        result = 3 # assume that the connection has failed

        if stem.util.system.is_windows():
            # Terminate tor.exe in case if it is still running
            TORFunctions.ProcesskillForWindows('tor.exe')

        print('\n')
        total_Nodes=len(json_Objects)
        number_Of_Nodes = int(numberOfNodes)
        for obj in json_Objects:

            fingerprint = str(obj['ExitNode']['Fingerprint'].encode("ascii"),'utf-8')

            # total  number of nodes # debugging prupuses
            nodes_Count = nodes_Count + 1
            if nodes_Count <= number_Of_Nodes:
                break
            result = self.connectToTORExitNode(fingerprint, ip, nodes_Count, TASK_MODE.TOR_CONNECTION_CHECKING)
            self.Result_List.append(result)


        time_taken = time.time() - start_time
        finalResult = Results.FinalResult(time_taken, nodes_Count, successfully_Connections, successfully_Connections_Checking_Failed, failed_Connections)
        finalResult.printResult()

        data = ''
        with open(self.OUTPUT_FILE,'r') as file:
            data = file.read()
        with open(self.OUTPUT_FILE,'w+') as file:
            file.write(data)
            file.write("\n--------------------------\n")
            file.write("\n--------------------------\n")
            file.write('Finished in  %0.2f seconds\n' % (time_taken))
            file.write('Found ' + str(nodes_Count) + ' Exit nodes:\n')
            file.write('   '+str(successfully_Connections) + ': were connected successfully\n')
            file.write('   '+str(successfully_Connections_Checking_Failed) + ': were connected successfully, but checking failed.\n')
            file.write('   '+str(failed_Connections) + ': failed\n')
            file.write('\n--------------------------\n')
            file.write('Checking Success rate:   '+str(successfully_Connections/nodes_Count * 100)+'% \n')
            file.write('Checking Failed rate:    '+str(successfully_Connections_Checking_Failed/nodes_Count * 100)+'% \n')
            file.write('Failed Connections rate: '+str(failed_Connections/nodes_Count * 100)+'% \n')

    #  check DNS if it supports domain name 0x20 coding.
    def checkWebsiteConnection(self, numberOfNodes=10000):
        start_time = time.time()
        nodesCount = 0
        successfully_Connections = 0
        successfully_Connections_Checking_Failed = 0

        re_successfully_Connections = 0
        re_successfully_Connections_Checking_Failed = 0
        failed_Connections = 0

        # load
        json_Objects = self.loadExitNodesFromJSON()
        result = 3  # assume that connection failed

        if stem.util.system.is_windows():
            # Terminate the tor in case if it is still running
            TORFunctions.ProcesskillForWindows('tor.exe')

        print('\n')
        total_Nodes = len(json_Objects)
        number_Of_Nodes = int(numberOfNodes)
        nodesCount = 0

        for obj in json_Objects:
            ip = str(obj['ExitNode']['Address'].encode("ascii"), 'utf-8')
            fingerprint = str(obj['ExitNode']['Fingerprint'].encode("ascii"), 'utf-8')
            nickname = str(obj['ExitNode']['Nickname'].encode("ascii"), 'utf-8')
            or_port = str(obj['ExitNode']['Or_port'])
            dir_port = str(obj['ExitNode']['Dir_port'])

            # total  number of nodes
            if nodesCount >= number_Of_Nodes:
                break
            nodesCount = nodesCount + 1
            result = self.connectToTORExitNode(fingerprint, ip, nodesCount,  TASK_MODE.DNS_0x20_CHECKING)    # check if the website is accessible / we use this method for check if the DNS support 0x20 coding for the domain name.
            exitNode = ExitNode(ipaddress=ip, fingerprint=fingerprint, nickname=nickname, or_port=or_port,
                                dir_port=dir_port, status=result)
            self.ExitNodes_List.append(exitNode)
            self.Result_List.append(result)

        time_taken = time.time() - start_time
        finalResult = Results.FinalResult(self.Result_List, nodesCount, time_taken)

        curpath = os.path.dirname(__file__)
        os.chdir(curpath)
        newJSONPath = os.path.join(curpath,self.PROCESSED_NODES_PATH)
        Helper.storeExitNodesJSON(objects=self.ExitNodes_List, path=newJSONPath)

    # resolve our domain via our DNS
    # findTORDNSResolver(self)
    def requestDomainViaTor(self):
        Helper.printOnScreenAlways('Requesting %s  via TOR ' % self.DOMAIN_URL)
        start_time = time.time()
        nodesCount = 0
        successfully_Connections = 0
        successfully_Connections_Checking_Failed = 0
        failed_Connections = 0

        json_Objects = self.loadExitNodesFromJSON()
        if stem.util.system.is_windows():
            # Terminate the tor in case if it is still running
            TORFunctions.ProcesskillForWindows('tor.exe')

        for obj in tqdm(json_Objects, ncols=80, desc='Requesting Domain via our DNS'):
            ip = str(obj['ExitNode']['Address'].encode("ascii"), 'utf-8')
            fingerprint = str(obj['ExitNode']['Fingerprint'].encode("ascii"), 'utf-8')
            nickname = str(obj['ExitNode']['Nickname'].encode("ascii"), 'utf-8')
            or_port = str(obj['ExitNode']['Or_port'].encode("ascii"))
            dir_port = str(obj['ExitNode']['Dir_port'].encode("ascii"))
            result = self.connectToTORExitNode(fingerprint, ip, nodesCount + 1, TASK_MODE.REQUEST_DOMAIN)
            exitNode = ExitNode(ipaddress=ip,fingerprint=fingerprint,nickname=nickname,or_port=or_port,dir_port=dir_port,status=result)
            self.ExitNodes_List.append(exitNode)
            self.Result_List.append(result)

        time_taken = time.time() - start_time
        finalResult = Results.FinalResult(self.Result_List, nodesCount, time_taken)

        cur_path = os.path.dirname(__file__)
        os.chdir(cur_path)
        new_path = os.path.relpath(self.PROCESSED_NODES_PATH, cur_path)
        Helper.storeExitNodesJSON(object=self.ExitNodes_List,path=new_path)


    # resolve our domain via our DNS
    def countDNSRequest(self):
        Helper.printOnScreenAlways('Requesting %s  via TOR ' % self.DOMAIN_URL)
        start_time = time.time()
        nodesCount = 0


        json_Objects = self.loadExitNodesFromJSON()
        if stem.util.system.is_windows():
            # Terminate the tor in case if it is still running
            TORFunctions.ProcesskillForWindows('tor.exe')

        for obj in tqdm(json_Objects, ncols=80, desc='Requesting Domain via our DNS'):

            ip = str(obj['ExitNode']['Address'].encode("ascii"), 'utf-8')
            fingerprint = str(obj['ExitNode']['Fingerprint'].encode("ascii"), 'utf-8')
            nickname = str(obj['ExitNode']['Nickname'].encode("ascii"), 'utf-8')
            or_port = str(obj['ExitNode']['Or_port'])
            dir_port = str(obj['ExitNode']['Dir_port'])
            self.connectToTORExitNode(fingerprint, ip, nodesCount + 1, TASK_MODE.DNS_RESOLVER_COUNTER)

        time_taken = time.time() - start_time

    def startTorConnection(self, exitFingerprint, ip,mode=TASK_MODE.DNS_0x20_CHECKING):
        # Start an instance of Tor configured to only exit through Russia. This prints
        # Tor's bootstrap information as it starts. Note that this likely will not
        # work if you have another Tor instance running.
        result = self.connectToTORExitNode(exitFingerprint, ip, 3, mode)  # check if the website i


    def start1(self,exitFingerprint, ip):
        # Start an instance of Tor configured to only exit through Russia. This prints
        # Tor's bootstrap information as it starts. Note that this likely will not
        # work if you have another Tor instance running.

        # Terminate the tor in case if it is still running
        if not (stem.util.system.get_pid_by_port(self.CONTROL_PORT)):
            print(term.format("Starting Tor, connecting to: %s \n", term.Attr.BOLD) % ip)
            tor_process = stem.process.launch_tor_with_config(
                timeout=90,
                completion_percent=100,
                config={
                    'SocksPort': str(self.SOCKS_PORT),
                    'ExitNodes': '$' + exitFingerprint,
                    'ControlPort': str(self.CONTROL_PORT),
                    'DataDirectory': 'Connection_info',
                },
            )
        else:
            pass

        Helper.printOnScreen("\nChecking our endpoint: \n", MSG_TYPES.RESULT, mode=self.mode)
        url = 'http://'+str(ip).replace('.','-')+'.'+self.DOMAIN_URL
        result = self.query(url)
        if result is True:
            Helper.printOnScreen(('Successfully connected over TOR: %S' % url), MSG_TYPES.RESULT, mode=self.mode)

    def wirteIntoFile(self,raw):
        data = ''
        with open(self.OUTPUT_FILE,'r') as file:
            data = file.read()
        with open(self.OUTPUT_FILE,'w+') as file:
            file.write(data)
            file.write(raw+'\n')

    def wirteIntoFileJOSN(self,json):
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
        with open(self.GATHERED_NODES_PATH, 'w') as outfile:
            json.dump(exit_Nodes, outfile)

    #
    def connectToTORExitNode(self, exitNodeFingerprint, exitNodeIp, index, mode):
        # Start an instance of Tor configured to only exit through Russia. This prints
        # Tor's bootstrap information as it starts. Note that this likely will not
        # work if you have another Tor instance running.

        # Return values
        # 1 : Connection succussed
        # 2 : Connected but failed to check it
        # 3 : Connection failed

        if stem.util.system.is_windows():
            self.TOR_CONNECTION_TIMEOUT=90  ## MUST be 90 - DO NOT CHANGE IT

        start_time = time.time()
        result = False

        torConnection = Connection(mode=self.mode, pycurlTimeout=self.PYCURL_TIMEOUT, socksPort=self.SOCKS_PORT, controlPort=self.CONTROL_PORT,
                                   torConnectionTimeout=self.TOR_CONNECTION_TIMEOUT, domainUrl =self.DOMAIN_URL, domainUrlCheck = self.DOMAIN_URL_CHECK,
                                   domainCorrectMessageResult= self.DOMAIN__CORRECT_MESSAGE_RESULT, torCheckConnection =self.TOR_CHECK_CONNECTION,
                                   forceNotResponseMsg= self.FORCE_NOT_RESPONSE_MSG,
                                   exitNodeFingerprint=exitNodeFingerprint, exitNodeIp=exitNodeIp)
        result = torConnection.connect(index)
        try:
            url = ''
            if result.connectionStatus == CONNECTION_STATUS.CONNECTED.value:
                if mode == TASK_MODE.REQUEST_DOMAIN: #
                    #   RUN_MANYTIMES_MODE to send many sendRequests to the DNS so will have alot of information(port/id they use) about TOR DNS solver.
                    result = torConnection.sendRequests(self.RUN_MANYTIMES_MODE, self.REQUEST_TIMES)
                elif mode ==TASK_MODE.TOR_CONNECTION_CHECKING:  #'check': # check the connection reliability of the Tor exit node only
                    result = torConnection.checkTORConnection()
                elif mode == TASK_MODE.DNS_0x20_CHECKING: #'check-domain': # check if the website is accessible
                    result = torConnection.checkDNSFor0x20Encoding()
                elif mode == TASK_MODE.DNS_RESOLVER_COUNTER: #'check-domain': # check if the website is accessible
                    result = torConnection.sendRequestsWithResponseMode(self.RUN_MANYTIMES_MODE, self.REQUEST_TIMES,responseMode=False)

            return result

        except Exception as ex:
            torConnection.killConnection()
            traceback.print_exc(file=sys.stdout)
            print('Error.... 400000 - %s', str(ex))

        return result

    #
    def showArgu(self):
        parser = argparse.ArgumentParser(description='Enumerate all the exit nodes in TOR network -> CheckingRequest TOR connection via them || Request website.')
        group = parser.add_mutually_exclusive_group()
        group.add_argument("-l", "--verbose", action="store_true")
        group.add_argument("-q", "--quiet", action="store_true")
        parser.add_argument("x", type=int, help="the base")
        parser.add_argument("y", type=int, help="the exponent")
        args = parser.parse_args()
        answer = args.x ** args.y
        print(args)

    #
    def maintest(self,argv):
        if argv[1:] != []:  # on the server
            try:
                number_OF_Nodes = -1
                opt1 = argv[1]
                if len(argv) > 2:
                    number_OF_Nodes = int(argv[2])
                if opt1 == '-r':  # check the connections
                    self.requestDomainViaTor()
                elif opt1 == '-c':
                    self.checkTorConnection(number_OF_Nodes)
                elif opt1 == '-cd': # check the domain name connection
                    self.checkWebsiteConnection(number_OF_Nodes)

            except Exception as ex:
                print('maintest :' + str(ex))
                sys.exit(2)

    #
    def run(self):
        try:
            if self.opt == '-r':  # check the connections
                self.requestDomainViaTor()
            elif self.opt == '-c':
                self.checkTorConnection(self.REQUIRED_NODES)
            elif self.opt == '-cd':  # check the domain name connection
                self.checkWebsiteConnection(self.REQUIRED_NODES)
            elif self.opt == '-drc':  # check the domain name connection
                self.countDNSRequest()

        except Exception as ex:
            Helper.printOnScreenAlways('TORConnector - run %s'%str(ex),MSG_TYPES.ERROR)
            sys.exit(2)
            #maintest(['', '-c', '3'])

#
if __name__ == '__main__':
    TORFunctions.ProcesskillForWindows('tor.exe')
    con = TORConnections('-cd','-out', 5,runManyTimeMode=True)
    con.startTorConnection('8ED84B53BD9556CCBB036073A1AD508EC27CBE52', '173.246.38.148')