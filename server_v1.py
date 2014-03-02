# -*- coding: utf-8 -*-
"""
Created on Mon Jan 27 23:54:15 2014

@author: lucas
"""

from twisted.internet import protocol, reactor
from datetime import datetime
from Messages import ACLMessage

class Server(protocol.Protocol):

    def __init__(self, factory):
        self.factory = factory
        self.STATE = "IDENT"
        self.name = None
        self.msg = {}
        
    def connectionMade(self):
        self.factory.contMsg += 1
        self.factory.msgNotif('Uma conexao foi estabelecida com o servidor central')
        self.factory.msgNotif('Numero de conexoes estabelecidas: ' + str(self.factory.contMsg))
        self.factory.msgNotif('Aguardando pela identificacao do agente...')
        
    def connectionLost(self, reason):
        self.factory.msgNotif('Uma conexao foi encerrada com o servidor central')
        self.factory.contMsg -= 1
        self.factory.msgNotif('Numero de conexoes remanescentes: ' + str(self.factory.contMsg))
        
    def dataReceived(self, data):
        if self.STATE == "IDENT":
            msg = ACLMessage()
            msg.setMsg(data)
            self.handle_identif(msg.sender)
        elif self.STATE == "READY":
            pass
        self.factory.msgs.append(data)
            
    def handle_identif(self, name):
        if name in self.factory.agents:
            self.factory.msgNotif('Falha na Identificacao do agente ' + name)
            self.transport.write('Ja existe um agente com este identificador. Por favor, escolha outro.')
            return
        self.name = name
        self.factory.agents[name] = self
        self.factory.msgNotif('Agente '+ name + ' identificado com sucesso')
        self.transport.write('Agente '+ name + ' identificado com sucesso')
        self.STATE = "READY"
        
    def sendMsg(self, data, agent):
        pass
        
    def sendMsgBroadcast(self, data):
        msg = '<%s> %s' % (self.agent, data)
        
        for name, protocol in self.factory.agents.iteritens():
            if protocol != self:
                protocol.transport.write(msg)
        
class ServerFactory(protocol.Factory):
    
    def __init__(self, port):
        self.agents = {}
        self.msgs = []
        self.contMsg = 0
        self.numConec = 0
        self.msgNotif('AMS is serving now on port ' + str(port))
        
    def buildProtocol(self, addr):
        return Server(self)
    
    def msgNotif(self, data):
        date = datetime.now()
        date = date.strftime('%d/%m/%Y %H:%M:%S --> ')
        print '[MAS] ' + date + data
        
reactor.listenTCP(8000, ServerFactory(8000))
reactor.run()