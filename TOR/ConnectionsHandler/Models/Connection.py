


import io
import os
import pycurl
import sys
import time
import certifi
import stem.process
import random

from tqdm import tqdm
from stem.util import term
from TOR.Helper.Helper import MSG_TYPES
from TOR.Helper.Helper import Helper
from TOR.Helper.Helper import MODE_TYPES
from TOR.NodeHandler import NodesHandler
from TOR.ConnectionsHandler import TORFunctions
from TOR.ConnectionsHandler.Models.Results import Result
from TOR.ConnectionsHandler.Models.Results import DOMAIN_STATUS
from TOR.ConnectionsHandler.Models.Results import CONNECTION_STATUS


from multiprocessing.dummy import Pool



class Connection:
    OUTPUT_FILE = 'result.txt'
    '''
    self.domain_url = 'dnstestsuite.space'
    self.DOMAIN_URL_CHECK = 'dnstestsuite.space/check'  # uses to check if the dns is supporting the 0x20 coding
    self.DOMAIN__CORRECT_RESULT = 'Works DNStestsuite.space@12.13.14.1'  # should be the same message in check.html page
    self.TOR_CHECK_CONNECTION = 'https://icanhazip.com'
    '''



    def __init__(self,mode,pycurlTimeout,socksPort,conrtrolPort,torConnectionTimeout,domainUrl,domainUrlCheck,domainCorrectMessageResult,torCheckConnection,
                 exitNodeFingerprint,exitNodeIp ) : #opt='r', mode='-none' , ):
        #self.mode = mode
        #self.opt = opt
        self.torConnectionTimeouT = torConnectionTimeout
        self.pycurlTimeout = pycurlTimeout
        self.socksPort = socksPort
        self.conrtrolPort = conrtrolPort
        self.domainUrl = domainUrl
        self.domainUrlCheck = domainUrlCheck
        self.domainCorrectMessageResult = domainCorrectMessageResult
        self.torCheckConnection = torCheckConnection
        self.exitNodeFingerprint = exitNodeFingerprint
        self.exitNodeIp = exitNodeIp
        self.mode = mode
        '''  # OTHER WAY TO IMPLEMENT THE CONSTRUCTOR
         def __init__(self, **kwargs):
            valid_keys = ["mode", "pycurlTimeout", "socksPort", "conrtrolPort", "torConnectionTimeout", "domainUrl", "domainUrlCheck", "domainCorrectResult", "torCheckConnection", "exitNodeFingerprint", "exitNodeIp"]
            for key in valid_keys:
                self.__dict__[key] = kwargs.get(key)
        '''

    #
    def connect(self,index):
        Helper.printOnScreen((term.format("\n\n%d- Starting Tor, connecting to: %s", term.Attr.BOLD) % (index, self.exitNodeIp)),
                             mode=self.mode)
        Helper.printOnScreen('Fingerprint: ' + self.exitNodeFingerprint, MSG_TYPES.RESULT, mode=self.mode)
        self.wirteIntoFile('\n%d- Starting Tor, connecting to: %s' % (index, self.exitNodeIp))
        self.wirteIntoFile('Fingerprint: ' + self.exitNodeFingerprint)

        try:
            self.tor_process = stem.process.launch_tor_with_config(
                timeout = self.torConnectionTimeouT,
                completion_percent = 100,
                config = {
                    'SocksPort': str(self.socksPort),
                    'ExitNodes': '$' + self.exitNodeFingerprint,
                    'ControlPort': str(self.conrtrolPort),
                    # 'DataDirectory': 'Connection_info',
                },
            )
            Helper.printOnScreen('Connected, Checking...', color=MSG_TYPES.YELLOW, mode=self.mode)
            self.wirteIntoFile('Connected, Checking...')

            return Result(CONNECTION_STATUS.CONNECTED,DOMAIN_STATUS.STATELESS)

        except Exception as ex:
            Helper.printOnScreen(('Connection - connect: ' + str(ex)), color=MSG_TYPES.ERROR, mode=self.mode)
            Helper.printOnScreen('Connection failed! - Timed out', color=MSG_TYPES.ERROR, mode=self.mode)
            self.wirteIntoFile('Connection failed! - Timed out')
            return Result(CONNECTION_STATUS.NOT_CONNECTED,DOMAIN_STATUS.STATELESS)

    #
    def killConnection(self):
        self.tor_process.kill()  # stops tor

    #
    def query(self,url):
        # https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=849845;msg=127
        # https://stackoverflow.com/questions/29876778/tor-tutorial-speaking-to-russia-stuck-at-45-50
        # Uses pycurl to fetch a site using the proxy on the SOCKS_PORT.
        output = io.BytesIO()
        query = pycurl.Curl()
        query.getinfo(pycurl.PRIMARY_IP)
        query.setopt(pycurl.CAINFO, certifi.where())
        query.setopt(pycurl.URL, url)

        query.setopt(pycurl.VERBOSE, False)
        query.setopt(pycurl.TIMEOUT, self.pycurlTimeout)
        query.setopt(pycurl.PROXY, '127.0.0.1')
        query.setopt(pycurl.PROXYPORT,  self.socksPort)
        query.setopt(pycurl.IPRESOLVE, pycurl.IPRESOLVE_V4)
        query.setopt(pycurl.USERAGENT, 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:8.0) Gecko/20100101 Firefox/8.0')
        query.setopt(pycurl.PROXYTYPE, pycurl.PROXYTYPE_SOCKS5_HOSTNAME)
        query.setopt(pycurl.WRITEFUNCTION, output.write)

        try:
            query.perform()
            temp = output.getvalue()
            #print("result: %s" % str(temp))
            return str(temp.decode('utf-8')).strip()

        except Exception as ex:
            Helper.printOnScreen(("Unable to reach %s (%s)" % (url, ex)), MSG_TYPES.ERROR, mode=self.mode)
            return b'unreachable'

        except pycurl.error as exc:
            Helper.printOnScreen(("Unable to reach %s (%s)" % (url, exc)),MSG_TYPES.ERROR,mode=self.mode)
            #print('pyCrul')
            return b'unreachable'

    #
    def request(self,runManytimesMode,requestTimes):
        try:
            randNumber = random.randint(1, 10000)  # to avoid cashing
            Helper.printOnScreen((term.format("Requesting our webiste:\n", term.Attr.BOLD)), color=MSG_TYPES.RESULT,
                                 mode=self.mode)
            domain = str(self.exitNodeIp).replace('.', '-') + '.' + self.domainUrl
            url = 'http://' + domain
            result = self.query(url)


            #   requesting many times/ testing the same node 100 times./ testing how random is the PORT number and Requset ID
            if runManytimesMode is True:
                pool = Pool(requestTimes)
                results = []
                for i in range(1, requestTimes):
                    sub_Domain = ("%d_%d_%s" % (randNumber,i,domain))
                    url = 'http://' + sub_Domain
                    Helper.printOnScreen(('Requesting: %s' % url),
                                         color=MSG_TYPES.RESULT,
                                         mode=self.mode)
                    # TODO: need to be solved
                    #pool.apply_async(self.query(url), (10,), callback=)
                    results.append(pool.apply_async(self.query(url)))  # no need to wait for the reponcse

                pool.close()
                pool.join()
                #for future in futures:
                    #print(future.get())

            self.killConnection()
            if result is True:
                Helper.printOnScreenAlways(('Successfully connected over TOR: %s' % url), color=MSG_TYPES.RESULT)
                return Result(CONNECTION_STATUS.CONNECTED, DOMAIN_STATUS.ACCESSIBLE)
            else:
                return Result(CONNECTION_STATUS.CONNECTED, DOMAIN_STATUS.NOT_ACCESSIBLE)

        except Exception as ex:
            self.killConnection()
            TORFunctions.loggingError('Connection - request: %s' % str(ex))
            #Helper.printOnScreenAlways(('Connection - request: %s' % ex), color=MSG_TYPES.ERROR)
            return Result(CONNECTION_STATUS.CONNECTED, DOMAIN_STATUS.STATELESS) # or something went wrong

    #   this function is just check if is establishing connection over TOR working
    def checkTORConnection(self):
        try:
            url = self.torCheckConnection
            #if self.exitNodeIp == str(self.query(url), 'utf-8').strip():
            if self.exitNodeIp == self.query(url):
                Helper.printOnScreen('Connected Successfully', color=MSG_TYPES.RESULT, mode=self.mode)
                self.wirteIntoFile('Connected Successfully')
                self.killConnection()
                return Result(CONNECTION_STATUS.CONNECTED, DOMAIN_STATUS.ACCESSIBLE)
            else:
                Helper.printOnScreen('Checking Failed ', color=MSG_TYPES.ERROR, mode=self.mode)
                self.wirteIntoFile('Checking Failed ')
                self.killConnection()
                return Result(CONNECTION_STATUS.CONNECTED, DOMAIN_STATUS.NOT_ACCESSIBLE)

        except Exception as ex:
            self.killConnection()
            TORFunctions.loggingError('Connection - checkTORConnection: %s' % str(ex))
            #Helper.printOnScreenAlways(('Connection - checkTORConnection: %s' % ex), color=MSG_TYPES.ERROR)
            return Result(CONNECTION_STATUS.CONNECTED, DOMAIN_STATUS.STATELESS) # or something went wrong


    #   This function will check for 0x20 bit encoding
    def checkDNSFor0x20Encoding(self):
        try:
            randNumber = random.randint(1, 10000) # to avoid cashing
            domain = (str(self.exitNodeIp).replace('.', '-') + '.' + self.domainUrlCheck).strip()
            subDomain = '%d_check_%s' % (randNumber, domain)  # 768_check_12.23.243.12.dnstestsuite.space/check
            url = 'http://' + subDomain
            message = self.domainCorrectMessageResult
            result_message = 'none'

            try:
                result_message = self.query(url) #str((self.query(url).decode('utf-8')).strip())
            except:
                result_message = 'unreachable'

            # print('result_message: ' + result_message)
            # print('message: ' + message)

            if message == result_message:   # matches
                Helper.printOnScreen(('Connected Successfully to : %s' % subDomain), color=MSG_TYPES.RESULT,
                                     mode=self.mode)
                self.wirteIntoFile('Connected Successfully to : %s' % subDomain)
                result = Result(CONNECTION_STATUS.CONNECTED, DOMAIN_STATUS.ACCESSIBLE)
            else:
                Helper.printOnScreen(('Checking Failed : %s' % subDomain), color=MSG_TYPES.ERROR, mode=self.mode)
                self.wirteIntoFile('Checking Failed : %s' % subDomain)
                # re-checking
                Helper.printOnScreenAlways('re-Checking...',color=MSG_TYPES.ANY)
                subDomain = '%d_re_check_%s' % (randNumber, domain)  # 12321_re_check_12.23.243.12.dnstestsuite.space/check
                url = 'http://' + subDomain
                result_message = 'none'
                try:
                    result_message = self.query(url)
                except:
                    result_message = 'unreachable'

                #print('result_message: ' + result_message.decode('utf-8'))
                #print('message: ' + message)

                if message == result_message:
                    Helper.printOnScreen(('re-Checking Successfully to : %s' % subDomain), color=MSG_TYPES.RESULT,
                                         mode=self.mode)
                    self.wirteIntoFile('re-Checking Successfully to : %s' % subDomain)
                    result = Result(CONNECTION_STATUS.CONNECTED, DOMAIN_STATUS.RE_ACCESSIBLE)
                else:
                    Helper.printOnScreen(('re-Checking Failed : %s' % subDomain), color=MSG_TYPES.ERROR,
                                         mode=self.mode)
                    self.wirteIntoFile('re-Checking Failed : %s' % subDomain)
                    result = Result(CONNECTION_STATUS.CONNECTED, DOMAIN_STATUS.NOT_ACCESSIBLE)

            self.killConnection()
            return result

        except Exception as ex:
            TORFunctions.loggingError('Connection - checkDNSFor0x20Encoding: %s' % str(ex))
            self.killConnection()
            return Result(CONNECTION_STATUS.CONNECTED, DOMAIN_STATUS.NOT_ACCESSIBLE)

    #
    def wirteIntoFile(self, raw):
        data = ''
        with open(self.OUTPUT_FILE, 'r') as file:
            data = file.read()
        with open(self.OUTPUT_FILE, 'w+') as file:
            file.write(data)
            file.write(raw + '\n')