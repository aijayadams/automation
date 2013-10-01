from twisted.internet import protocol
import re
import time

class PioneerTelnetServer(protocol.Protocol):
    def dataReceived(self, data):
        print('From {}: {}'.format(self.transport.getHost(), data.strip('\n\r')))
        if '?P' in data:
             for online in self.factory.local_clients.online:
                 if not online.pwr:
                     online.send_command(data)
                 else:
                     self.transport.write(online.pwr)
        elif '?V' in data:
             for online in self.factory.local_clients.online:
                 if not online.vol:
                     online.send_command(data)
                 else:
                     self.transport.write(online.vol)
        elif '?M' in data:
            for online in self.factory.local_clients.online:
                if not online.mut:
                    online.send_command(data)
                else:
                    self.transport.write(online.mut)
        else:
            vol = re.search('\d{1,3}VL', data)
            if vol:
                data = data.replace(vol.group(), vol.group().rjust(5, '0'))
                print('From {}: {}'.format(self.transport.getHost(), data))
            for online in self.factory.local_clients.online:
                online.send_command(data)

    def connectionMade(self):
        self.factory.online.append(self)

    def connectionLost(self, reason):
        self.factory.online.remove(self)

class PioneerTelnetServerFactory(protocol.ServerFactory):
    protocol = PioneerTelnetServer

    def __init__(self):
        self.online = []
        self.local_server = []

class SamsungTelnetServer(protocol.Protocol):
    def dataReceived(self, data):
        print('From {}: {}'.format(self.transport.getHost(), data.strip('\r\n')))
        for online in self.factory.local_clients.online:
            online.send_command(data)

    def connectionMade(self):
        self.factory.online.append(self)

    def connectionLost(self, reason):
        self.factory.online.remove(self)

class SamsungTelnetServerFactory(protocol.ServerFactory):
    protocol = SamsungTelnetServer

    def __init__(self):
        self.online = []
        self.local_server = []
