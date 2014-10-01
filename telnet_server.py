from twisted.internet import protocol
from rpc3 import rpc3

import re
import time


class PioneerTelnetServer(protocol.Protocol):
    def dataReceived(self, data):
        if '?P' in data:
             for online in self.factory.local_clients.online:
                 if online.pwr:
                     self.transport.write(online.pwr)
             return
        elif '?V' in data:
             for online in self.factory.local_clients.online:
                 if online.vol:
                     self.transport.write(online.vol)
             return
        elif '?M' in data:
            for online in self.factory.local_clients.online:
                if online.mut:
                    self.transport.write(online.mut)
            return
        elif '?FRONTPANEL' in data:
            for online in self.factory.local_clients.online:
                self.transport.write(online.panel)
            return
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


class MarantzTelnetServer(protocol.Protocol):
    def dataReceived(self, data):
        if 'PW?' in data:
             for online in self.factory.local_clients.online:
                 if online.pwr:
                     self.transport.write(online.pwr)
             return
        elif 'MV?' in data:
             for online in self.factory.local_clients.online:
                 if online.vol:
                     self.transport.write(online.vol)
             return
        elif 'MU?' in data:
            for online in self.factory.local_clients.online:
                if online.mut:
                    self.transport.write(online.mut)
            return
        elif '?FRONTPANEL' in data:
            for online in self.factory.local_clients.online:
                self.transport.write(online.panel)
            return
        vol = re.search('MV\d{1,2}', data)
        if vol:
            data = data.replace(vol.group(), vol.group().rjust(4, '0'))
        print('From {}: {}'.format(self.transport.getHost(), data))
        for online in self.factory.local_clients.online:
            online.send_command(data)

    def connectionMade(self):
        self.factory.online.append(self)

    def connectionLost(self, reason):
        self.factory.online.remove(self)


class MarantzTelnetServerFactory(protocol.ServerFactory):
    protocol = MarantzTelnetServer

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


class RPCTelnetServer(protocol.Protocol):
    def dataReceived(self, data):
        rpc = self.factory.rpc
        print('From {}: {}'.format(self.transport.getHost(), data.strip('\r\n')))
        rpc.connect()
        cmd_on = re.search('ON[ ](?P<outlet>\d)', data)
        if cmd_on:
            outlet = int(cmd_on.group('outlet'))
            rpc.power_on(outlet)
            status = rpc.get_status()
            if outlet > 0:
                self.transport.write(status[outlet])
            else:
                self.transport.write('On')
        cmd_off = re.search('OFF[ ](?P<outlet>\d)', data)
        if cmd_off:
            outlet = int(cmd_off.group('outlet'))
            rpc.power_off(outlet)
            status = rpc.get_status()
            if outlet > 0:
                self.transport.write(status[outlet])
            else:
                self.transport.write('Off')
        cmd_temp = re.search('TEMP', data)
        if cmd_temp:
            status = rpc.get_status()
            self.transport.write(str(status['temp']))
        cmd_current = re.search('CURRENT', data)
        if cmd_current:
            status = rpc.get_status()
            self.transport.write(str(status['current']))
        rpc.disconnect()

    def connectionMade(self):
        self.factory.online.append(self)

    def connectionLost(self, reason):
        self.factory.online.remove(self)


class RPCTelnetServerFactory(protocol.ServerFactory):
    protocol = RPCTelnetServer

    def __init__(self, ip=None, port=None, username='admin', password='admin'):
        self.rpc = rpc3.RPC3(ip, port, username, password)
        self.online = []
