#! /usr/bin/env python3
import datetime
from enum import Enum
from stem.util import term

class MODE_TYPES(Enum):
    printing = '-out'
    none = '-none'

class MSG_TYPES(Enum):
    RESULT = term.Color.GREEN
    ERROR = term.Color.RED
    YELLOW = term.Color.YELLOW
    ANY = term.Color.WHITE

class TIME_FORMAT(Enum):
    FULL = 'full'
    DATE = 'date'
    TIME = 'time'

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
