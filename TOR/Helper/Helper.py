#! /usr/bin/env python3


import json
from enum import Enum
from stem.util import term


import pickle


class TASK_MODE(Enum):
    REQUEST_DOMAIN = '-r'
    TOR_CONNECTION_CHECKING = '-d'
    DNS_0x20_CHECKING = '-cd'  # Capitalization

class MODE_TYPES(Enum):
    printing = '-out'
    none = '-none'

class MSG_TYPES(Enum):
    RESULT = term.Color.GREEN
    ERROR = term.Color.RED
    YELLOW = term.Color.YELLOW
    ANY = term.Color.WHITE

class ComplexEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj,'reprJSON'):
            return obj.reprJSON()
        else:
            return json.JSONEncoder.default(self, obj)

class EnumEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Enum):
            return obj.name
        return json.JSONEncoder.default(self, obj)


    '''
    def as_enum(d):
        if "__enum__" in d:
            name, member = d["__enum__"].split(".")
            return getattr(PUBLIC_ENUMS[name], member)
        else:
            return d
            
    def default(self, obj,enum):
    if type(obj) in enum.values():
        return {enum.name: str(obj)}
    return json.JSONEncoder.default(self, obj)
    
    def default(self, obj):
        if isinstance(obj, Enum):
            return obj.name
        return json.JSONEncoder.default(self, obj)
        
    '''

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


    def storeExitNodesJSON(objects,path):
        try:
            exitNodes = []
            for exitNode in objects:
                  exitNodes.append({
                            'ExitNode': {
                                'Address': exitNode.ipaddress,
                                'Fingerprint': exitNode.fingerprint,
                                'Nickname': exitNode.nickname,
                                'Dir_port': exitNode.or_port,
                                'Or_port' : exitNode.dir_port,
                                'Status'  : exitNode.status.reprJSON()
                            }
                        })
            with open(path, 'w+') as outfile:
                json.dump(exitNodes, outfile)
        except Exception as ex:
            print(ex)

    def storeJSONMethod2(objects,path):
        try:
            # with open(path, "wb") as f:

            #    pickle.dump(objects, f)

            exitNodes = []
            for exitNode in objects:
                #js# =
                #js = json.dumps(exitNode.reprJSON(), sort_keys=True, indent=4,cls=ComplexEncoder)
                exitNodes.append(json.loads(exitNode.reprJSON(), cls=ComplexEncoder))
               # exitNodes.append(json.dumps(exitNode.reprJSON(), cls=ComplexEncoder))

            with open(path, 'w+') as outfile:
                json.dumps(exitNodes, outfile)

        except Exception as ex:
            print(ex)

