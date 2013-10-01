from twisted.internet import protocol
from twisted.protocols import telnet

import re
import simplejson
import os
import sys
import time

def byte_to_hex(byte):
    return ''.join( [ "%02X " % ord( x ) for x in byte ] ).strip()

def hex_to_byte(hex):
    bytes = []

    hex = ''.join( hex.split(" ") )
    hex = '0822' + hex
    checksum = 256
    for i in range(0, len(hex), 2):
        dec = int (hex[i:i+2], 16 )
        bytes.append( chr( dec ) )
        checksum -= dec
    if checksum < 0:
        checksum = 256 + checksum
    bytes.append(chr(checksum))

    return ''.join( bytes )

class SamsungClient(telnet.Telnet):
    def __init__(self):
        self.pwr = None
        self.vol = None

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
        print("From TV: " + byte_to_hex(data))
        if '\n' in data:
            print('newline')
        if '\r' in data:
            print('cr')
#        data = data.strip('\r').split('\n')
#        for line in data:
#            if line and line[0] != 'R':
#                print('From TV: {}'.format(line))
#                self.parse_input(line)
#                for online in self.factory.local_server.online:
#                    online.transport.write(line+'\r\n')

    def send_command(self, cmd):
        while self.lock:
            pass
        cmd = cmd.strip('\n\r')
        for in_cmd, info in self.commands['to'].iteritems():
            if re.search('^' + in_cmd + '$', cmd) != None:
                self.lock = True
                time.sleep(0.1)
                send = hex_to_byte(info['cmd'])
                print('To TV: {}'.format(byte_to_hex(send)))
                self.transport.write(send)
                time.sleep(0.1)
                self.lock = False

    def parse_input(self, data):
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
        fl = re.search('FL.*', data)
        if fl:
            out = ''
            for c in range(4, 32, 2):
                out += chr(int(fl.group()[c:c+2], 16))
            print(out)

    def connectionLost(self, reason):
        print('Connection lost: {}'.format(reason))
        self.factory.online.remove(self)

class SamsungClientFactory(protocol.ReconnectingClientFactory):
    def __init__(self):
        self.online = []
        self.local_clients = []

    def startedConnecting(self, connector):
        print('Starting connection: {}'.format(connector))

    def buildProtocol(self, addr):
        print('Connected to {}'.format(addr))
        p = SamsungClient()
        p.factory = self
        self.resetDelay()
        return p

    def clientConnectionLost(self, connector, reason):
        print('Lost connection to {}: {}'.format(connector, reason))
        protocol.ReconnectingClientFactory.clientConnectionFailed(self, connector, reason)
