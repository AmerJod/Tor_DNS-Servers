#! /usr/bin/env python3
import datetime
import io
import os
from enum import Enum
from stem.util import term

import logging
ERRORS_LOG_PATH = 'Logs/Errors/'

# class LOGGING_LEVEL(Enum):
#     logging.CRITICAL = 50
#     logging.ERROR    = 40
#     logging.WARNING  = 30
#     logging.INFO     = 20
#     logging.DEBUG    = 10
#     logging.NOTSET   = 0

class MODE_TYPES(Enum):
    printing = '-out'
    none = '-none'

class MSG_TYPES(Enum):
    RESULT = term.Color.GREEN
    ERROR = term.Color.RED
    YELLOW = term.Color.YELLOW
    ANY = term.Color.WHITE

class Helper:

    def __init__(self,mode='-none'):
        self.mode = ''

    #@staticmethod
    def printOnScreen(msg,color=MSG_TYPES.ANY,mode='-none'):
        if mode == '-out':
            print(term.format(msg,color.value))
        # @staticmethod

    def printOnScreenAlways(msg, color=MSG_TYPES.ANY):
        try:
            print(term.format(msg, color.value))
        except:
            print(msg) # could be like this

    def initLogger(level,enableConsole=False):
        date = Helper.getTime(2)
        file = ("%sE-%s.log" % (ERRORS_LOG_PATH, date))
        # set up logging to file - see previous section for more details
        logging.basicConfig(level=int(level),
                            format='%(asctime)-s %(name)-8s %(levelname)-8s %(message)s',
                            datefmt='%Y-%m-%d %H:%M',
                            filename=file
                            )
        # define a Handler which writes INFO messages or higher to the sys.stderr
        console = logging.StreamHandler(stream=None)
        console.setLevel(level)

        # set a format which is simpler for console use
        formatter = logging.Formatter('%(asctime)-s %(name)-12s: %(levelname)-8s %(message)s')
        # tell the handler to use this format
        console.setFormatter(formatter)
        if enableConsole is True:
            # add the handler to the root logger
            logger = logging.getLogger('').addHandler(console)

    def loggingError(fuctName, error):
        logging.error(str(error))

    def getTime(opt=1):
        date = datetime.datetime.now()
        if opt == 1:  # full
            return (((str(date)).split('.')[0]).split(' ')[1] + ' ' + ((str(date)).split('.')[0]).split(' ')[0])
        if opt == 2:  # date
            return (((str(date)).split('.')[0]).split(' ')[0])
        if opt == 3:  # time
            return (((str(date)).split('.')[0]).split(' ')[1])

class LogData():
    def __init__(self, filename, mode='none'):
        date = Helper.getTime(2)
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
            raw = str(Helper.getTime(3)) + ': ' + raw
            with open(self.file, 'r') as file:
                data = file.read()
            with open(self.file, 'w+') as file:
                file.write(data)
                file.write(raw + '\n')

    def counter(self):
        pass

