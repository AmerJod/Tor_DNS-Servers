#! /usr/bin/env python3
'''
To move the DNS files to DNS server.
You MUST have the KEY stored on your PC
'''

import sys
import datetime
import os
from enum import Enum

DNS_SERVERIP = '34.198.193.29'
DNS_SERVER_PATH = 'dns_0998_Betav5'
KEY_PATH = 'C:/pem/DNS_MSc_Thesis_amer.pem'

class TransferFiles:
    def __init__(self):
        self.mode = ''
        self.Key = KEY_PATH


    def TransferToDNS(self,folderName='none'):
        try:
            RootPath = '\\'.join(os.path.dirname(os.path.abspath(__file__)).split('\\')[:-1])
            com = 'scp -r -i %s "%s" ubuntu@%s:/home/ubuntu/%s/'
            if folderName == 'none':
                folderName = self.StoreDNSFilesPath

            com = (com % (self.Key, RootPath,DNS_SERVERIP,folderName ))
            os.system(com)
        except Exception as ex:
            print(ex)



    def getdate(self):

            date = datetime.datetime.now()
            # date = (((str(date)).split('.')[0]).split(' ')[1] + ' ' + ((str(date)).split('.')[0]).split(' ')[0])
            # date =(((str(date)).split('.')[0]) + '_' + ((str(date)).split('.')[0]).split(' ')[0]).replace(':', '-')
            date_ = (((str(date)).split('.')[0])).replace(':', '-').replace(' ','_')
            return date_



    def run(self,argv):

        print('path: ' + str(os.chdir(os.path.dirname(os.path.realpath(__file__)))))
        try:
            if len(argv) != 1:
                if argv[1] == '-move': # DNS Server
                    if argv.__len__() > 3:
                        if argv[2] == '-n':
                            self.TransferToDNS(folderName=argv[3])
                            print('Transfering file is done')
                    else:
                        print('Missing parameters. Folder Name?! ')

        except Exception as ex:
            print(ex)


if __name__ == '__main__':
    argv= sys.argv
    #run(argv)
    transfer =TransferFiles()
    try:
        if argv.__len__() > 1:
            transfer.run(argv)
        else:
            transfer.run(['', '-move', '-n', DNS_SERVER_PATH])

    except Exception as ex:
        print(ex)













