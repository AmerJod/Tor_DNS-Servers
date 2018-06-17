import datetime
import functools
import io
import json
import os
import pycurl
import subprocess
import time
from threading import Thread

import certifi
import stem.process
from stem import StreamStatus, process
from stem.util import term

# varebles
#$C42E78EC7BEB5CA0FABD4A6BBDDD67EDD61DFF8D -works
EXIT_FINGERPRINT = 'FDCB34483EED86D3113537ED06BC49130F2C51AE'
SOCKS_PORT = 7000
CONRTROL_PORT = 9051
DOMAIN_URL = ""
CONSUMER_KEY = ""
CONSUMER_SECRET = ""
ACCESS_TOKEN = ""
ACCESS_TOKEN_SECRET = ""
TOR_CONNECTION_TIMEOUT = 20   # timeout before we give up on a circuit
PYCURL_TIMEOUT = 15


OUTPUTFILE= 'result.txt'
NODEPATH = 'ExitNodesJSON.json'
MODE = 'out'

#NODEPATH = 'Info\ExitNodesJSON.json'
#https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=849845;msg=127
#https://stackoverflow.com/questions/29876778/tor-tutorial-speaking-to-russia-stuck-at-45-50
def query(url):
  # Uses pycurl to fetch a site using the proxy on the SOCKS_PORT.
  output = io.BytesIO()
  query = pycurl.Curl()
  query.setopt(pycurl.CAINFO, certifi.where())
  query.setopt(pycurl.URL, url)
  query.setopt(pycurl.TIMEOUT, PYCURL_TIMEOUT)
  query.setopt(pycurl.PROXY, '127.0.0.1')
  query.setopt(pycurl.PROXYPORT, SOCKS_PORT)
  query.setopt(pycurl.IPRESOLVE, pycurl.IPRESOLVE_V4)

  query.setopt(pycurl.PROXYTYPE, pycurl.PROXYTYPE_SOCKS5_HOSTNAME)
  query.setopt(pycurl.WRITEFUNCTION, output.write)
  try:
    query.perform()
    return output.getvalue()
  except pycurl.error as exc:
    return "Unable to reach %s (%s)" % (url, exc)

def stream_event(controller, event):
  if event.status == StreamStatus.SUCCEEDED and event.circ_id:
    circ = controller.get_circuit(event.circ_id)

    exit_fingerprint = circ.path[-1][0]
    exit_relay = controller.get_network_status(exit_fingerprint)

    print("Exit relay for our connection to %s" % (event.target))
    print("  address: %s:%i" % (exit_relay.address, exit_relay.or_port))
    print("  fingerprint: %s" % exit_relay.fingerprint)
    print("  nickname: %s" % exit_relay.nickname)
    print("  locale: %s" % controller.get_info("ip-to-country/%s" % exit_relay.address, 'unknown'))
    print("")


def checkTorConnectionForWindows():
    start_time = time.time()
    nodesCount = 0
    successfully_Connection = 0
    failed_Connections = 0
    cur_path = os.path.dirname(__file__)
    # read all the nodes
    new_path = os.path.relpath(NODEPATH, cur_path)

    with open(new_path) as f:
        jsonObjects = json.load(f)

    result = False
    # print the whole obj
    for obj in jsonObjects:
        ip = str(obj['ExitNode']['Address'].encode("ascii"),'utf-8')
        fingerprint = str(obj['ExitNode']['Fingerprint'].encode("ascii"),'utf-8')
        # https://stackoverflow.com/questions/21827874/timeout-a-python-function-in-windows
        func = timeout(timeout=16)(getTORExitPoint)
        result = func(fingerprint, ip, nodesCount+1)
        try:
            if result is True:
                successfully_Connection += 1
            else:
                failed_Connections += 1
        except:
            failed_Connections += 1

        # total  number of nodes
        nodesCount = nodesCount + 1
        if nodesCount == 20000:
            break

    time_taken = time.time() - start_time

    print("\n--------------------------")
    print('Finished in  %0.2f seconds' % (time_taken))
    print(term.format('Found ' + str(nodesCount) + ' Exit nodes', term.Attr.BOLD))
    print(term.format(str(successfully_Connection) + ': were connected successfully', term.Attr.BOLD))
    print(term.format(str(failed_Connections) + ': Failed/Problem/Not Sure', term.Attr.BOLD))

    print(term.format('Checking Success rate: '+str(successfully_Connection/nodesCount * 100)+'%', term.Color.GREEN))
    print(term.format('Checking Failed rate: '+str(failed_Connections/nodesCount * 100)+'%', term.Color.RED))

