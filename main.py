import telnet_server as server
from pioneer_avr import client as avr
from twisted.internet import reactor

def main():
    avr_ip = '10.50.4.85'
    avr_port = 23
    local_port = 8900

    my_avr = avr.PioneerClientFactory()
    my_server = server.TelnetServerFactory()
    my_avr.local_server = my_server
    my_server.local_clients = my_avr

    reactor.connectTCP(avr_ip, avr_port, my_avr)
    reactor.listenTCP(local_port, my_server)
    reactor.run()

if __name__=='__main__':
    main()
