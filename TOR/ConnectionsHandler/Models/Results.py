
import json
from enum import Enum
from TOR.Helper.Helper  import Helper
from TOR.Helper.Helper  import MSG_TYPES
from TOR.Helper.Helper  import MODE_TYPES
from TOR.Helper.Helper  import EnumEncoder



# We could marge them on one Enum
class CONNECTION_STATUS(Enum):
    CONNECTED = True
    NOT_CONNECTED = False


class DOMAIN_STATUS(Enum):
    STATELESS = 'Stateless'
    ACCESSIBLE = 'Accessible'
    RE_ACCESSIBLE = 'Re_Accessible'
    NOT_ACCESSIBLE = 'NotAccessible'



class Result:
    #
    def __init__(self,connectionStatus, requestingDomainStatus):
        self.connectionStatus = connectionStatus.value
        self.requestingDomainStatus = requestingDomainStatus.value

    #
    def reprJSON(self):
        return dict(ConnectionStatus=self.connectionStatus, RequestingDomainStatus=self.requestingDomainStatus)


class FinalResult:
    #
    def __init__(self,resultList,nodesCount,timetaken):
        self.resultList = resultList
        self.timetaken = timetaken
        self.nodesCount = nodesCount

    #
    def printCheckedResult(self):
        '''
            This function print the result of checking if the DNS support 0x20 bit encoding(Capitalization)
        '''
        connectionFailed =0
        connectionSucceeded=0
        connectedAndAccessible = 0
        connectedAndReAccessible =0
        connectedButNotAccessible =0
        connectedFailed =0

        print("\n--------------------------")
        Helper.printOnScreenAlways('Finished in  %0.2f seconds' % (self.timetaken))

        Helper.printOnScreenAlways('Found ' + str(self.nodesCount) + ' Exit nodes', MSG_TYPES.RESULT)
        for result in self.resultList:
            if result.connectionStatus == CONNECTION_STATUS.CONNECTED.value:
                if result.requestingDomainStatus == DOMAIN_STATUS.ACCESSIBLE.value:
                    connectedAndAccessible += 1
                elif result.requestingDomainStatus == DOMAIN_STATUS.RE_ACCESSIBLE.value:
                    connectedAndReAccessible += 1
                elif result.requestingDomainStatus == DOMAIN_STATUS.NOT_ACCESSIBLE.value:
                    connectedButNotAccessible += 1
                connectionSucceeded += 1
            if result.connectionStatus == CONNECTION_STATUS.NOT_CONNECTED.value:
                    connectedFailed += 1

        Helper.printOnScreenAlways(str(connectionSucceeded) + ': were connected successfully',MSG_TYPES.RESULT)
        Helper.printOnScreenAlways('   ' +str(connectedAndAccessible) + ': were connected and checked successfully.',MSG_TYPES.RESULT)
        Helper.printOnScreenAlways('   ' +str(connectedAndReAccessible) + ': were connected and re-checked successfully.',MSG_TYPES.RESULT)
        Helper.printOnScreenAlways('   ' +str(connectedButNotAccessible) + ': were connected successfully but checked failed.',MSG_TYPES.RESULT)
        Helper.printOnScreenAlways(str(connectionFailed) + ': failed ', MSG_TYPES.RESULT)
        Helper.printOnScreenAlways("\n--------------------------")

        Helper.printOnScreenAlways('Checking Success rate:   ' + str(connectionSucceeded / self.nodesCount * 100) + '%',MSG_TYPES.RESULT)
        Helper.printOnScreenAlways('Checking Failed rate:    ' + str(connectedButNotAccessible / self.nodesCount * 100) + '%',MSG_TYPES.RESULT)
        Helper.printOnScreenAlways('Failed Connections rate: ' + str(connectionFailed / self.nodesCount * 100) + '%',MSG_TYPES.RESULT)
        Helper.printOnScreenAlways('\n***********************************================END===============***********************************\n',MSG_TYPES.RESULT)


    #
    def writeCheckedResult(self):
        connectionFailed = 0
        connectionSucceeded = 0
        connectedAndAccessible = 0
        connectedAndReAccessible = 0
        connectedButNotAccessible = 0
        connectedFailed = 0

        print("\n--------------------------")
        Helper.printOnScreenAlways('Finished in  %0.2f seconds' % (self.timetaken))

        Helper.printOnScreenAlways('Found ' + str(self.nodesCount) + ' Exit nodes', MSG_TYPES.RESULT)
        for result in self.resultList:
            if result.connectionStatus == CONNECTION_STATUS.CONNECTED.value:
                if result.requestingDomainStatus == DOMAIN_STATUS.ACCESSIBLE.value:
                    connectedAndAccessible += 1
                elif result.requestingDomainStatus == DOMAIN_STATUS.RE_ACCESSIBLE.value:
                    connectedAndReAccessible += 1
                elif result.requestingDomainStatus == DOMAIN_STATUS.NOT_ACCESSIBLE.value:
                    connectedButNotAccessible += 1
                connectionSucceeded += 1
            if result.connectionStatus == CONNECTION_STATUS.NOT_CONNECTED.value:
                connectedFailed += 1

        data = ''
        with open(self.OUTPUT_FILE, 'r') as file:
            data = file.read()
        with open(self.OUTPUT_FILE, 'w+') as file:
            file.write(data)
            file.write("\n--------------------------\n")
            file.write("\n--------------------------\n")
            file.write('Finished in  %0.2f seconds\n' % (self.time_taken))
            file.write('Found ' + str(self.nodesCount) + ' Exit nodes:\n')
            file.write('   ' + str(connectionSucceeded) + ': were connected successfully\n')

            file.write('   ' + str(connectionSucceeded) + ': were connected successfully')
            file.write('   ' + str(connectedAndAccessible) + ': were connected and checked successfully.')
            file.write('   ' + str(connectedAndReAccessible) + ': were connected and re-checked successfully.')
            file.write('   ' + str(connectedButNotAccessible) + ': were connected successfully but checked failed.')
            file.write('   ' + str(connectionFailed) + ': failed ')

            file.write('\n--------------------------\n')
            file.write('Checking Success rate:   ' + str(connectionSucceeded / self.nodesCount * 100) + '%')
            file.write('Checking Failed rate:    ' + str(connectedButNotAccessible / self.nodesCount * 100) + '%')
            file.write('Failed Connections rate: ' + str(connectionFailed / self.nodesCount * 100) + '%')
            file.write('\n***********************************================END===============***********************************\n')


