#! /usr/bin/env python3

import queue
import threading
import dns.resolver

class BirhtdayAttak2(threading.Thread):
    def __init__(self,q,dnsIP,domain,numberOfTries, loop_time = 1.0/60):
        self.q = q
        self.timeout = loop_time
        self.dnsIP = dnsIP
        self.domain = domain
        self.res = dns.resolver.Resolver()
        self.res.nameservers = [self.dnsIP]  # ['149.20.48.31','34.198.193.29','8.8.8.8']
        self.res.lifetime = 20
        self.numberOfTries = numberOfTries
        super(BirhtdayAttak2, self).__init__()

    def onThread(self, function, *args, **kwargs):
        self.q.put((function, args, kwargs))

    def run(self):
        while True:
            try:
                function, args, kwargs = self.q.get(timeout=self.timeout)
                function(*args, **kwargs)

            except queue.Empty:
                self.idle()

    def idle(self):
        pass
        # put the code you would have put in the `run` loop here

    def mountAttackAsycn(self):
        try:
            for i in range(1,self.numberOfTries):
                answers = self.res.query(self.domain, 'a')
                for rdata in answers:
                    print(rdata.address)
        except Exception as ex:
            print(ex)


if __name__ == '__main__':

    birhtdayAttak = BirhtdayAttak2(dnsIP='8.8.8.8',domain='google.com',numberOfTries=10)
    birhtdayAttak.start()
    birhtdayAttak.onThread(birhtdayAttak.mountAttackAsycn())
    birhtdayAttak.onThread(birhtdayAttak.mountAttackAsycn())
