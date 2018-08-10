'''

This file contains functions to DNS server to complete its tasks.

'''


import os
import logging
import datetime

import  sys, traceback


ERRORS_LOG_PATH = 'Logs/Errors/'

DEBUG = False
COUNTER = 0

#<editor-fold desc="******************* General Tools *******************">
def ProcesskillForWindows(process_name):
    try:
        killed = os.system('taskkill /f /im ' + process_name)
    except Exception as e:
        killed = 0
    return killed

class LogData():
    def __init__(self, filename, mode='none'):
        date = getTime(2)
        self.mode = mode
        '''
        self.file = 'Logs/'+filename+'_'+date+'.log'     # This is hard coded but you could make dynamic

        if (os.path.exists(self.file)) != True:
            with open(self.file, 'w+') as file:
                file.write('Start - '+date +'\n')
        '''
        # TODO: need refactoring - make it more abstract
        self.file = 'Logs/' + filename + '_' + date + '_counter+.txt'
        if (os.path.exists(self.file)) != True:
            with open(self.file, 'w+') as file:
                file.write('Start - ' + date + '\n')

    def wirteIntoFile(self, raw):
        if self.mode == 'out':
            data = ''
            raw = str(getTime(3)) + ': ' + raw
            with open(self.file, 'r') as file:
                data = file.read()
            with open(self.file, 'w+') as file:
                file.write(data)
                file.write(raw + '\n')

    def counter(self):
        pass

def initLogger():
    date = getTime(2)
    file = ("%sE-%s.log" % (ERRORS_LOG_PATH,date) )
    # set up logging to file - see previous section for more details
    logging.basicConfig(level=logging.ERROR,
                        format='%(asctime)-s %(name)-8s %(levelname)-8s %(message)s',
                        datefmt='%Y-%m-%d %H:%M',
                        filename=file,
                        filemode='w')
    # define a Handler which writes INFO messages or higher to the sys.stderr
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    # set a format which is simpler for console use
    formatter = logging.Formatter('%(asctime)-s %(name)-12s: %(levelname)-8s %(message)s')
    # tell the handler to use this format
    console.setFormatter(formatter)
    # add the handler to the root logger
    logging.getLogger('').addHandler(console)

def loggingError(fuctName,error):
    logging.error('DNSFunction - storeDNSRequestJSON - JSON invalid : %s' % str(error))

def getTime(opt = 1):
    date = datetime.datetime.now()
    if opt == 1:    # full
        return (((str(date)).split('.')[0]).split(' ')[1] + ' ' + ((str(date)).split('.')[0]).split(' ')[0])
    if opt == 2:    # date
        return (((str(date)).split('.')[0]).split(' ')[0])
    if opt == 3:    # time
        return (((str(date)).split('.')[0]).split(' ')[1])

def loggingData(value):
    file = LogData(filename='incoming_request', mode='out')
    file.wirteIntoFile(value)


# </editor-fold>

#<editor-fold desc="******************* Zone File *******************">

# </editor-fold>
