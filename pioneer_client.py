from twisted.internet import protocol
import re

class PioneerClient(protocol.Protocol):
    def __init__(self):
        self.pwr = None
        self.vol = None

    def connectionMade(self):
        self.factory.online.append(self)

    def dataReceived(self, data):
        print('From AVR: {}'.format(data.strip('\n')))
        self.setStatus(data)
        for online in self.factory.local_server.online:
            online.transport.write(data)

    def setStatus(self, data):
        vol = re.search('VOL\d{3}', data)
        if vol:
            self.vol = vol.group()
        pwr = re.search('PWR\d', data)
        if pwr:
            self.pwr = pwr.group()
            if pwr == 'PWR1':
                self.vol = 'VOL000'
            else:
                self.transport.write('?V')

    def connectionLost(self, reason):
        print('Connection lost: {}'.format(reason))
        self.factory.online.remove(self)

class PioneerClientFactory(protocol.ReconnectingClientFactory):
    def __init__(self):
        self.online = []
        self.local_clients = []

    def startedConnecting(self, connector):
        print('Starting connection: {}'.format(connector))

    def buildProtocol(self, addr):
        print('Connected to {}'.format(addr))
        p = PioneerClient()
        p.factory = self
        self.resetDelay()
        return p

    def clientConnectionLost(self, connector, reason):
        print('Lost connection to {}: {}'.format(connector, reason))
        protocol.ReconnectingClientFactory.clientConnectionFailed(self, connector, reason)
