from __future__ import print_function

import pexpect
import re

RPC_IP = '10.50.4.11'
RPC_PORT = 23
RPC_USERNAME = 'admin'
RPC_PASSWORD = 'admin'

def main():
    rpc1 = RPC3(RPC_IP, RPC_PORT, RPC_USERNAME, RPC_PASSWORD)
    rpc1.connect()
    print(rpc1.get_status())
    for outlet in [8]:
        rpc1.power_off(outlet)
        print(rpc1.get_status())
        rpc1.power_on(outlet)
        print(rpc1.get_status())
    rpc1.disconnect()


class my_spawn(pexpect.spawn):
    def sendline(self, text, *args, **kwargs):
        self.send(text + '\r', *args, **kwargs)


class RPC3(object):
    def __init__(self, ip, port, username, password):
        self.ip = ip
        self.port = port
        self.username = username
        self.password = password
        self.client = None
        self.status = {}

    def connect(self):
        print('Connecting...', end='')
        telnet = my_spawn('telnet {ip} {port}'.format(
            ip=self.ip, port=self.port))
        print('OK')
    
        print('Sending username...', end='')
        telnet.expect('username>')
        telnet.sendline(self.username)
        print('OK')
    
        print('Sending password...', end='')
        telnet.expect('password>')
        telnet.sendline(self.password)
        print('OK')
        self.client = telnet
    
    def disconnect(self):
        print('Logging out...', end='')
        self.client.expect('election>')
        self.client.sendline('6')
        print('OK')

    def check_status(self):
        print('Checking status...', end='')
        self.client.expect('election>')
        self.client.sendline('1')
        self.client.expect('>')
        self.client.sendline('STATUS')
        self.client.expect('commands')

        self._parse_status(self.client.before)

        self.client.sendline('')
        self.client.expect('>')
        self.client.sendline('MENU')
        print('OK')

    def _parse_status(self, status):
        current = re.search('True[ ]RMS[ ]current:[ ]+(?P<current>.*)[ ]Amps', status)
        if current:
            self.status['current'] = float(current.group('current'))

        temp = re.search('Internal[ ]Temperature:[ ](?P<temp>.*)[ ]C', status)
        if temp:
            self.status['temp'] = float(temp.group('temp'))

        outlets = {}
        for match in re.finditer('(?P<number>\d)[ \d\w]+(?P<status>On|Off)', status):
            outlets[int(match.group('number'))] = match.group('status')
        self.status.update(outlets)

    def get_status(self):
        self.check_status()
        return self.status

    def power_on(self, outlet):
        self._power_cmd('ON {}'.format(outlet))

    def power_off(self, outlet):
        self._power_cmd('OFF {}'.format(outlet))

    def _power_cmd(self, state):
        print('Turning {}...'.format(state), end='')
        self.client.expect('election>')
        self.client.sendline('1')
        self.client.expect('>')
        self.client.sendline(state)
        self.client.expect('N\)>')
        self.client.sendline('y')
        self.client.expect('>')

        self._parse_status(self.client.before)

        self.client.sendline('MENU')
        print('OK')
        

if __name__ == '__main__':
    main()
