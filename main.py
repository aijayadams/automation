import pioneer_client, pioneer_server
from twisted.internet import reactor

def main():
    avr_ip = '10.50.4.85'
    avr_port = 23
    local_port = 8900

    avr = pioneer_client.PioneerClientFactory()
    server = pioneer_server.PioneerServerFactory()
    avr.local_server = server
    server.local_clients = avr

    reactor.connectTCP(avr_ip, avr_port, avr)
    reactor.listenTCP(local_port, server)
    reactor.run()

if __name__=='__main__':
    main()
