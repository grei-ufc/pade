#! /usr/bin/python
# -*- coding: utf-8 -*-

from twisted.internet import protocol, reactor
from twisted.protocols.basic import LineReceiver
from messages import ACLMessage
from utils import displayMessage
from pickle import loads

#=================================
# Server and Client Classes
#=================================
class AgentProtocol(LineReceiver):
    '''
        Esta classe implementa o protocolo que será seguido pelos agentes
        na comunicação entre
    '''
    
    def __init__(self, factory):
        self.factory = factory
        self.state = 'IDENT'
        
        # conecta o agente ao AMS
        reactor.connectTCP(self.factory.ams['name'], self.factory.ams['port'], self.factory)
    
    def connectionMade(self):
        if self.state == 'IDENT':
           
            # cria a mensagem de registro no AMS
            msg = ACLMessage()
            msg.addReceiver('AMS')
            msg.setSender(self.factory.name)
            msg.setPerformative(ACLMessage.INFORM)
            msg.setContent(self.factory.port)
            
            # envia a mensagem ao AMS
            self.sendLine(msg.getMsg())
        else:
            if self.factory.messages != []:
                for name, port in self.factory.table.iteritems():
                    if port == self.transport.getPeer().port:
                        self.factory.connections[name] = self
                message = self.factory.messages.pop(0)
                self.sendLine(message.getMsg())
            
        
    def lineReceived(self, line):
        if self.state == 'IDENT':
            message = ACLMessage()
            message.setMsg(line)
            self.factory.table = loads(message.content)
            displayMessage(self.factory.name, 'tabela atualizada: ' + str(self.factory.table.keys()))
            self.state = 'READY'
            self.factory.onStart()
        else:
            message = ACLMessage()
            message.setMsg(line)
            if 'AMS' in message.sender:
                self.factory.table = loads(message.content)
                displayMessage(self.factory.name, 'tabela atualizada: ' + str(self.factory.table.keys()))
            else:
                self.factory.react(message)
        
    def connectionLost(self, reason):
        displayMessage(self.factory.name,'Perda de Conexão')

class AgentFactory(protocol.ClientFactory):
    
    def __init__(self, name, port, ams, react=None, onStart=None):
        self.name = name
        self.port = port
        self.ams = ams
        self.messages = []
        self.react = react
        self.onStart = onStart
        self.table = {}
        self.connections = {}
        self.agentProtocol = AgentProtocol(self)
        
    def buildProtocol(self, addr):
        return self.agentProtocol
    
    def clientConnectionFailed(self, connector, reason):
        displayMessage(self.name, 'Falha na Conexão')
        reactor.stop()
    
    def clientConnectionLost(self, connector, reason):
        displayMessage(self.name, 'Perda de Conexão')
        reactor.stop()
    
    def startedConnecting(self, connector):
        pass
    
        
#=================================
# Agent Class
#=================================
class Agent():
    
    def __init__(self, name, port):
        self.name = name
        self.port = port
        self.ams = {}
        self.agentInstance = None
        
    def setAMS(self, name='localhost', amsPort=8000):
        '''
            Este metodo configura os parametros do agente AMS,
            e dos agentes que instanciam a classe, deixando os
            agentes aguandando apenas o chamado do metodo 
            reactor.run()
        '''
        self.ams['name'] = name
        self.ams['port'] = amsPort
    
    def start(self):
        '''
            cria a instancia da classe AgentProtocol e inicializa o agente
        '''
        self.agentInstance = AgentFactory(self.name, self.port, self.ams, self.react, self.onStart)
        reactor.listenTCP(self.port, self.agentInstance)
        
    def react(self, message):
        '''
            Este metodo deve ser SobreEscrito e será executado todas as vezes que
            o agente em questão receber algum tipo de dado
        '''
        pass
    
    def send(self, message):
        for receiver in message.receivers:
            if receiver in self.agentInstance.connections.keys() and receiver != self.name:
                self.agentInstance.connections[receiver].sendLine(message.getMsg())
            else:
                if receiver in self.agentInstance.table.keys() and receiver != self.name:
                    self.agentInstance.messages.append(message)
                    reactor.connectTCP('localhost', self.agentInstance.table[receiver], self.agentInstance)
                else:
                    displayMessage(self.name, 'Agente ' + receiver + ' não esta ativo')
    
    def onStart(self):
        pass