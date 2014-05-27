#! /usr/bin/python
# -*- coding: utf-8 -*-

"""
Created on Mon Jan 27 23:54:15 2014

@author: lucas
"""

import twisted.internet
from twisted.internet import protocol
from twisted.protocols.basic import LineReceiver
from datetime import datetime
from messages import ACLMessage
from pickle import dumps, loads
from aid import AID
from agentsGui import ControlAgentsGui, ControlACLMessageDialog

import sys

from PySide import QtCore, QtGui

#===============================================================================
# Protocolo do agente AMS
#===============================================================================

class AMS(LineReceiver):
    '''
        Esta classe implementa os comportamentos de um agente AMS
        Agent Mannagement Service
        ============
        
        A princiapal funcionalidade do AMS é registrar todos os agentes que
        estão conectados ao sistema e atualizar a tabela de agentes de cada
        um deles sempre que um novo agente se conectar. 
    '''

    MAX_LENGTH = 32768
    
    def __init__(self, factory):
        '''
            Inicializa o objeto instanciado com os parâmetros iniciais
            @param factory: factory do protocolo do AMS 
        '''
        self.factory = factory
        
    def connectionMade(self):
        pass
        
        peer = self.transport.getPeer()
        for message in self.factory.messages:
            if int(message[0].port) == int(peer.port):
                self.sendLine(message[1].getMsg())
                self.factory.messages.remove(message)
                self.transport.loseConnection()
                break
                                
    def connectionLost(self, reason):
        '''
            Quando uma conexão é encerrada este método é chamado.
            Ele decrementa a variavel que conta o numero de conexões ativas com o AMS
            e exclue este agente da tebela de agentes ativos.
            Ele também envia mensagem para todos os agentes ativos com a tabela de
            agentes conectados atualizada
        '''
        pass
#         displayMessage('AMS', 'Uma conexao foi encerrada com o servidor central')
#         self.factory.connections -= 1
#         try:
#             self.factory.agents.pop(self.name)
#         except:
#             displayMessage('AMS', 'Erro ao desconectar agente...')
#             
#         # prepara mensagem de atualização de tabela de agentes
#         message = ACLMessage(ACLMessage.INFORM)
#         message.setSender(self.factory.aid)
#         message.setContent(dumps(self.factory.table))
#         
#         # envia tabela de agentes atualizada a todos os agentes com conexao ativa com o AMS
#         self.broadcastMessage(message)
#         
#         displayMessage('AMS', 'Numero de conexoes remanescentes: ' + str(self.factory.connections))
        
    def lineReceived(self, line):
        '''
            Quando uma mensagem é enviada ao AMS este método é executado.
            Quando em fase de identificação, o AMS registra o agente
            em sua tabele de agentes ativos
        '''
        message = ACLMessage()
        message.setMsg(line)
        
        self.handle_identif(loads(message.content))
            
    def handle_identif(self, aid):
        '''
            Este método é utilizado para cadastrar o agente que esta se identificando
            na tabela de agentes ativos.
        '''
        if aid.name in self.factory.table:
            displayMessage('AMS', 'Falha na Identificacao do agente ' + aid.name)
            
            # prepara mensagem de resposta
            message = ACLMessage(ACLMessage.REFUSE)
            message.setSender(self.factory.aid)
            message.addReceiver(aid)
            message.setContent('Ja existe um agente com este identificador. Por favor, escolha outro.')
            # envia mensagem
            self.sendLine(message.getMsg())
            return
        self.aid = aid
        self.factory.table[self.aid.name] = self.aid
        displayMessage('AMS', 'Agente '+ aid.name + ' identificado com sucesso')
        
        # prepara mensagem de resposta
        message = ACLMessage(ACLMessage.INFORM)
        message.setSender(self.factory.aid)
        for receiver in self.factory.table.values():
            message.addReceiver(receiver)
            
            
        message.setContent(dumps(self.factory.table))
        self.broadcastMessage(message, aid)
        
        # envia tabela de agentes atualizada a todos os agentes com conexao ativa com o AMS
        
    
    def broadcastMessage(self, message, agent_aid):
        '''
            Este método é utilizado para o envio de mensagems de atualização da
            tabela de agentes ativos sempre que um novo agente é connectado.
        '''
        for name, aid in self.factory.table.iteritems():
            #displayMessage('AMS', 'Mensagem de atualização de tabela para o agente: ' + name)
            twisted.internet.reactor.connectTCP('localhost', int(aid.port), self.factory)
            self.factory.messages.append((aid, message))
                
        
