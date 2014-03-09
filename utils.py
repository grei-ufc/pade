#! /usr/bin/python
# -*- coding: utf-8 -*-

"""
Created on Mon Jan 27 23:54:15 2014

@author: lucas
"""

from twisted.internet import protocol, reactor
from twisted.protocols.basic import LineReceiver
from datetime import datetime
from messages import ACLMessage
from pickle import dumps

class AMS(LineReceiver):
    '''
        Esta classe implementa os comportamentos de um agente AMS
        Agent Mannagement Service
        ============
        
        A princiapal funcionalidade do AMS é registrar todos os agentes que
        estão conectados ao sistema e atualizar a tabela de agentes de cada
        um deles sempre que um novo agente se conectar. 
    '''

    def __init__(self, factory):
        '''
            Inicializa o objeto instanciado com os parâmetros iniciais
            @param factory: factory do protocolo do AMS 
        '''
        self.factory = factory
        self.STATE = "IDENT"
        self.name = None
        
    def connectionMade(self):
        '''
            Quando uma conexão é realizada este metodo é chamado,
            Ele registra a conexão com o cliente em self.factory.connections
        '''
        self.factory.connections += 1
        displayMessage('AMS', 'Uma conexao foi estabelecida com o servidor central')
        displayMessage('AMS', 'Numero de conexoes estabelecidas: ' + str(self.factory.connections))
        displayMessage('AMS', 'Aguardando pela identificacao do agente...')
        
    def connectionLost(self, reason):
        '''
            Quando uma conexão é encerrada este método é chamado.
            Ele decrementa a variavel que conta o numero de conexões ativas com o AMS
            e exclue este agente da tebela de agentes ativos.
            Ele também envia mensagem para todos os agentes ativos com a tabela de
            agentes conectados atualizada
        '''
        displayMessage('AMS', 'Uma conexao foi encerrada com o servidor central')
        self.factory.connections -= 1
        try:
            self.factory.agents.pop(self.name)
        except:
            displayMessage('AMs', 'Erro ao desconectar agente...')
            
        # prepara mensagem de atualização de tabela de agentes
        message = ACLMessage(ACLMessage.INFORM)
        message.setSender('AMS')
        message.setContent(dumps(self.factory.table))
        
        # envia tabela de agentes atualizada a todos os agentes com conexao ativa com o AMS
        self.broadcastMessage(message)
        
        displayMessage('AMS', 'Numero de conexoes remanescentes: ' + str(self.factory.connections))
        
    def lineReceived(self, line):
        '''
            Quando uma mensagem é enviada ao AMS este método é executado.
            Quando em fase de identificação, o AMS registra o agente
            em sua tabele de agentes ativos
        '''
        if self.STATE == "IDENT":
            message = ACLMessage()
            message.setMsg(line)
            self.handle_identif(message.sender, int(message.content))
        elif self.STATE == "READY":
            pass
        message = ACLMessage()
        self.factory.msgs.append(message)
            
    def handle_identif(self, name, port):
        '''
            Este método é utilizado para cadastrar o agente que esta se identificando
            na tabela de agentes ativos.
        '''
        if name in self.factory.agents:
            displayMessage('AMS', 'Falha na Identificacao do agente ' + name)
            
            # prepara mensagem de resposta
            message = ACLMessage(ACLMessage.REFUSE)
            message.setSender('AMS')
            message.addReceiver(name)
            message.setContent('Ja existe um agente com este identificador. Por favor, escolha outro.')
            # envia mensagem
            self.sendLine(message.getMsg())
            return
        self.name = name
        self.factory.agents[name] = self
        self.factory.table[name] = port
        displayMessage('AMS', 'Agente '+ name + ' identificado com sucesso')
        
        # prepara mensagem de resposta
        message = ACLMessage(ACLMessage.INFORM)
        message.setSender('AMS')
        message.setContent(dumps(self.factory.table))
        
        # envia tabela de agentes atualizada a todos os agentes com conexao ativa com o AMS
        self.broadcastMessage(message)
        self.STATE = "READY"
    
    def broadcastMessage(self, message):
        '''
            Este método é utilizado para o envio de mensagems de atualização da
            tabela de agentes ativos sempre que um novo agente é connectado.
        '''
        for name, protocol in self.factory.agents.iteritems():
            displayMessage('AMS', 'Mensagem de atualização de tabela para o agente: ' + name)
            protocol.sendLine(message.getMsg())
        
class AMSFactory(protocol.Factory):
    
    def __init__(self, port):
        self.agents = {}
        self.table = {}
        self.msgs = []
        self.port = port
        self.connections = 0
        displayMessage('AMS', 'AMS is serving now on port ' + str(self.port))
        
    def buildProtocol(self, addr):
        return AMS(self)
    

def displayMessage(name, data):
    '''
        Metodo utilizado para exibicao de mensagens no console de comandos
    '''
    date = datetime.now()
    date = date.strftime('%d/%m/%Y %H:%M:%S --> ')
    print '[' + name + '] ' + date + str(data)

def startAMS(port):
    '''
        Metodo utilizado na inicialização do laço de execução do AMS 
    '''
    ams = AMSFactory(port)
    reactor.listenTCP(port, ams)
    
def startLoop():
    # inicia a execuçao do laço principal do agente
    reactor.run()