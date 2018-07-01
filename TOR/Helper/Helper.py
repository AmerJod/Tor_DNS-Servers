from enum import Enum
from stem.util import term




class MODE_TYPES(Enum):
    print = '-out'
    none = '-none'

class MSG_TYPES(Enum):
    RESULT = term.Color.GREEN
    ERROR = term.Color.RED
    YELLOW = term.Color.YELLOW

class Helper:

    def __init__(self,mode='-none'):
        self.mode = ''

    #@staticmethod
    def printOnScreen(msg,color=term.Color.WHITE,mode='-none'):
        if mode == '-out':
            print(term.format(msg,color))
        # @staticmethod

    def printOnScreenAlways(msg, color=term.Color.WHITE):
       print(term.format(msg, color))