class AMSFactory(protocol.ClientFactory):
    
    def __init__(self, port):
        
        self.state = 'IDENT'
        
        # dictionary que tem como keys o nome dos agentes e como valor o objeto aid que identifica o agente
        # indicado pela chave
        self.table = {}
        
        # lista que armazena as mensagens recebidas pelo AMS, devera ser utilizada posteriormente pelo
        # serviço de visualização de mensagens
        self.messages = []
        
        # aid do agente AMS
        self.aid = AID(name='AMS' + '@' + 'localhost' + ':' + str(port))
        
        # numero de conexões ativas
        self.connections = 0
        
        displayMessage('AMS', 'AMS is serving now on port ' + str(self.aid.port))
        
    def buildProtocol(self, addr):
        return AMS(self)


#===============================================================================
# Protocolo do Agente GUI paramonitaramento dos agentes 
# e das mensagens dos agentes
#===============================================================================

class Sniffer(LineReceiver):
    
    MAX_LENGTH = 32768
    
    def __init__(self, factory):
        self.factory = factory
        # conecta o agente ao agente AMS
        twisted.internet.reactor.connectTCP(self.factory.ams['name'], self.factory.ams['port'], self.factory)
        # configura os sinais da interface grafica
        self.factory.ui.listWidget.currentItemChanged.connect(self.onItemChanged)
        self.factory.ui.listWidget_2.itemPressed.connect(self.onItemEntered)
        
    
    def connectionMade(self):
        '''
            Este método é executado sempre que uma conexão é executada entre 
            um cliente e um servidor
        '''
        
        # fase de identificação do agente com o AMS
        if self.factory.state == 'IDENT':
            # cria a mensagem de registro no AMS
            msg = ACLMessage()
            msg.addReceiver(AID(name='AMS' + '@' + self.factory.ams['name'] + ':' + str(self.factory.ams['port']) ))
            msg.setSender(self.factory.aid)
            msg.setPerformative(ACLMessage.INFORM)
            msg.setContent(dumps(self.factory.aid))
            
            # envia a mensagem ao AMS
            self.factory.state = 'READY'
            self.sendLine(msg.getMsg())
            self.transport.loseConnection()
        else:
            peer = self.transport.getPeer()
            for message in self.factory.messages:
                if int(message[0].port) == int(peer.port):
                    self.sendLine(message[1].getMsg())
                    self.factory.messages.remove(message)
                    #self.transport.loseConnection()
                    #print 'conexao encerrada'
                    break

    def connectionLost(self, reason):
        pass
    
    
    def lineLengthExceeded(self, line):
        print 'A mensagem e muito grande!!!'
        return LineReceiver.lineLengthExceeded(self, line)
    
    def lineReceived(self, line):
        '''
            Este método é executado sempre que uma mesagem é recebida pelo agente Sniffer
        '''
        
        message = ACLMessage()
        message.setMsg(line)
        
        displayMessage(self.factory.aid.name, 'Mensagem recebida de: ' + str(message.sender.name))
        
        # este método é executado caso a mensagem recebida tenha sido enviada pelo AMS
        # para atualização da tabela de agentes disponíveis
        if 'AMS' in message.sender.name:
            self.factory.ui.listWidget.clear()
            
            # loop for verifica se os agentes enviados na lista do AMS já estão cadastrados na tabela do agente
            agents = loads(message.content)
            for i in agents:
                for j in self.factory.table:
                    if i == j:
                        break
                else:
                    self.factory.table[i] = agents[i]
            
            for agent in self.factory.table:
                serifFont = QtGui.QFont(None,10, QtGui.QFont.Bold)
                item = QtGui.QListWidgetItem(str(agent) + '\n')
                item.setFont(serifFont)
                self.factory.ui.listWidget.addItem(item)
        
        # caso a mensagem recebida seja de um agente a lista de mensagens deste agente é atualizada
        elif message.performative == ACLMessage.INFORM:
            
            displayMessage(self.factory.aid.name, 'Lista de Mensagens Recebida')
            
            agent = message.sender.name
            for i in self.factory.agents_messages:
                if agent == i:
                    messages = self.factory.agents_messages[i]
                    messages.extend(loads(message.content))
                    self.factory.agents_messages[i] = messages
                    break
            else:
                self.factory.agents_messages[agent] = loads(message.content)
            
            print self.factory.agents_messages[agent]
            self.showMessages(self.factory.agents_messages[agent])
        
    def onItemChanged(self, current, previous):
        for name, aid in self.factory.table.iteritems():
            if name in current.text() and not ('Sniffer' in name):
                message = ACLMessage(ACLMessage.REQUEST)
                message.setSender(self.factory.aid)
                message.addReceiver(aid)
                message.setContent('Request messages history')
                
                self.factory.messages.append((aid, message))
                
                twisted.internet.reactor.connectTCP('localhost', aid.port, self.factory)
                break
                
    def showMessages(self, messages):
        '''
            Este método exibe a lista de mensagens que estão em na lista de mensagens do agente selecionado
        '''
        self.factory.ui.listWidget_2.clear()
        for message in messages:
            serifFont = QtGui.QFont(None,10, QtGui.QFont.Bold)
            item = Item(message, serifFont)
            self.factory.ui.listWidget_2.addItem(item)
    
    def onItemEntered(self, item):
        
        gui = ControlACLMessageDialog()
        gui.ui.senderText.setText(item.message.sender.name)
        gui.ui.communicativeActComboBox.setCurrentIndex(
                                                        gui.ui.communicativeActComboBox.findText(item.message.performative)
                                                        )
        for receiver in item.message.receivers:
            gui.ui.receiverListWidget.addItem(receiver.name)
        try:
            gui.ui.contentText.setText(str(loads(item.message.content)))
        except:
            gui.ui.contentText.setText(str(item.message.content))
        
        gui.ui.protocolComboBox.setCurrentIndex(
                                                gui.ui.protocolComboBox.findText(item.message.protocol)
                                                )
        gui.ui.languageText.setText(item.message.language)
        gui.ui.encodingText.setText(item.message.encoding)
        gui.ui.ontologyText.setText(item.message.ontology)
        gui.ui.inReplyToText.setText(item.message.in_reply_to)
        gui.ui.replyWithText.setText(item.message.reply_with)
        gui.exec_()

