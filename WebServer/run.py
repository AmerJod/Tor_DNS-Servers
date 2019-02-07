#! /usr/bin/env python3

import sys
import os
from app import app
from stem.util import term

app.debug = True
app.static_folder = 'static'

VERSION = '4.02'
STARTS = False

#
def main(argv):
    try:
        if argv.__len__() > 0:
            if argv[0] == '-s': # on the server
                app.run(host="0.0.0.0",port="80",debug=False, threaded=True)
            else:
                print('Wrong parameters...')
        else:
            app.run()
    except Exception as ex:
        print(ex)
        # run it locally
        print('Running locally... ')
        app.run()

#
def makeDirectories():

    if not os.path.exists('JSON'):
        os.makedirs('JSON/CheckingRequests')
        os.makedirs('JSON/NormalRequests')
    else:
        if not os.path.exists('JSON/CheckingRequests'):
            os.makedirs('JSON/CheckingRequests')
        if not os.path.exists('JSON/NormalRequests'):
            os.makedirs('JSON/NormalRequests')

    if not os.path.exists('Logs'):
        os.makedirs('Logs')

#
def printLogo():
        try:
            with open('Logo/logo.txt', 'r') as f:
                lineArr = f.read()
                print(term.format(str(lineArr),term.Color.GREEN))
            with open('Logo/logo2.txt', 'r') as f:
                lineArr = f.read()
                print(term.format((str(lineArr) % str(VERSION)), term.Color.YELLOW))
        except Exception as ex:
            print('ERROR: printLogo - ' + str(ex))

#
if __name__ == '__main__':
    makeDirectories()
    printLogo()
    main(sys.argv[1:])

