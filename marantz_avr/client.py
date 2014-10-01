from twisted.internet import protocol
from twisted.protocols import telnet

import re
import simplejson
import os
import sys
import time

class MarantzClient(telnet.Telnet):
    def __init__(self):
        self.pwr = None
        self.vol = None
        self.mut = None
        self.panel = 'FP'

        self.lock = False
        self.cmd_file = 'commands.json'
        self.my_path = os.path.realpath(
          os.path.join(os.getcwd(), os.path.dirname(__file__)))
        self.commands = self.load_commands()

    def load_commands(self):
        f = open(os.path.join(self.my_path, self.cmd_file))
        commands = simplejson.load(f)
        f.close()
        return commands

    def connectionMade(self):
        self.factory.online.append(self)

    def dataReceived(self, data):
        data = data.strip('\r').split('\n')
        for line in data:
            if line and line[0] != 'R':
                print('From AVR: {}'.format(line))
                self.parse_input(line)
                for online in self.factory.local_server.online:
                    online.transport.write(line+'\r\n')

    def send_command(self, cmd):
        while self.lock:
            pass
        success = False
        for key in self.commands['to']:
            if re.search(key, cmd) != None:
                cmd = cmd.strip('\n\r')
                print('To AVR: {}'.format(cmd))
                self.lock = True
                self.transport.write('\r\n')
                time.sleep(0.1)
                self.transport.write('\r'+cmd+'\r')
                success = True
                time.sleep(0.1)
                self.lock = False
        if success:
            for online in self.factory.local_server.online:
                online.transport.write('1')
        else:
            print('Invalid command: {}'.format(cmd))
            for online in self.factory.local_server.online:
                online.transport.write('0')

    def parse_input(self, data):
        vol = re.search('MV\d{2}', data)
        if vol:
            self.vol = vol.group()
        pwr = re.search('ZM(ON|OFF)', data)
        if pwr:
            self.pwr = pwr.group()
            if pwr == 'ZMON' and not self.vol:
                self.vol = 'MV00'
            else:
                self.transport.write('PW?')
        fl = re.search('FL.*', data)
        if fl:
            out = ''
            for c in range(4, 32, 2):
                out += chr(int(fl.group()[c:c+2], 16))
            self.panel = out
            print(out)
        mut = re.search('MU(ON|OFF)', data)
        if mut:
            self.mut = mut.group()

    def connectionLost(self, reason):
        print('Connection lost: {}'.format(reason))
        self.factory.online.remove(self)

class MarantzClientFactory(protocol.ReconnectingClientFactory):
    def __init__(self):
        self.online = []
        self.local_clients = []

    def startedConnecting(self, connector):
        print('Starting connection: {}'.format(connector))

    def buildProtocol(self, addr):
        print('Connected to {}'.format(addr))
        p = MarantzClient()
        p.factory = self
        self.resetDelay()
        return p

    def clientConnectionLost(self, connector, reason):
        print('Lost connection to {}: {}'.format(connector, reason))
        protocol.ReconnectingClientFactory.clientConnectionFailed(self, connector, reason)
