from twisted.internet import protocol
import re
import time

class PioneerServer(protocol.Protocol):
    def dataReceived(self, data):
        print('From {}: {}'.format(self.transport.getHost(), data))
        if '?P' in data:
             for online in self.factory.local_clients.online:
                 if not online.pwr:
                     online.transport.write(data)
                 else:
                     self.transport.write(online.pwr)
        elif '?V' in data:
             for online in self.factory.local_clients.online:
                 if not online.vol:
                     online.transport.write(data)
                 else:
                     self.transport.write(online.vol)
        elif 'PO' in data:
             for online in self.factory.local_clients.online:
                online.transport.write('?P\r\n')
                time.sleep(1)
                online.transport.write(data)
        else:
            vol = re.search('\d{1,3}VL', data)
            if vol:
                data = data.replace(vol.group(), vol.group().rjust(5, '0'))
                print('From {}: {}'.format(self.transport.getHost(), data))
            for online in self.factory.local_clients.online:
                online.transport.write(data)

    def connectionMade(self):
        self.factory.online.append(self)
#        print('Connected {}'.format(self.transport.getHost()))

    def connectionLost(self, reason):
        self.factory.online.remove(self)

class PioneerServerFactory(protocol.ServerFactory):
    protocol = PioneerServer

    def __init__(self):
        self.online = []
        self.local_server = []
