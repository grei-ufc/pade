#! /usr/bin/python
# -*- coding: utf-8 -*-

from twisted.internet import protocol, reactor
from twisted.protocols.basic import LineReceiver
from messages import ACLMessage
from aid import AID
from utils import displayMessage
from pickle import dumps, loads

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
            msg.addReceiver(AID(name='AMS' + '@' + self.factory.ams['name'] + ':' + str(self.factory.ams['port']) ))
            msg.setSender(self.factory.aid)
            msg.setPerformative(ACLMessage.INFORM)
            msg.setContent(dumps(self.factory.aid))
            
            # envia a mensagem ao AMS
            self.sendLine(msg.getMsg())
        else:
            if self.factory.messages != []:
                for name, aid in self.factory.table.iteritems():
                    if aid.port == self.transport.getPeer().port:
                        self.factory.connections[name] = self
                message = self.factory.messages.pop(0)
                self.sendLine(message.getMsg())
            
        
    def lineReceived(self, line):
        if self.state == 'IDENT':
            message = ACLMessage()
            message.setMsg(line)
            self.factory.table = loads(message.content)
            displayMessage(self.factory.aid.name, 'tabela atualizada: ' + str(self.factory.table.keys()))
            self.state = 'READY'
            self.factory.onStart()
        else:
            message = ACLMessage()
            message.setMsg(line)
            if 'AMS' in message.sender.name:
                self.factory.table = loads(message.content)
                displayMessage(self.factory.aid.name, 'tabela atualizada: ' + str(self.factory.table.keys()))
            else:
                self.factory.react(message)
        
    def connectionLost(self, reason):
        displayMessage(self.factory.aid.name,'Perda de Conexão')

class AgentFactory(protocol.ClientFactory):
    
    def __init__(self, aid, ams, react=None, onStart=None):
        self.aid = aid
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
        displayMessage(self.aid.name, 'Falha na Conexão')
        reactor.stop()
    
    def clientConnectionLost(self, connector, reason):
        displayMessage(self.aid.name, 'Perda de Conexão')
        reactor.stop()
    
    def startedConnecting(self, connector):
        pass
    
        
#=================================
# Agent Class
#=================================
class Agent():
    
    def __init__(self, aid):
        self.aid = aid
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
        self.agentInstance = AgentFactory(self.aid, self.ams, self.react, self.onStart)
        reactor.listenTCP(self.aid.port, self.agentInstance)
        
    def react(self, message):
        '''
            Este metodo deve ser SobreEscrito e será executado todas as vezes que
            o agente em questão receber algum tipo de dado
        '''
        pass
    
    def send(self, message):
        # for percorre os destinatarios da mensagem
        for receiver in message.receivers:
            
            # for percorre os agentes que já estão conectados
            for name in self.agentInstance.connections.keys():
                # if verifica se o nome do destinatario está entre os agentes já conectados
                if receiver.localname in name and receiver.localname != self.aid.localname:
                    # corrige o parametro porta e host gerado aleatoriamente quando apenas um nome
                    # e dado como identificador de um destinatário
                    receiver.port = self.agentInstance.table[name].port
                    receiver.host = self.agentInstance.table[name].host
                    # envia a mensagem ao agente destinatario
                    self.agentInstance.connections[receiver].sendLine(message.getMsg())
                    break
            else:
                # for percorre a lista de agentes disponíveis
                for name in self.agentInstance.table:
                    # if verifica se o nome do destinatario está entre os agentes disponíveis
                    if receiver.localname in name and receiver.localname != self.aid.localname:
                        # corrige o parametro porta e host gerado aleatoriamente quando apenas um nome
                        # e dado como identificador de um destinatário
                        receiver.port = self.agentInstance.table[name].port
                        receiver.host = self.agentInstance.table[name].host
                        # se conecta ao agente e envia a mensagem
                        self.agentInstance.messages.append(message)
                        reactor.connectTCP('localhost', self.agentInstance.table[name].port, self.agentInstance)
                        break
                else:
                    displayMessage(self.aid.localname, 'Agente ' + receiver.name + ' não esta ativo')
    
    def onStart(self):
        pass