# -*- coding: utf-8 -*-
"""
Created on Wed Jan 29 13:53:31 2014

@author: lucas
"""

from twisted.internet import protocol, reactor
from datetime import datetime
from Messages import ACLMessage

class Agent(protocol.Protocol):
    
    def __init__(self, factory, name):
        self.factory = factory        
        self.name = name
        
    def connectionMade(self):
        self.factory.msgNotif('Iniciando Processo de Identificacao...')
        msg = ACLMessage()
        msg.setReceiver('AMS')
        msg.setSender(self.name)
        msg.setPerformative(ACLMessage.Inform)
        msg.setContent('IDENT')
        self.transport.write(msg.getMsg())
    
    def dataReceived(self, data):
        self.factory.msgNotif(data)

class AgentFactory(protocol.ClientFactory):

    def __init__(self, name):
        self.name = name
        self.msgNotif('Agente ' + name + ' lancado')
        
    def buildProtocol(self, addr):
        return Agent(self, self.name)
    
    def clientConnectionFailed(self, connector, reason):
        print 'Connection failed:', reason.getErrorMessage()
    
    def clientConnectionLost(self, connector, reason):
        print 'Connection lost:', reason.getErrorMessage()
    
    def msgNotif(self, data):
        date = datetime.now()
        date = date.strftime('%d/%m/%Y %H:%M:%S --> ')
        print '[AGENT] ' + date + data

reactor.connectTCP('localhost', 8000, AgentFactory("lucas"))
reactor.run()