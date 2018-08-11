'''
This to gather all the files and put them together in one folder
'''

import os
import shutil
import sys

from TOR.Helper.Helper import Helper
from TOR.Helper.Helper import MSG_TYPES

class MoveFiles():
    def __init__(self, dnsPath='none', webPath='none'):
        self.mode = ''
        self.SOURCE_PATH = 'FetchFiles'
        self.DESTINATION_PATH = 'GatheredFiles/'

    def findAllDNSFiles(self, folder: object = 'Logs') -> object:
        RootPath = '\\'.join(os.path.dirname(os.path.abspath(__file__)).split('\\')[:-1])
        newDestinationPath = os.path.join(RootPath, self.DESTINATION_PATH)

        # find all the logs folders for DNS
        files = [os.path.join(dp, f) for dp, dn, fn in os.walk(os.path.expanduser(self.SOURCE_PATH)) for f in fn]

        if folder =='Logs':
            newDestinationPath = os.path.join(newDestinationPath, "Logs")
            # find all the logs files for DNS
            filteredLogFiles = [filePath for filePath in files if
                                "logs" in filePath.lower() and "error" not in filePath.lower() and "DNS" in filePath]
        elif folder == 'JSON': # TODO: need some more work
            newDestinationPath = os.path.join(newDestinationPath, "JSON")
            # find all the logs files for DNS
            filteredLogFiles = [filePath for filePath in files if
                                "JSON" in filePath.lower() and "error" not in filePath.lower() and "DNS" in filePath and "Checking" in filePath]

        count = 0
        for filePath in filteredLogFiles:
            try:
                shutil.move(filePath, newDestinationPath)
                count += 1
            except shutil.Error as e:
                pass
                # os.rename(filePath, ('v%s _' % index) + filePath)
                # shutil.move(filePath, newDestinationPath)
        Helper.printOnScreenAlways('%d files has been moved.' % count, MSG_TYPES.RESULT)

    def findAllWebFiles(self, folder='Logs'):
        RootPath = '\\'.join(os.path.dirname(os.path.abspath(__file__)).split('\\')[:-1])
        newDestinationPath = os.path.join(RootPath, self.DESTINATION_PATH)

        # find all the logs folders for DNS
        files = [os.path.join(dp, f) for dp, dn, fn in os.walk(os.path.expanduser(self.SOURCE_PATH)) for f in fn]

        if folder == 'Logs':
            newDestinationPath = os.path.join(newDestinationPath, "Logs")
            # find all the logs files for DNS
            filteredLogFiles = [filePath for filePath in files if
                                "logs" in filePath.lower() and "error" not in filePath.lower() and "WEB" in filePath]
        elif folder == 'JSON':  # TODO: need some more work
            newDestinationPath = os.path.join(newDestinationPath, "JSON")
            # find all the logs files for DNS
            filteredLogFiles = [filePath for filePath in files if
                                "JSON" in filePath.lower() and "DNS" in filePath and "Checking" in filePath]

        count = 0
        for filePath in filteredLogFiles:
            try:
                shutil.move(filePath, newDestinationPath)
                count += 1
            except shutil.Error as e:
                pass
                # os.rename(filePath, ('v%s _' % index) + filePath)
                # shutil.move(filePath, newDestinationPath)
        Helper.printOnScreenAlways('%d files has been moved.' % count, MSG_TYPES.RESULT)
if __name__ == '__main__':  # for debugging purpose
    #argv= sys.argv
    movefiles = MoveFiles()
    movefiles.findAllDNSFiles(folder='Logs') #folder='JSON'
    #fetch = FetchFiles()
    #fetch.run(['','-dns','-fetch', '-logs'])



