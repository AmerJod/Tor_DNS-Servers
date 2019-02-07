#! /usr/bin/env python3

'''
    This file is to fetch files from and to servers(DNS/WebServer)
    YOU MUST HAVE THE KEY STORE ON YOUR MACHINE.
'''

import sys
import datetime
import os
from enum import Enum
from MoveFiles import MoveFiles
from Helper import Helper
from Helper import MSG_TYPES


DNS_SERVERIP = '34.198.193.29'
WEB_SERVERIP = '52.20.33.59'
DNS_SERVER_KEY = "C:/pem/DNS_MSc_Thesis_amer.pem"
WEB_SERVER_KEY = "C:/pem/DNS_MSc_Thesis_amer.pem"

#
class FETCHFROM_OPT(Enum):
    FromDNS = 'scp -r -i scp -r -i %s ' + 'ubuntu@%s' % DNS_SERVERIP + ':/home/ubuntu/%s "%s" '
    FromDNSLogs = 'scp -r -i scp -r -i %s ' + 'ubuntu@%s' % DNS_SERVERIP + ':/home/ubuntu/%s/Logs "%s" '
    FromDNSJSON = 'scp -r -i scp -r -i %s ' + 'ubuntu@%s' % DNS_SERVERIP + ':/home/ubuntu/%s/JSON "%s" '
    FromWebServer = 'scp -r -i %s ' + 'ubuntu@%s' % WEB_SERVERIP + ':/home/ubuntu/%s "%s" '
    FromWebServerJOSNs = 'scp -r -i %s ' + 'ubuntu@%s' % WEB_SERVERIP + ':/home/ubuntu/%s/JSON "%s" '

#
class FETCHFILE_OPT(Enum):
    All = 'all'
    Logs = 'logs'
    JSON = 'json'

#
class FetchFiles:
    DnsServerPath = 'dns_114_B'
    WebServerPath = 'web402'

    def __init__(self, dnsPath='none',webPath='none'):
        self.mode = ''
        self.Key = DNS_SERVER_KEY
        if dnsPath == 'none':
            self.DnsPath = self.DnsServerPath
        else:
            self.DnsPath = dnsPath

        if webPath == 'none':
            self.WebPath = self.WebServerPath
        else:
            self.WebPath = webPath

        self.GeneratedDate = self.getdate()
        self.StorePath = "FetchFiles"
        self.StoreDNSFolderName = "DNSServer%s" % self.GeneratedDate
        self.StoreWebFolderName = "WEBServer%s" % self.GeneratedDate
        self.StoreDNSFilesPath = ('%s\%s' % (self.StorePath, self.StoreDNSFolderName))
        self.StoreWebFilesPath = ('%s\%s' % (self.StorePath, self.StoreWebFolderName))

    #   fetch files from our DNS server - all files or just logs.
    def fetchFromDNS(self,folderName='none', mode = FETCHFILE_OPT.Logs.value):
        Helper.printOnScreenAlways('Fetching DNS files....',MSG_TYPES.YELLOW)
        try:
            if folderName == 'none':
                folderName = self.StoreDNSFilesPath
            dict = os.getcwd() + ("\%s" % folderName) # the dirctory where we store the files
            com = ''
            if mode == FETCHFILE_OPT.All.value:
                com = FETCHFROM_OPT.FromDNS.value
            elif mode == FETCHFILE_OPT.Logs.value:
                com = FETCHFROM_OPT.FromDNSLogs.value
            elif mode == FETCHFILE_OPT.JSON.value:
                com = FETCHFROM_OPT.FromDNSJSON.value

            com = ( com % (self.Key,self.DnsPath,dict))
            os.system(com)
            Helper.printOnScreenAlways('Fetching file is done.',MSG_TYPES.RESULT)
        except Exception as ex:
            print(ex)

    #   fetch files from our Web server - all files or just logs.
    def fetchFromServer(self,folderName='none',mode=FETCHFILE_OPT.Logs.value):
        Helper.printOnScreenAlways('Fetching WEb server files....',MSG_TYPES.YELLOW)
        try:
            if folderName == 'none':
                folderName = self.StoreWebFilesPath
            dict = os.getcwd() + ("\%s" % folderName) # the directory  where we store the files
            com = ''
            if mode == FETCHFILE_OPT.All.value:
                com = FETCHFROM_OPT.FromWebServer.value
            elif mode == FETCHFILE_OPT.JSON.value:
                com = FETCHFROM_OPT.FromWebServerJOSNs.value


            com = (com % (self.Key,self.WebPath,dict))
            os.system(com)
            Helper.printOnScreenAlways('Fetching file is done.', MSG_TYPES.RESULT)
        except Exception as ex:
            print(ex)

    #
    def getdate(self):
        date = datetime.datetime.now()
        date_ = (((str(date)).split('.')[0])).replace(':', '-').replace(' ','_')
        return date_

    #   make the directories in case they are missing
    def makeDirectories(self):
        try:

            if not os.path.exists(self.StorePath):
                os.makedirs(self.StorePath)
                os.makedirs(self.StoreDNSFilesPath)
                os.makedirs(self.StoreWebFilesPath)
            else:
                if not os.path.exists(self.StoreDNSFilesPath):
                    os.makedirs(self.StoreDNSFilesPath)

                if not os.path.exists(self.StoreWebFilesPath):
                    os.makedirs(self.StoreWebFilesPath)

        except Exception as ex:
            print(ex)

    #
    def removeEmptyDirectories(self):
        Folders = [x for x in os.listdir('FetchFiles')]
        for folder in Folders:
            os.rmdir(folder)

    #
    def run(self,argv):
        self.makeDirectories()
        try:
            if len(argv) != 1:
                if argv[1] == '-dns': # DNS Server
                    if argv[2] == '-fetch':
                        if argv.__len__() > 3:
                            if argv[3] == '-all':
                                self.fetchFromDNS(mode=FETCHFILE_OPT.All.value)
                            elif argv[3] == '-logs':
                                self.fetchFromDNS( mode=FETCHFILE_OPT.Logs.value)
                            elif argv[3] == '-json':
                                self.fetchFromDNS(mode=FETCHFILE_OPT.JSON.value)
                            else:
                                self.fetchFromDNS()
                        else:
                            self.fetchFromDNS()  # get all the file by defailt
                elif argv[1] == '-web': # Web Server
                    if argv[2] == '-fetch':
                        if argv[3] == '-all':
                            self.fetchFromServer(mode=FETCHFILE_OPT.All.value)
                        elif argv[3] == '-json':
                            self.fetchFromServer(mode=FETCHFILE_OPT.JSON.value)
                        else:
                            self.fetchFromServer()
                    else:
                        self.fetchFromServer()  # get Log files by defailt
        except Exception as ex:
            print(ex)

if __name__ == '__main__':  # for debugging purpose
    argv= sys.argv
    fetch = FetchFiles()
    fetch.run(['','-dns','-fetch', '-all'])














