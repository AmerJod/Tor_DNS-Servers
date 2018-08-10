


import json
'''
Exit node class ....
'''

class ExitNode:

    def __init__(self,ipaddress,fingerprint,nickname,or_port,dir_port,status):
        self.ipaddress = ipaddress
        self.fingerprint = fingerprint
        self.nickname = nickname
        self.or_port = or_port
        self.dir_port = dir_port
        self.status = status

    def reprJSON(self):
        return dict(IpAddress =self.ipaddress,Fingerprint=self.fingerprint,Nickname= self.nickname,
                        Dir_port= self.or_port,
                        Or_port= self.dir_port,
                        Status =self.status)



    #def toJSON(self):







