# -*- coding: utf-8 -*-

from twisted.internet import protocol, reactor

class Echo(protocol.Protocol):
    def connectionMade(self):
        self.transport.write('Hello Server!')
        print 'Conacxão realizada!'

    def dataReceived(self, data):
        print data

class EchoFactory(protocol.ClientFactory):
    def buildProtocol(self, addr):
        return Echo()

    def clientConnectionFailed(self, connector, reason):
        print 'Conexão falhou!'
        print reason.getErrorMessage()
        reactor.stop()

if __name__ == '__main__':
	print 'Conectando...'
	reactor.connectTCP('192.168.0.32', 1234, EchoFactory())
	reactor.run()