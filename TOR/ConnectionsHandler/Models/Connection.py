
"""
TOR connection class
"""

import io
import os
import pycurl
import sys
import time
import traceback
import certifi
import stem.process
import random

from async import thread
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

    #
    def __init__(self,mode,pycurlTimeout,socksPort,controlPort,torConnectionTimeout,domainUrl,domainUrlCheck,domainCorrectMessageResult,torCheckConnection,
                 forceNotResponseMsg, exitNodeFingerprint,exitNodeIp) :

        self.torConnectionTimeouT = torConnectionTimeout
        self.pycurlTimeout = pycurlTimeout
        self.socksPort = socksPort
        self.controlPort = controlPort
        self.domainUrl = domainUrl
        self.domainUrlCheck = domainUrlCheck
        self.domainCorrectMessageResult = domainCorrectMessageResult
        self.torCheckConnection = torCheckConnection
        self.exitNodeFingerprint = exitNodeFingerprint
        self.exitNodeIp = exitNodeIp
        self.forceNotResponseMsg = forceNotResponseMsg
        self.mode = mode

        '''  # OTHER WAY TO IMPLEMENT THE CONSTRUCTOR
         def __init__(self, **kwargs):
            valid_keys = ["mode", "pycurlTimeout", "socksPort", "controlPort", "torConnectionTimeout", "domainUrl", "domainUrlCheck", "domainCorrectResult", "torCheckConnection", "exitNodeFingerprint", "exitNodeIp"]
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
                    'ControlPort': str(self.controlPort),
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
            return str(temp.decode('utf-8')).strip()

        except Exception as ex:
            Helper.printOnScreen(("Unable to reach %s (%s)" % (url, ex)), MSG_TYPES.ERROR, mode=self.mode)
            return b'unreachable'

        except pycurl.error as exc:
            Helper.printOnScreen(("Unable to reach %s (%s)" % (url, exc)),MSG_TYPES.ERROR,mode=self.mode)
            return b'unreachable'

    #
    def sendRequests(self, runManytimesMode, requestTimes):
        try:

            Helper.printOnScreen((term.format("Requesting our webiste:\n", term.Attr.BOLD)), color=MSG_TYPES.RESULT,
                                 mode=self.mode)
            domain = str(self.exitNodeIp).replace('.', '-') + '.' + self.domainUrl
            url = 'http://' + domain
            result = self.query(url)

            #   requesting many times/ testing the same node 100 times./ testing how random is the PORT number and Requset ID
            if runManytimesMode is True:
                self.requestDomain(domain=domain, times=requestTimes)

            self.killConnection()
            if result is True:
                Helper.printOnScreenAlways(('Successfully connected over TOR: %s' % url), color=MSG_TYPES.RESULT)
                return Result(CONNECTION_STATUS.CONNECTED, DOMAIN_STATUS.ACCESSIBLE)
            else:
                return Result(CONNECTION_STATUS.CONNECTED, DOMAIN_STATUS.NOT_ACCESSIBLE)

        except Exception as ex:
            self.killConnection()
            TORFunctions.loggingError('Connection - sendRequests: %s' % traceback.format_exc())
            return Result(CONNECTION_STATUS.CONNECTED, DOMAIN_STATUS.STATELESS) # or something went wrong

    #
    def sendRequestsWithResponseMode(self, runManytimesMode, requestTimes, responseMode=True):
        try:
            Helper.printOnScreen((term.format("Requesting our webiste:\n", term.Attr.BOLD)), color=MSG_TYPES.RESULT,
                                 mode=self.mode)
            domain = str(self.exitNodeIp).replace('.', '-') + '.' + self.domainUrl
            url = 'http://' + domain
            #   requesting many times/ testing the same node 100 times./ testing how random is the PORT number and Requset ID
            self.requestDomain(domain=domain, times=requestTimes, responseMode=responseMode,
                                   addtionname=self.forceNotResponseMsg, )
            self.killConnection()
        except Exception as ex:
            self.killConnection()
            TORFunctions.loggingError('Connection - sendRequests: %s' % traceback.format_exc())

    #
    def requestDomainThread(self, domain, times, responseMode, addtionname= None):
             # to avoid cashing
            pool = Pool(times)
            results = []
            try:
                for i in range(1, times):
                    randNumber = random.randint(1, 10000)
                    if addtionname is None:
                        sub_Domain = ("%d_%d_%d_%s" % (randNumber,times, i, domain))
                    else:
                        sub_Domain = ("%d_%s_%s" % (times,addtionname,  domain))

                    url = 'http://' + sub_Domain
                    Helper.printOnScreen(('%d- Requesting: %s' %(i, url)),
                                         color=MSG_TYPES.RESULT,
                                         mode=self.mode)

                    # TODO: need to be solved
                    result_ =results.append(pool.apply_async(self.query(url)))  # no need to wait for the reponcse
                    print(result_)
                    if result_ is not None:
                        if 'sock' in result_.lower() and i > 3:
                            print(result_)
                            pool.close()
                            pool.join()
                            break

            except Exception as ex:
                print("requestDomain")
                print(ex)

            pool.close()
            pool.join()

    #
    def requestDomain(self, domain, times,responseMode,addtionname= None):
            # to avoid cashing
            results = []
            try:
                randNumber = random.randint(1, 10000)
                for i in range(1, times):

                    if addtionname is None:
                        sub_Domain = ("%d_%d_%d_%s" % (randNumber,times, i, domain))
                    else:
                        sub_Domain = ("%d_%s_%s" % (randNumber,addtionname,  domain))

                    url = 'http://' + sub_Domain
                    Helper.printOnScreen(('%d- Requesting: %s' %(i, url)),
                                         color=MSG_TYPES.RESULT,
                                         mode=self.mode)
                    # TODO: need to be solved
                    result_ = self.query(url) # no need to wait for the reponcse

                    if result_ is not None:
                        if 'sock' in result_.lower() and i > 3:
                            print(result_)
                            break
            except Exception as ex:
                print("requestDomain")
                print(ex)


    #
    def checkTORConnection(self):
        '''
            Check if is establishing connection over TOR working.
        '''

        try:
            url = self.torCheckConnection
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
            TORFunctions.loggingError('Connection - checkTORConnection: %s' % traceback.format_exc())
            return Result(CONNECTION_STATUS.CONNECTED, DOMAIN_STATUS.STATELESS) # or something went wrong

    #
    def checkDNSFor0x20Encoding(self):
        '''
            Check for 0x20 bit encoding
        '''

        try:
            randNumber = random.randint(1, 10000) # to avoid cashing
            domain = (str(self.exitNodeIp).replace('.', '-') + '.' + self.domainUrlCheck).strip()
            subDomain = '%d_check_%s' % (randNumber, domain)  # 768_check_12.23.243.12.dnstestsuite.space/check
            url = 'http://' + subDomain
            message = self.domainCorrectMessageResult
            result_message = 'none'
            try:
                result_message = self.query(url)

            except:
                result_message = 'unreachable'

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

                if message == result_message:
                    Helper.printOnScreen(('re-Checking Successful : %s' % subDomain), color=MSG_TYPES.RESULT,
                                         mode=self.mode)
                    self.wirteIntoFile('re-Checking Successful : %s' % subDomain)
                    result = Result(CONNECTION_STATUS.CONNECTED, DOMAIN_STATUS.RE_ACCESSIBLE)

                else:
                    Helper.printOnScreen(('re-Checking Failed : %s' % subDomain), color=MSG_TYPES.ERROR,
                                         mode=self.mode)
                    self.wirteIntoFile('re-Checking Failed : %s' % subDomain)
                    result = Result(CONNECTION_STATUS.CONNECTED, DOMAIN_STATUS.NOT_ACCESSIBLE)

            self.killConnection()

            return result

        except Exception as ex:
            TORFunctions.loggingError('Connection - checkDNSFor0x20Encoding: %s' % traceback.format_exc())
            self.killConnection()

            return Result(CONNECTION_STATUS.CONNECTED, DOMAIN_STATUS.NOT_ACCESSIBLE)

    #


    #
    def wirteIntoFile(self, raw):
        data = ''
        with open(self.OUTPUT_FILE, 'r') as file:
            data = file.read()

        with open(self.OUTPUT_FILE, 'w+') as file:
            file.write(data)
            file.write(raw + '\n')