def checkTorConnectionForLinux():
    start_time = time.time()
    nodesCount = 0
    successfully_Connections = 0
    successfully_Connections_checking_failed = 0
    failed_Connections = 0

    global MODE
    cur_path = os.path.dirname(__file__)
    # read all the nodes
    new_path = os.path.relpath(NODEPATH, cur_path)

    with open(new_path) as f:
        jsonObjects = json.load(f)

    result = 3 # assume that connection failed

    # print the whole obj
    for obj in jsonObjects:
        ip = str(obj['ExitNode']['Address'].encode("ascii"),'utf-8')
        fingerprint = str(obj['ExitNode']['Fingerprint'].encode("ascii"),'utf-8')
        # https://stackoverflow.com/questions/21827874/timeout-a-python-function-in-windows
        result = getTORExitPoint(fingerprint, ip, nodesCount+1)
        try:
            if result == 1:    # Connection succeed
                successfully_Connections += 1
            elif result == 2:   # Connection succeed , but checking failed.
                successfully_Connections_checking_failed += 1
            elif result == 3:   # Connection failed
                failed_Connections += 1
        #TODO: need to check why we have here
        except:
            failed_Connections += 1

        # total  number of nodes
        nodesCount = nodesCount + 1
        if nodesCount == 20000:
            break

    time_taken = time.time() - start_time

    print("\n--------------------------")
    print('Finished in  %0.2f seconds' % (time_taken))
    print(term.format('Found ' + str(nodesCount) + ' Exit nodes', term.Attr.BOLD))
    print(term.format(str(successfully_Connections) + ': were connected successfully', term.Attr.BOLD))
    print(term.format(str(successfully_Connections_checking_failed) + ': were connected successfully, but checking failed.', term.Attr.BOLD))
    print(term.format(str(failed_Connections) + ': failed ', term.Attr.BOLD))
    print("\n--------------------------")
    print(term.format('Checking Success rate:   '+str(successfully_Connections/nodesCount * 100)+'%', term.Color.GREEN))
    print(term.format('Checking Failed rate:    '+str(successfully_Connections_checking_failed/nodesCount * 100)+'%', term.Color.GREEN))
    print(term.format('Failed Connections rate: '+str(failed_Connections/nodesCount * 100)+'%', term.Color.RED))
    if MODE == 'out':
        data = ''
        with open(OUTPUTFILE,'r') as file:
            data = file.read()
        with open(OUTPUTFILE,'w+') as file:
            file.write(data)
            file.write("\n--------------------------\n")
            file.write("\n--------------------------\n")
            file.write('Finished in  %0.2f seconds\n' % (time_taken))
            file.write('Found ' + str(nodesCount) + ' Exit nodes:\n')
            file.write('   '+str(successfully_Connections) + ': were connected successfully\n')
            file.write('   '+str(successfully_Connections_checking_failed) + ': were connected successfully, but checking failed.\n')
            file.write('   '+str(failed_Connections) + ': failed\n')
            file.write('\n--------------------------\n')
            file.write('Checking Success rate:   '+str(successfully_Connections/nodesCount * 100)+'% \n')
            file.write('Checking Failed rate:    '+str(successfully_Connections_checking_failed/nodesCount * 100)+'% \n')
            file.write('Failed Connections rate: '+str(failed_Connections/nodesCount * 100)+'% \n')


def Processkill(process_name):
    try:
      killed = os.system('taskkill /f /im ' + process_name)
    except Exception as e:
      killed = 0
    return killed

def print_bootstrap_lines(line):
  # print line
  if "Bootstrapped " in line:
    print(term.format(line, term.Color.GREEN))



