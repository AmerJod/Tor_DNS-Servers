#! /usr/bin/env python3

'''
    This file moves file between local PC and DNS Server and Web Server.
'''


import sys
import datetime
import os

def moveToDNS(dic_name='dns'):
    os.system('scp -r -i C:/pem/DNS_MSc_Thesis_amer.pem C:/TOR_PRJ/DNS/TO   ubuntu@34.198.193.29:/home/ubuntu/%s/' % dic_name)

def moveFromDNS(dic_name='dns_back'):
    #
    dict = 'DNSlogs\%s' % dic_name
    os.makedirs(dict)
    dict= os.getcwd() + ("\%s" % dict)
    com = ('scp -r -i  scp -r -i C:/pem/DNS_MSc_Thesis_amer.pem ubuntu@34.198.193.29:/home/ubuntu/dns9/Logs "%s" ' % dict)
    print(com)
    os.system(com)

def moveToWebServer(dic_name='web'):
    os.system('scp -r -i C:/pem/DNS_MSc_Thesis_amer.pem C:/TOR_PRJ/TO/web  ubuntu@52.20.33.59:/home/ubuntu/%s/' % dic_name)

def moveFromServer(dic_name='web_back'):
    os.mkdir('C:/Web/FROM/%s' % dic_name)
    os.system('scp -r -i C:/pem/DNS_MSc_Thesis_amer.pem ubuntu@52.20.33.59:/home/ubuntu/web/  C:/Web/FROM/%s' % dic_name)

def getdate():
        date = datetime.datetime.now()
        date_ = (((str(date)).split('.')[0])).replace(':', '-').replace(' ','_')
        return date_


def makeDirectories():
    '''
        Make the directories in case they are missing.
    '''
    try:
        if not os.path.exists('DNSLogs'):
            os.makedirs('DNSLogs')
        if not os.path.exists('WEBLogs'):
            os.makedirs('WEBLogs')

    except Exception as ex:
        print(ex)

def run(argv):
    makeDirectories()
    date=getdate()
    print('path: ' + str(os.chdir(os.path.dirname(os.path.realpath(__file__)))))
    print('ste:'+ str(os.getcwd()))
    try:
        if len(argv) != 1:
            if argv[1] == '-d': # DNS Server
                if argv[2] == 'to':
                    moveToDNS(date)
                elif argv[2] == 'from':
                    moveFromDNS(date)
            elif argv[1] == '-w': # Web Server
                if argv[2] =='to':
                    moveToWebServer(date)
                elif argv[2] =='from':
                    moveFromServer(date)
        print('DONE :)')

    except Exception as ex:
        print(ex)


if __name__ == '__main__':
    argv= sys.argv
    run(['','-d','from'])













