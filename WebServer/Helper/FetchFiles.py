#! /usr/bin/env python3

'''
    this file is to move and fetch files from and to servers(DNS/WebServer)
     you have to have the KEY
'''

import sys
import datetime
import os

from enum import Enum

#
class FETCH_OPT(Enum):
    ToDNS = 'scp -r -i %s %s  ubuntu@34.198.193.29:/home/ubuntu/%s/'
    FromDNSLogs = 'scp -r -i scp -r -i %s ubuntu@34.198.193.29:/home/ubuntu/%s/Logs "%s" '
    ToWebServer = ""
    FromWebServerLogs = ""

#
class FetchFile:
    oDnsPath = 'dns_0994Test'
    def __init__(self, dnsPath='none',webPath='none'):
        self.mode = ''
        self.Key = "C:/pem/DNS_MSc_Thesis_amer.pem"
        if dnsPath == 'none':
            self.DnsPath = self.oDnsPath
        else:
            self.DnsPath = dnsPath

        self.StorePath = "FetchFiles"
        self.StoreDNSFolderName = "DNSLogs"
        self.StoreWebFolderName = "WEBLogs"
        self.StoreDNSFilesPath = ('%s\%s' % (self.StorePath, self.StoreDNSFolderName))
        self.StoreWEbFilesPath = ('%s\%s' % (self.StorePath, self.StoreWebFolderName))
        self.WebPath = webPath

    #
    def moveFromDNS(self, dnsPath ,folderName='none'):
        try:
            if folderName == 'none':
                folderName = self.StoreDNSFilesPath
            dict= os.getcwd() + ("\%s" % folderName) # the dirctory where we store the files
            com = ( FETCH_OPT.FromDNSLogs.value % (self.Key,self.DnsPath,dict))
            os.system(com)
            print('Moving file is done.')

        except Exception as ex:
            print(ex)

    #
    def moveToDNS(self, dnsPath , folderName='none'):
        try:
            if folderName == 'none':
                folderName = self.StoreDNSFilesPath
            dict= os.getcwd() + ("\%s" % folderName) # the dirctory where we store the files
            com = (FETCH_OPT.ToDNS.value % (self.Key,dict,self.DnsPath))
            os.system(com)
            print('Fetching file is done.')
        except Exception as ex:
            print(ex)

    #
    def moveToWebServer(self, folderName='web'):
        os.system('scp -r -i C:/pem/DNS_MSc_Thesis_amer.pem C:/TOR_PRJ/TO/web  ubuntu@52.20.33.59:/home/ubuntu/%s/' % folderName)

    #
    def getdate(self):
            date = datetime.datetime.now()
            date_ = (((str(date)).split('.')[0])).replace(':', '-').replace(' ','_')
            return date_

    #
    def makeDirectories(self):
        '''
            Make the directories in case they are missing
        '''
        try:

            if not os.path.exists(self.StorePath):
                os.makedirs(self.StorePath)
                os.makedirs(self.StoreDNSFilesPath)
                os.makedirs(self.StoreWEbFilesPath)
            else:
                if not os.path.exists(self.StoreDNSFilesPath):
                    os.makedirs(self.StoreDNSFilesPath)

                if not os.path.exists(self.StoreWEbFilesPath):
                    os.makedirs(self.StoreWEbFilesPath)

        except Exception as ex:
            print(ex)


    #
    def run(self,argv):
        self.makeDirectories()
        date=self.getdate()
        print('path: ' + str(os.chdir(os.path.dirname(os.path.realpath(__file__)))))
        print('ste:'+ str(os.getcwd()))
        try:
            if len(argv) != 1:
                if argv[1] == '-d': # DNS Server
                    if argv[2] == 'to':
                        self.moveToDNS(date)
                    elif argv[2] == 'from':
                        self.moveFromDNS(date)
                elif argv[1] == '-w': # Web Server
                    if argv[2] =='to':
                        self.moveToWebServer(date)
                    elif argv[2] =='from':
                        self.moveFromServer(date)
            print('DONE :)')

        except Exception as ex:
            print(ex)


if __name__ == '__main__':
    argv= sys.argv
    fetch =FetchFile()
    fetch.run(['','-d','to'])