#TODO: need to be removed
def start(exitFingerprint, ip):
    # Start an instance of Tor configured to only exit through Russia. This prints
    # Tor's bootstrap information as it starts. Note that this likely will not
    # work if you have another Tor instance running.

    # Terminate the tor in case if it is still running
    print(term.format("Starting Tor, connecting to: %s \n", term.Attr.BOLD) % ip)
    tor_process = stem.process.launch_tor_with_config(
      config = {
        'SocksPort': str(SOCKS_PORT),
        'ExitNodes': '$'+EXIT_FINGERPRINT,
        'ControlPort': str(CONRTROL_PORT),
        'DataDirectory' : 'Connection_info',
      },

      #timeout=CONNECTION_TIMEOUT,
      #completion_percent=100,
      #take_ownership=True,
      #init_msg_handler = print_bootstrap_lines,
    )

    print(term.format("\nChecking our endpoint:\n", term.Attr.BOLD))

    #print(term.format(query("https://www.atagar.com/echo.php"), term.Color.BLUE))
    print(term.format(query("https://icanhazip.com"), term.Color.GREEN))
    tor_process.kill()  # stops tor

def timeout(timeout):
    def deco(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            res = [Exception('function [%s] timeout [%s seconds] exceeded!' % (func.__name__, timeout))]

            def newFunc():
                try:
                    res[0] = func(*args, **kwargs)
                except Exception as e:
                    res[0] = e

            t = Thread(target=newFunc)
            t.daemon = True
            try:
                t.start()
                t.join(timeout)
            except Exception as e:
                print('error starting thread')
                raise e
            ret = res[0]
            if isinstance(ret, BaseException):
                return ret
            return ret

        return wrapper
    return deco

def wirteIntoFile(raw):
    if MODE == 'out':
        data = ''
        with open(OUTPUTFILE,'r') as file:
            data = file.read()
        with open(OUTPUTFILE,'w+') as file:
            file.write(data)
            file.write(raw+'\n')

def getTORExitPoint(exitFingerprint, ip,index):
    # Start an instance of Tor configured to only exit through Russia. This prints
    # Tor's bootstrap information as it starts. Note that this likely will not
    # work if you have another Tor instance running.

    # Return values
    # 1 : Connection succussed
    # 2 : Connected but failed to check it
    # 3 : Connection failed

    start_time = time.time()
    result = 3
    print(term.format(" \n%d- Starting Tor, connecting to: %s", term.Attr.BOLD) % (index,ip))
    print('Fingerprint: ' + exitFingerprint)
    wirteIntoFile('\n%d- Starting Tor, connecting to: %s' % (index,ip))
    wirteIntoFile('Fingerprint: ' + exitFingerprint)

    try:
        tor_process = stem.process.launch_tor_with_config(
            timeout=TOR_CONNECTION_TIMEOUT,
            completion_percent=100,
            config={
                'SocksPort': str(SOCKS_PORT),
                'ExitNodes': '$' + exitFingerprint,
                'ControlPort': str(CONRTROL_PORT),
                'DataDirectory': 'Connection_info',
            },
        )
    except:
        print(term.format('Connection failed! - Timed out', term.Color.RED))
        wirteIntoFile('Connection failed! - Timed out')
        return 3

    print(term.format('Connected, Checking...', term.Color.GREEN))
    wirteIntoFile('Connected, Checking...')
    try:
        if ip == str(query("https://icanhazip.com"),'utf-8').rstrip():
            print(term.format('Connected Successfully', term.Color.GREEN))
            wirteIntoFile('Connected Successfully2')
            result = 1
        else:
            print(term.format('Failed Checking', term.Color.RED))
            wirteIntoFile('Failed Checking')
            result = 2

    except:
        tor_process.kill()  # stops tor
        result = 2
        print(term.format('Failed Checking', term.Color.RED))
        wirteIntoFile('Failed Checking')

    tor_process.kill()  # stops tor

    return result

def test():
    func = timeout(timeout=16)(start)
    result = func('9795BA8B2912CB25ECE3CE9B258B5171E622F17C', '197.149.34.201')
    try:
        if result is True:
            print ('S')
        else:
            print ('F')
    except:
        print('E F')

def main():
    # this method is for testing
    # test()
    open(OUTPUTFILE, 'w').close()
    date = datetime.datetime.now()
    date =(((str(date)).split('.')[0]).split(' ')[1] + ' ' + ((str(date)).split('.')[0]).split(' ')[0])
    print("Date %s" % date)

    wirteIntoFile("Date %s" % date)

    if stem.util.system.is_windows():
        # Terminate the tor in case if it is still running
        Processkill('tor.exe')
        checkTorConnectionForWindows()
    else:
        checkTorConnectionForLinux()

if __name__ == '__main__':
    main()




