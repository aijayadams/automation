import telnet_server as server
from pioneer_avr import client as avr
from optoma_proj import client as proj
from twisted.internet import reactor

def main():
    avr_ip = '10.50.4.85'
    avr_port = 23
    tv_serial_ip = '10.50.4.89'
    tv_serial_port = 5000
    rpc1_ip = '10.50.4.11'
    rpc1_port = 23

    local_avr_port = 8900
    local_tv_serial_port = 8901
    local_rpc1_port = 8902

    my_avr = avr.PioneerClientFactory()
    my_tv_serial = proj.SamsungClientFactory()

    my_avr_server = server.PioneerTelnetServerFactory()
    my_tv_server = server.SamsungTelnetServerFactory()
    my_rpc1_server = server.RPCTelnetServerFactory(ip=rpc1_ip, port=rpc1_port)

    my_avr.local_server = my_avr_server
    my_avr_server.local_clients = my_avr

    my_tv_serial.local_server = my_tv_server
    my_tv_server.local_clients = my_tv_serial

    reactor.connectTCP(avr_ip, avr_port, my_avr)
    reactor.connectTCP(tv_serial_ip, tv_serial_port, my_tv_serial)
    reactor.listenTCP(local_avr_port, my_avr_server)
    reactor.listenTCP(local_tv_serial_port, my_tv_server)
    reactor.listenTCP(local_rpc1_port, my_rpc1_server)
    reactor.run()

if __name__=='__main__':
    main()
