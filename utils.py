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
        message.setSender(self.factory.aid)
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
            self.handle_identif(loads(message.content))
        elif self.STATE == "READY":
            pass
        message = ACLMessage()
        self.factory.msgs.append(message)
            
    def handle_identif(self, aid):
        '''
            Este método é utilizado para cadastrar o agente que esta se identificando
            na tabela de agentes ativos.
        '''
        if aid.name in self.factory.agents:
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
        self.factory.agents[aid.name] = self
        self.factory.table[aid.name] = aid
        displayMessage('AMS', 'Agente '+ aid.name + ' identificado com sucesso')
        
        # prepara mensagem de resposta
        message = ACLMessage(ACLMessage.INFORM)
        message.setSender(self.factory.aid)
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
        
        # dictionary que tem como keys o nome dos agentes e como valor a instancia do objeto instanciado
        # pela classe twisted.protocols.basic.LineReceiver
        self.agents = {}
        
        # dictionary que tem como keys o nome dos agentes e como valor o objeto aid que identifica o agente
        # indicado pela chave
        self.table = {}
        
        # lista que armazena as mensagens recebidas pelo AMS, devera ser utilizada posteriormente pelo
        # serviço de visualização de mensagens
        self.msgs = []
        
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
    def __init__(self, factory):
        self.factory = factory
        self.state = 'IDENT'
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
            peer = self.transport.getPeer()
            for message in self.factory.messages:
                for receiver in message.receivers:
                    if int(receiver.port) == int(peer.port):
                        self.sendLine(message.getMsg())
                        self.factory.messages.remove(message)
                        print 'mensagem enviada'

    def lineReceived(self, line):
        '''
            Este método é executado sempre que uma mesagem é recebida pelo agente Sniffer
        '''
        if self.state == 'IDENT':
            self.state = 'READY'
        
        message = ACLMessage()
        message.setMsg(line)
        # este método é executado caso a mensagem recebida tenha sido enviada pelo AMS
        # para atualização da tabela de agentes disponíveis
        if 'AMS' in message.sender.name:
            self.factory.ui.listWidget.clear()
            self.factory.table = loads(message.content)
            for agent in self.factory.table:
                serifFont = QtGui.QFont(None,10, QtGui.QFont.Bold)
                item = QtGui.QListWidgetItem(str(agent) + '\n')
                item.setFont(serifFont)
                self.factory.ui.listWidget.addItem(item)
        elif message.performative == ACLMessage.INFORM:
            self.showMessages(message)
            self.transport.loseConnection()
        
    def onItemChanged(self, current, previous):
        for name, aid in self.factory.table.iteritems():
            if name in current.text():
                message = ACLMessage(ACLMessage.REQUEST)
                message.setSender(self.factory.aid)
                message.addReceiver(AID(current.text()))
                print message.sender.name
                message.setContent('Request messages history')
                twisted.internet.reactor.connectTCP('localhost', aid.port, self.factory)
                self.factory.messages.append(message)
    
    def showMessages(self, message):
        print 'exibindo mensagens'
        messages = loads(message.content)
        self.factory.ui.listWidget_2.clear()
        for message in messages:
            serifFont = QtGui.QFont(None,10, QtGui.QFont.Bold)
            item = Item(message, serifFont)
            self.factory.ui.listWidget_2.addItem(item)
    
    def onItemEntered(self, item):
        print 'Enter!'
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
        
def startLoop():
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
    
    # lança o loop do Twisted
    twisted.internet.reactor.run()
    