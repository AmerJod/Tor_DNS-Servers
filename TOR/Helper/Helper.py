#! /usr/bin/env python3


import json
from enum import Enum
from stem.util import term

#
class TASK_MODE(Enum):
    REQUEST_DOMAIN = '-r'
    TOR_CONNECTION_CHECKING = '-d'
    DNS_0x20_CHECKING = '-cd'  # Capitalization
    DNS_RESOLVER_COUNTER = '-drc'  #

#
class MODE_TYPES(Enum):
    printing = '-out'
    none = '-none'

#
class MSG_TYPES(Enum):
    RESULT = term.Color.GREEN
    ERROR = term.Color.RED
    YELLOW = term.Color.YELLOW
    ANY = term.Color.WHITE

#
class ComplexEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj,'reprJSON'):
            return obj.reprJSON()
        else:
            return json.JSONEncoder.default(self, obj)

#
class EnumEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Enum):
            return obj.name
        return json.JSONEncoder.default(self, obj)

#
class Helper:

    #
    def __init__(self,mode='-none'):
        self.mode = ''

    #
    def printOnScreen(msg,color=MSG_TYPES.ANY,mode='-none'):
        if mode == '-out':
            print(term.format(msg,color.value))

    #
    def printOnScreenAlways(msg, color=MSG_TYPES.ANY):
        try:
            print(term.format(msg, color.value))

        except:
            print(msg) # could be like this

    #
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

    def storeDNSResolverData(objects,path):
        try:
            DNSNodes = []
            for DNSNode in objects:
                DNSNodes.append({
                            'DNSResolver': {
                                'DNSIP': DNSNode.DNSIP,
                                'nodeCount': DNSNode.nodeCount,
                                'ExitNodeList' : DNSNode.ExitNodelistJSON
                            }
                        })
            with open(path, 'w+') as outfile:
                json.dump(DNSNodes, outfile)
            Helper.printOnScreenAlways("\n*******************************************\n"
                                       "DNS Resolver Servers information has saved.\n"
                                       "*******************************************",MSG_TYPES.RESULT)

        except Exception as ex:
            Helper.printOnScreenAlways("Something went wrong.",MSG_TYPES.ERROR)
            print(ex)


    def storeJSONMethod2(objects,path):
        try:
            exitNodes = []
            for exitNode in objects:
                exitNodes.append(json.loads(exitNode.reprJSON(), cls=ComplexEncoder))
            with open(path, 'w+') as outfile:
                json.dumps(exitNodes, outfile)

        except Exception as ex:
            print(ex)

