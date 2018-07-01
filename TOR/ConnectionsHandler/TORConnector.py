import datetime
import functools
import getopt
import io
import json
import os
import pycurl
import sys
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

from TOR.Helper.Helper import MSG_TYPES
from TOR.Helper.Helper import Helper
from TOR.Helper.Helper import MODE_TYPES
from TOR.NodeHandler import NodesHandler


class TORConnections:

    def __init__(self, opt='r', mode='-none',requiredNodes=10000):
        self.mode = mode
        self.opt = opt
        self.requiredNodes = requiredNodes
        self.SOCKS_PORT = 7000
        self.CONRTROL_PORT = 9051
        self.DOMAIN_URL = 'dnstestsuite.space'
        self.DOMAIN_URL_CHECK = 'https://icanhazip.com'
        self.OUTPUT_FILE = 'result.txt'
        self.NODES_PATH = 'TOR/ConnectionsHandler/Nodes/ExitNodesJSON.json'
        self.TOR_CONNECTION_TIMEOUT = 20  # timeout before we give up on a circuit
        self.PYCURL_TIMEOUT = 40

        self.CONSUMER_KEY = ""
        self.CONSUMER_SECRET = ""
        self.ACCESS_TOKEN = ""
        self.ACCESS_TOKEN_SECRET = ""

    #NODEPATH = 'Info\ExitNodesJSON.json'
    #https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=849845;msg=127
    #https://stackoverflow.com/questions/29876778/tor-tutorial-speaking-to-russia-stuck-at-45-50
    def query(self,url):
      # Uses pycurl to fetch a site using the proxy on the SOCKS_PORT.
      output = io.BytesIO()
      query = pycurl.Curl()
      query.getinfo(pycurl.PRIMARY_IP)
      query.setopt(pycurl.CAINFO, certifi.where())
      query.setopt(pycurl.URL, url)

      query.setopt(pycurl.VERBOSE, False)
      query.setopt(pycurl.TIMEOUT, self.PYCURL_TIMEOUT)
      query.setopt(pycurl.PROXY, '127.0.0.1')
      query.setopt(pycurl.PROXYPORT,  self.SOCKS_PORT)
      query.setopt(pycurl.IPRESOLVE, pycurl.IPRESOLVE_V4)
      query.setopt(pycurl.USERAGENT, 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:8.0) Gecko/20100101 Firefox/8.0')
      query.setopt(pycurl.PROXYTYPE, pycurl.PROXYTYPE_SOCKS5_HOSTNAME)
      query.setopt(pycurl.WRITEFUNCTION, output.write)

      try:
        query.perform()
        temp =output.getvalue()
        return (temp)

      except pycurl.error as exc:
        Helper.printOnScreen(("Unable to reach %s (%s)" % (url, exc)),MSG_TYPES.ERROR.value,mode=self.mode)

        return ("Unable to reach %s (%s)" % (url, exc))
        ##return False

    def stream_event(controller, event):
      if event.status == StreamStatus.SUCCEEDED and event.circ_id:
        circ = controller.get_circuit(event.circ_id)

        exit_fingerprint = circ.path[-1][0]
        exit_relay = controller.get_network_status(exit_fingerprint)
        print("Exit relay for our connection to %s" % (event.target))
        print("  address: %s:%i" % (exit_relay.address, exit_relay.or_port))
        print("  fingerprint: %s" % exit_relay.fingerprint)
        print("  nickname: %s" % exit_relay.nickname)
        print("  locale: %s" % controller.get_info("ip-to-country/%s" % exit_relay.address, 'unknown'))
        print("")

    def loadExitNodes(self):
        cur_path = os.path.dirname(__file__)
        # read all the nodes
        new_path = os.path.relpath(self.NODES_PATH, cur_path)

        with open(new_path) as f:
            jsonObjects= json.load(f)
            random.shuffle(jsonObjects)
            return jsonObjects

    def checkTorConnectionForLinux(self,numberOfNodes=10000):
        start_time = time.time()
        nodesCount = 0
        successfully_Connections = 0
        successfully_Connections_checking_failed = 0
        failed_Connections = 0

        # load
        jsonObjects = self.loadExitNodes()
        #random.shuffle(jsonObjects)

        result = 3 # assume that connection failed

        if stem.util.system.is_windows():
            # Terminate the tor in case if it is still running
            self.ProcesskillForWindows('tor.exe')

        print('\n')
        totalNodes=len(jsonObjects)
        #for obj in tqdm(jsonObjects):
        for obj in jsonObjects:
            ip = str(obj['ExitNode']['Address'].encode("ascii"),'utf-8')
            fingerprint = str(obj['ExitNode']['Fingerprint'].encode("ascii"),'utf-8')
            # https://stackoverflow.com/questions/21827874/timeout-a-python-function-in-windows
            result = self.getTORExitPoint(fingerprint, ip, nodesCount+1,'check')

            try:
                if result == 1:    # Connection succeed
                    successfully_Connections += 1

                elif result == 2:   # Connection succeed , but checking failed.
                    successfully_Connections_checking_failed += 1

                elif result == 3:   # Connection failed
                    failed_Connections += 1

            #TODO: need to check why we have here
            except:
                failed_Connections += 1

            # total  number of nodes

            nodesCount = nodesCount + 1
            number_of_Nodes=int(numberOfNodes)
            if nodesCount == number_of_Nodes:
                break

        time_taken = time.time() - start_time

        print("\n--------------------------")
        print('Finished in  %0.2f seconds' % (time_taken))
        print(term.format('Found ' + str(nodesCount) + ' Exit nodes', term.Attr.BOLD))
        print(term.format(str(successfully_Connections) + ': were connected successfully', term.Attr.BOLD))
        print(term.format(str(successfully_Connections_checking_failed) + ': were connected successfully, but checking failed.', term.Attr.BOLD))
        print(term.format(str(failed_Connections) + ': failed ', term.Attr.BOLD))
        print("\n--------------------------")
        print(term.format('Checking Success rate:   '+str(successfully_Connections/nodesCount * 100)+'%', term.Color.GREEN))
        print(term.format('Checking Failed rate:    '+str(successfully_Connections_checking_failed/nodesCount * 100)+'%', term.Color.GREEN))
        print(term.format('Failed Connections rate: '+str(failed_Connections/nodesCount * 100)+'%', term.Color.RED))

        data = ''
        with open(self.OUTPUT_FILE,'r') as file:
            data = file.read()
        with open(self.OUTPUT_FILE,'w+') as file:
            file.write(data)
            file.write("\n--------------------------\n")
            file.write("\n--------------------------\n")
            file.write('Finished in  %0.2f seconds\n' % (time_taken))
            file.write('Found ' + str(nodesCount) + ' Exit nodes:\n')
            file.write('   '+str(successfully_Connections) + ': were connected successfully\n')
            file.write('   '+str(successfully_Connections_checking_failed) + ': were connected successfully, but checking failed.\n')
            file.write('   '+str(failed_Connections) + ': failed\n')
            file.write('\n--------------------------\n')
            file.write('Checking Success rate:   '+str(successfully_Connections/nodesCount * 100)+'% \n')
            file.write('Checking Failed rate:    '+str(successfully_Connections_checking_failed/nodesCount * 100)+'% \n')
            file.write('Failed Connections rate: '+str(failed_Connections/nodesCount * 100)+'% \n')


    # check the domain via our DNS
    def requestDomainViaTor(self):
        Helper.printOnScreenAlways('Requesting %s  via TOR ' % self.DOMAIN_URL_CHECK)

        start_time = time.time()
        nodesCount = 0
        successfully_Connections = 0
        successfully_Connections_checking_failed = 0
        failed_Connections = 0

        jsonObjects = self.loadExitNodes()

        if stem.util.system.is_windows():
            # Terminate the tor in case if it is still running
            self.ProcesskillForWindows('tor.exe')

        for obj in tqdm(jsonObjects, ncols=80, desc='Requesting Domain via our DNS'):
            ip = str(obj['ExitNode']['Address'].encode("ascii"), 'utf-8')
            fingerprint = str(obj['ExitNode']['Fingerprint'].encode("ascii"), 'utf-8')
            # https://stackoverflow.com/questions/21827874/timeout-a-python-function-in-windows
            result = self.getTORExitPoint(fingerprint, ip, nodesCount + 1, 'request')

            try:
                if result == 1:    # Connection succeed
                    successfully_Connections += 1
                elif result == 2:   # Connection succeed , but checking failed.
                    successfully_Connections_checking_failed += 1
                elif result == 3:   # Connection failed
                    failed_Connections += 1
            #TODO: need to check why we have here
            except:
                failed_Connections += 1

    def ProcesskillForWindows(self,process_name):
        try:
          killed = os.system('taskkill /f /im ' + process_name)
        except Exception as e:
          killed = 0
        return killed

    def print_bootstrap_lines(self,line):
      # print line
      if "Bootstrapped " in line:
        print(term.format(line, term.Color.GREEN))

    def progressBar(count, total, suffix='', color=term.Color.GREEN):
        bar_len = 60
        filled_len = int(round(bar_len * count / float(total)))

        percents = round(100.0 * count / float(total), 1)
        bar = '=' * filled_len + '-' * (bar_len - filled_len)

        sys.stdout.write(term.format('[%s] %s%s ...%s\r' % (bar, percents, '%', suffix),color))
        sys.stdout.flush()

    #TODO: need to be removed
    def start(self,exitFingerprint, ip):
        # Start an instance of Tor configured to only exit through Russia. This prints
        # Tor's bootstrap information as it starts. Note that this likely will not
        # work if you have another Tor instance running.

        # Terminate the tor in case if it is still running
        if not (stem.util.system.get_pid_by_port(self.CONRTROL_PORT)):
            print(term.format("Starting Tor, connecting to: %s \n", term.Attr.BOLD) % ip)
            tor_process = stem.process.launch_tor_with_config(
                timeout=90,
                completion_percent=100,
                config={
                    'SocksPort': str(self.SOCKS_PORT),
                    'ExitNodes': '$' + exitFingerprint,
                    'ControlPort': str(self.CONRTROL_PORT),
                    'DataDirectory': 'Connection_info',
                },
            )
        else:
            pass

        Helper.printOnScreen("\nChecking our endpoint:\n", MSG_TYPES.RESULT.value, mode=self.mode)
        #print(term.format("\nChecking our endpoint:\n", term.Attr.BOLD))
        url = 'http://'+str(ip).replace('.','-')+'.'+self.DOMAIN_URL
        result = self.query(url)
        if result is True:
            Helper.printOnScreen(('Successfully connected over TOR: %S' % url), MSG_TYPES.RESULT.value, mode=self.mode)
            #print(term.format(('Successfully connected over TOR: %S' % url), term.Color.GREEN))
        #tor_process.kill()  # stops tor

    def wirteIntoFile(self,raw):
        data = ''
        with open(self.OUTPUT_FILE,'r') as file:
            data = file.read()
        with open(self.OUTPUT_FILE,'w+') as file:
            file.write(data)
            file.write(raw+'\n')

    def getTORExitPoint(self,exitFingerprint, ip,index,mode):
        # Start an instance of Tor configured to only exit through Russia. This prints
        # Tor's bootstrap information as it starts. Note that this likely will not
        # work if you have another Tor instance running.

        # Return values
        # 1 : Connection succussed
        # 2 : Connected but failed to check it
        # 3 : Connection failed

        global TOR_CONNECTION_TIMEOUT
        if stem.util.system.is_windows():
            TOR_CONNECTION_TIMEOUT=90

        start_time = time.time()
        result = 3


        Helper.printOnScreen((term.format("\n\n%d- Starting Tor, connecting to: %s", term.Attr.BOLD) % (index,ip)),mode=self.mode)
        Helper.printOnScreen('Fingerprint: ' + exitFingerprint, MSG_TYPES.RESULT.value, mode=self.mode)
        self.wirteIntoFile('\n%d- Starting Tor, connecting to: %s' % (index,ip))
        self.wirteIntoFile('Fingerprint: ' + exitFingerprint)

        try:
            tor_process = stem.process.launch_tor_with_config(
                timeout=TOR_CONNECTION_TIMEOUT,
                completion_percent=100,
                config={
                    'SocksPort': str(self.SOCKS_PORT),
                    'ExitNodes': '$' + exitFingerprint,
                    'ControlPort': str(self.CONRTROL_PORT),
                     #'DataDirectory': 'Connection_info',
                },
            )
        except Exception as ex:
            Helper.printOnScreen(('getTORExitPoint: '+ str(ex)),color=MSG_TYPES.ERROR, mode=self.mode)
            Helper.printOnScreen('Connection failed! - Timed out',color=MSG_TYPES.ERROR, mode=self.mode)
            self.wirteIntoFile('Connection failed! - Timed out')
            return 3

        Helper.printOnScreen('Connected, Checking...',color=MSG_TYPES.YELLOW.value, mode=self.mode)
        self.wirteIntoFile('Connected, Checking...')
        try:

            url = ''
            if mode == 'request': #-----------------------------------------------------------------------------------------------------------HERE
                Helper.printOnScreen((term.format("\nChecking our endpoint:\n", term.Attr.BOLD)),color=MSG_TYPES.RESULT.value, mode=self.mode)
                url = 'http://' + str(ip).replace('.', '-') + '.' + self.DOMAIN_URL
                result = self.query(url)
                if result is True:
                    print(term.format(('Successfully connected over TOR: %s' % url), term.Color.GREEN))

            elif mode == 'check':
                url = self.DOMAIN_URL_CHECK
                if ip == str(self.query(url),'utf-8').rstrip():
                    Helper.printOnScreen('Connected Successfully', color=MSG_TYPES.RESULT.value, mode=self.mode)
                    self.wirteIntoFile('Connected Successfully2')
                    result = 1
                else:
                    Helper.printOnScreen('Failed Checking',color=MSG_TYPES.ERROR.value, mode=self.mode)
                    self.wirteIntoFile('Failed Checking')
                    result = 2

        except Exception as ex:
            Helper.printOnScreen(('getTORExitPoint: '+ str(ex)),color=MSG_TYPES.ERROR.value, mode=self.mode)
            #tor_process.kill()  # stops tor
            result = 2
            Helper.printOnScreen('Failed Checking',color=MSG_TYPES.ERROR.value, mode=self.mode)
            self.wirteIntoFile('Failed Checking')

        tor_process.kill()  # stops tor

        return result

    def printToday(self):
        open(self.OUTPUT_FILE, 'w').close()
        date = datetime.datetime.now()
        date = (((str(date)).split('.')[0]).split(' ')[1] + ' ' + ((str(date)).split('.')[0]).split(' ')[0])
        date = ("Date %s" % date)
        print(date, term.Color.GREEN)
        # print(term.format(date, term.Color.GREEN))

    def showArgu(self):
        parser = argparse.ArgumentParser(description='Enumerate all the exit nodes in TOR network -> Check TOR connection via them || Request website.')
        group = parser.add_mutually_exclusive_group()
        group.add_argument("-l", "--verbose", action="store_true")
        group.add_argument("-q", "--quiet", action="store_true")
        parser.add_argument("x", type=int, help="the base")
        parser.add_argument("y", type=int, help="the exponent")
        args = parser.parse_args()
        answer = args.x ** args.y
        print(args)

    def maintest(self,argv):
        if argv[1:] != []:  # on the server
            try:
                numberOFNodes = -1
                opt1 = argv[1]
                if len(argv) > 2:
                    numberOFNodes = int(argv[2])
                if opt1 == '-r':  # check the connections
                    self.requestDomainViaTor()
                elif opt1 == '-c':
                    self.checkTorConnectionForLinux(numberOFNodes)

            except Exception as ex:
                print('maintest :' + str(ex))

                sys.exit(2)

    def run(self):
        try:
            if self.opt == '-r':  # check the connections
                self.requestDomainViaTor()
            elif self.opt == '-c':
                self.checkTorConnectionForLinux(self.requiredNodes)

        except Exception as ex:
            Helper.printOnScreenAlways(ex,MSG_TYPES.ERROR)
            sys.exit(2)
            #maintest(['', '-c', '3'])

    '''  
    if __name__ == '__main__':
        argv =sys.argv
        if argv[1:] != []:  # on the server
            try:
                numberOFNodes= -1
                opt1 = argv[1]
                if len(argv) > 2:
                    numberOFNodes = int(argv[2])
                if opt1 == '-r':    # check the connections
                    requestDomainViaTor()
                elif opt1 == '-c':
                    checkTorConnectionForLinux(numberOFNodes)

            except:
                sys.exit(2)

        else:  # locally
          #showArgu()
          maintest(['','-c','3'])

          print(term.format("ERROR: specify: '-s' for running on the server, '-l' for running it locally-checking" , term.Color.RED))

        #176.10.104.243
        #167.10.104.240
        # start("38A42B8D7C0E6346F4A4821617740AEE86EA885B", "185.107.70.202") # works
    
        start('7016E939A2DD6EF2FB66A33F1DD45357458B737F', '92.195.107.176')
        ##dig()
    
        ProcesskillForWindows('tor.exe')
    
        start("47C42E2094EE482E7C9B586B10BABFB67557030B", "185.220.101.34") # works
        ProcesskillForWindows('tor.exe')
    
        start('8EBB8D1CF48FE2AB95C451DA8F10DB6235F40F8A','51.15.13.245') # not
        ProcesskillForWindows('tor.exe')
        #"185.220.101.34", "Fingerprint":
    
       '''




