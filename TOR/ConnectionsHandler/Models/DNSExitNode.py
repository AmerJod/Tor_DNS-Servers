
"""
This class is for each exitNode which delong to DNS resolver
"""

class DNSExitNode():
    def __init__(self,nodeIP,nodeDomain,nodeModifiedDomainfull):
        self.exitNodeIP = nodeIP
        self.nodeDomian = nodeDomain
        self.nodeModifiedDomian = nodeModifiedDomainfull
        self.JSON = self.reprExitNodelistJSON()

    def reprExitNodelistJSON(self):
        return dict(nodeIP=self.exitNodeIP, nodeDomian=self.nodeDomian, nodeModifiedDomian= self.nodeModifiedDomian)