class SnifferFactory(protocol.ClientFactory):
    
    def __init__(self, aid, ams, ui):
        self.ui = ui    # instancia da interface grafica
        self.aid = aid  # identificação do agente
        self.ams = ams  # identificação do agente ams
        self.table = {} # armazena os agentes ativos, é um dicionário contendo chaves: nome e valores: aid
        self.agents_messages = {}
        self.state = 'IDENT'
        self.messages = [] # armazena as mensagens a serem enviadas
        self.protocol = Sniffer(self)
        
    def buildProtocol(self, addr):
        return self.protocol

class Item(QtGui.QListWidgetItem):
    def __init__(self, message, font):
        super(Item, self).__init__()
        self.setFont(font)
        self.message = message
        self.setText(message.performative.upper() + '\n' +
                                         'Enviada em: ' + message.attrib['date'] + '\n' +
                                         'Por: ' + message.sender.name + '\n')
        
#===============================================================================
# Metodos Utilitarios 
#===============================================================================

ams = {'name' : 'localhost', 'port' : 8000}
setGui = False

def displayMessage(name, data):
    '''
        Metodo utilizado para exibicao de mensagens no console de comandos
    '''
    date = datetime.now()
    date = date.strftime('%d/%m/%Y %H:%M:%S --> ')
    print '[' + name + '] ' + date + str(data)

def setAMS(name, port):
    '''
        Metodo utilizado na inicialização do laço de execução do AMS 
    '''
    global ams
    
    ams = {'name' : name, 'port' : port}
    
    amsFactory = AMSFactory(port)
    twisted.internet.reactor.listenTCP(port, amsFactory)

def configLoop(gui=False):
    '''
        Importa o elemento Qt4Reactor que integra o Loop do Twisted com o loop
        do Qt
    '''
    global setGui
    setGui = gui
    
    if gui == False:
        pass
    else:
        app = QtGui.QApplication(sys.argv)
        
        try:
            import qt4reactor
        except:
            print 'Erro ao importar o modulo qt4reactor'
        
        qt4reactor.install()
        
def startLoop(agents):
    '''
        Lança o loop do twisted integrado com o loop do Qt se a opção setGui for
        verdadeira, se não lança o loop do Twisted
    '''
    global ams, setGui
    
    if setGui == True:
        controlAgentsGui = ControlAgentsGui()
        controlAgentsGui.show()
    
        # instancia um AID para o agente Sniffer
        aid = AID('Sniffer_Agent')
        # instancia um objeto Factory para o agente Sniffer
        snifferFactory = SnifferFactory(aid, ams, controlAgentsGui.ui)
        # lança o agente como servidor na porta gerada pelo objeto AID
        twisted.internet.reactor.listenTCP(aid.port, snifferFactory)
    
    i = 0
    for agent in agents:
        i += 1
        twisted.internet.reactor.callLater(i, listenAgent, agent)
        
    
    # lança o loop do Twisted
    #twisted.internet.reactor.startRunning(init)
    twisted.internet.reactor.run()

def init():
    print 'Hello World!'
    
def listenAgent(agent):
    # Conecta o agente ao AMS
    twisted.internet.reactor.connectTCP(agent.ams['name'], agent.ams['port'], agent.agentInstance)
    # Conecta o agente à porta que será utilizada para comunicação
    twisted.internet.reactor.listenTCP(agent.aid.port, agent.agentInstance)