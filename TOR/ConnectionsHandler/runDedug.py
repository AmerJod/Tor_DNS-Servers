import sys
from TOR.ConnectionsHandler.TORConnector import TORConnections

if __name__ == '__main__':

    con = TORConnections('-c', 'out', 6)
    con.run()
