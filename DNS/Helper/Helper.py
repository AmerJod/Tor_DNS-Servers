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

class TIME_FORMAT(Enum):
    FULL = 'full'
    DATE = 'date'
    TIME = 'time'

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
        date = Helper.getTime(TIME_FORMAT.DATE)
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

    def loggingError(error):
        logging.error(str(error))

    def loggingError(functName, error):
        logging.error(str("%s: %s" % (functName,error)))

    def getTime(format=TIME_FORMAT.FULL):
        date = datetime.datetime.now()
        try:
            if format == TIME_FORMAT.FULL:  # full
                return (((str(date)).split('.')[0]).split(' ')[1] + ' ' + ((str(date)).split('.')[0]).split(' ')[0])
            if format == TIME_FORMAT.DATE:  # date
                return (((str(date)).split('.')[0]).split(' ')[0])
            if format == TIME_FORMAT.TIME:  # time
                return (((str(date)).split('.')[0]).split(' ')[1])
        except Exception as ex:
            print('Helper - getTime: %s' % ex)


class LogData():
    def __init__(self, filename, mode='none'):
        date = Helper.getTime(TIME_FORMAT.DATE)
        fullDate = Helper.getTime(TIME_FORMAT.FULL)
        self.mode = mode

        # TODO: need refactoring - make it more abstract
        self.file = 'Logs/' + filename + '_' + date + '_counter+.txt'
        if (os.path.exists(self.file)) != True:
            with open(self.file, 'w+') as file:
                file.write('Start - ' + fullDate + '\n')

    def wirteIntoFile(self, raw):
        if self.mode == 'out':
            data = ''
            #raw = str(Helper.getTime(TIME_FORMAT.TIME)) + ': ' + raw
            with open(self.file, 'r') as file:
                data = file.read()
            with open(self.file, 'w+') as file:
                file.write(data)
                file.write(raw + '\n')

    def counter(self):
        pass

