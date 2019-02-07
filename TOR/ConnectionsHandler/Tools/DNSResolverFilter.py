

from enum import Enum

from TOR.ConnectionsHandler.Tools.DnsResolver import DNSResolver
from TOR.ConnectionsHandler.Tools import TORNodeFilter
from TOR.Helper.Helper import Helper
from TOR.Helper.Helper import MSG_TYPES



class DNS_CATEGORY(Enum):

    ALL = 'All'
    SUPPORT0X20ENCODING = '0x20'
    DONOTSUPPORT0X20ENCODING = 'NO0x20'

if __name__ == '__main__':

    exitNodeFilter = TORNodeFilter.ExitNodeFilter()
    (listTORConnected,listTORAccessWebsite, listTORREAccessWebsite,
    listTORFullyAccessWebsite, listTORNOTAccessWebsite) = exitNodeFilter.filterExitNode()

    DNSFilter = DNSResolver()
    DNSlist = DNSFilter.Normalize(show='no')
    resolverList = []
    for resolver in DNSlist:
        exitnodeIPList = []

        index =0
        for exitnode in resolver.ExitNodelist:
            exitnodeIPList.append(resolver.ExitNodelist[index].exitNodeIP) # for dns
            index += 1

        for exitnode in listTORREAccessWebsite: # nodes that needed to reconnect
            nodeIP = exitnode['ExitNode']['Address']
            if nodeIP in exitnodeIPList:
                if resolver.DNSIP not in resolverList:
                    resolverList.append(resolver.DNSIP)

    # print Resolvers have implemented 0x20bit encoding
    Helper.printOnScreenAlways('%d Resolvers found that have implemented 0x20bit encoding  '% len(resolverList),MSG_TYPES.RESULT)
    for dns in resolverList:
        Helper.printOnScreenAlways(dns,MSG_TYPES.RESULT)





