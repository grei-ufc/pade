#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
 Módulo de Utilidades
 --------------------

 Este módulo Python compõe a espinha dorçal do framework para 
 desenvolvimento de sistemas multiagentes em Python. Ele contém
 as classes que implementam os comportamentos de dois importantes
 agentes, o agente AMS e o agente Sniffer.

 Este módulo Python também disponibiliza métodos de configuração
 do loop twisted onde os agentes serão executados e caso se utilize
 interface gráfica, é neste módulo que o loop Qt4 é integrado ao 
 loop Twisted, além de disponibilizar métodos para lançamento do AMS
 e Sniffer por linha de comando e para exibição de informações no 
 terminal


 @author: lucas
"""

import twisted.internet
from twisted.internet import protocol
from twisted.protocols.basic import LineReceiver
from twisted.enterprise import adbapi
from datetime import datetime
from messages import ACLMessage
from pickle import dumps, loads
from uuid import uuid4
from aid import AID
from agentsGui import ControlAgentsGui, ControlACLMessageDialog

import sys
import optparse

try:
    from PySide import QtGui
except ValueError:
    pass


class AgentManagementProtocol(LineReceiver):

    """
        Agent Management protocol
        -------------------------

        Esta classe implementa os comportamentos de um agente AMS

        A princiapal funcionalidade do AMS é registrar todos os agentes que
        estão conectados ao sistema e atualizar a tabela de agentes de cada
        um deles sempre que um novo agente se conectar. 
    """

    MAX_LENGTH = 32768

    def __init__(self, factory):
        """
            Este método Inicializa o objeto que implementa a classe AMS

            Parâmetros
            ----------
            factory: factory do protocolo do AMS 
        """
        self.factory = factory

    def connectionMade(self):
        """
            connectionMade
            --------------

            Este método é executado sempre que uma conexão é realizada
            com o agente AMS
        """
        # armazena as informações do agente conectado por meio do metodo
        # transport.getPeer()
        peer = self.transport.getPeer()

        # laço for percorre as mensagens armazenadas na variavel
        # factory.messages e caso alguma mensagem seja para o agente
        # conectado esta será enviada
        for message in self.factory.messages:
            if int(message[0].port) == int(peer.port):
                # envia a mensagem por meio do metodo sendLine()
                self.sendLine(message[1].get_message())
                # remove a mesagem enviada da variavel factory.messages
                self.factory.messages.remove(message)
                display_message(
                    self.factory.aid.name,
                    'Mensagem enviada ao agente ' + message[0].name)
                # encerra a conexão com o agente
                self.transport.loseConnection()
                break

    def connectionLost(self, reason):
        """
            connectionLost
            --------------

            Este método é executado sempre que uma conexão é perdida 
            com o agente AMS
        """
        pass

    def connection_test_send(self):
        """
            Este método é executado ciclicamente com o objetivo de 
            verificar se os agentes estão conectados
        """
        display_message(self.factory.aid.name,
                        'Enviando mensagens de verificação da conexão...')
        for name, aid in self.factory.table.iteritems():
            display_message(
                self.factory.aid.name,
                'Tentando conexão com agente ' + name + '...')
            twisted.internet.reactor.connectTCP(
                aid.host, int(aid.port), self.factory)
            self.transport.loseConnection()
        else:
            twisted.internet.reactor.callLater(1,
                                               self.connection_test_send
                                               )

    def lineReceived(self, line):
        """
            Quando uma mensagem é enviada ao AMS este método é executado.
            Quando em fase de identificação, o AMS registra o agente
            em sua tabele de agentes ativos
        """
        message = ACLMessage()
        # carrega a mesagem recebida no objeto message
        message.set_message(line)

        # como o agente AMS só recebe mensagens
        self.handle_identif(loads(message.content))

    def handle_identif(self, aid):
        """
            handle_identif
            --------------

            Este método é utilizado para cadastrar o agente que esta se identificando
            na tabela de agentes ativos.
        """
        if aid.name in self.factory.table:
            display_message(
                'AMS', 'Falha na Identificacao do agente ' + aid.name)

            # prepara mensagem de resposta
            message = ACLMessage(ACLMessage.REFUSE)
            message.set_sender(self.factory.aid)
            message.add_receiver(aid)
            message.set_content(
                'Ja existe um agente com este identificador. Por favor, escolha outro.')
            # envia mensagem
            self.sendLine(message.get_message())
            return
        self.aid = aid
        self.factory.table[self.aid.name] = self.aid
        display_message(
            'AMS', 'Agente ' + aid.name + ' identificado com sucesso')

        # prepara mensagem de resposta
        message = ACLMessage(ACLMessage.INFORM)
        message.set_sender(self.factory.aid)
        for receiver in self.factory.table.values():
            message.add_receiver(receiver)

        message.set_content(dumps(self.factory.table))
        self.broadcast_message(message)

        # envia tabela de agentes atualizada a todos os agentes com conexao
        # ativa com o AMS

    def broadcast_message(self, message):
        """
            broadcast_message
            -----------------

            Este método é utilizado para o envio de mensagems de atualização da
            tabela de agentes ativos sempre que um novo agente é connectado.
        """
        for name, aid in self.factory.table.iteritems():
            twisted.internet.reactor.connectTCP(
                aid.host, int(aid.port), self.factory)
            self.factory.messages.append((aid, message))


class AgentManagementFactory(protocol.ClientFactory):

    """
        AgentManagementFactory
        ----------

        Esta classe implementa as ações e atributos do protocolo AMS
        sua principal função é armazenar informações importantes ao protocolo de comunicação 
        do agente AMS
    """

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

        display_message(
            'AMS', 'AMS esta servindo na porta' + str(self.aid.port))

        # instancia do objeto que implementa o protocolo AMS
        self.protocol = AgentManagementProtocol(self)

        # instancia o objeto que realizará a conexão com o banco de dados
        self.conn = adbapi.ConnectionPool(
            'sqlite3', 'database.db', check_same_thread=False)
        self.d = self.createAgentsTable()
        self.d.addCallback(self.insert_agent)

    def buildProtocol(self, addr):
        return self.protocol

    def clientConnectionFailed(self, connector, reason):
        for name, aid in self.table.iteritems():
            if aid.port == connector.port:
                display_message(
                    self.aid.name, 'O agente ' + aid.name + ' esta desconectado.')
                self.table.pop(name)
                message = ACLMessage(ACLMessage.INFORM)
                message.set_sender(self.aid)
                message.set_content(dumps(self.table))
                self.protocol.broadcast_message(message)
                break

    #========================================================================
    # Estes métodos são utilizados para a comunicação do loop twisted com o banco de dados
    #========================================================================
    def createAgentsTable(self):
        display_message(
            self.aid.name, 'Tabela de agentes criada no banco de dados.')
        return self.conn.runInteraction(self._cretateAgentsTable)

    def _cretateAgentsTable(self, transaction):
        display_message(
            self.aid.name, 'Tabela de agentes criada no banco de dados.')
        self.dbid = 'agents_' + str(uuid4().time)
        s = 'CREATE TABLE ' + self.dbid + '( id INTEGER PRIMARY KEY AUTOINCREMENT, ' +\
            'name VARCHAR(20), ' +\
            'port INTEGER);'
        transaction.execute(s)
        #transaction.execute('INSERT INTO ' + self.dbid + ' VALUES ' + '')

    def insert_agent(self):
        pass


#=========================================================================
# Protocolo do Agente GUI paramonitoramento dos agentes
# e das mensagens dos agentes
#=========================================================================

class Sniffer(LineReceiver):

    """
        Sniffer
        -------

        Esta classe implementa o agente Sniffer que tem o objetivo de 
        enviar mensagens para os agentes ativos e exibir suas mensagens
        por meio de uma GUI
    """

    MAX_LENGTH = 32768

    def __init__(self, factory):
        self.factory = factory
        # conecta o agente ao agente AMS
        twisted.internet.reactor.connectTCP(
            self.factory.ams['name'], self.factory.ams['port'], self.factory)
        # configura os sinais da interface grafica
        self.factory.ui.listWidget.currentItemChanged.connect(
            self.onItemChanged)
        self.factory.ui.listWidget_2.itemPressed.connect(self.on_item_entered)

    def connectionMade(self):
        """
            Este método é executado sempre que uma conexão é executada entre 
            um cliente e um servidor
        """

        # fase de identificação do agente com o AMS
        if self.factory.state == 'IDENT':
            # cria a mensagem de registro no AMS
            msg = ACLMessage()
            msg.add_receiver(
                AID(name='AMS' + '@' + self.factory.ams['name'] + ':' + str(self.factory.ams['port'])))
            msg.set_sender(self.factory.aid)
            msg.set_performative(ACLMessage.INFORM)
            msg.set_content(dumps(self.factory.aid))

            # envia a mensagem ao AMS
            self.factory.state = 'READY'
            self.sendLine(msg.get_message())
            self.transport.loseConnection()
        else:
            peer = self.transport.getPeer()
            for message in self.factory.messages:
                if int(message[0].port) == int(peer.port):
                    self.sendLine(message[1].get_message())
                    self.factory.messages.remove(message)
                    self.transport.loseConnection()
                    break

    def connectionLost(self, reason):
        pass

    def lineLengthExceeded(self, line):
        print 'A mensagem e muito grande!!!'
        return LineReceiver.lineLengthExceeded(self, line)

    def lineReceived(self, line):
        """
            Este método é executado sempre que uma mesagem é recebida pelo agente Sniffer
        """

        message = ACLMessage()
        message.set_message(line)

        display_message(self.factory.aid.name,
                        'Mensagem recebida de: ' + str(message.sender.name))

        # este método é executado caso a mensagem recebida tenha sido enviada pelo AMS
        # para atualização da tabela de agentes disponíveis
        if 'AMS' in message.sender.name:
            self.factory.ui.listWidget.clear()

            # loop for verifica se os agentes enviados na lista do AMS já estão
            # cadastrados na tabela do agente
            self.factory.table = loads(message.content)

            for agent in self.factory.table:
                serifFont = QtGui.QFont(None, 10, QtGui.QFont.Bold)
                item = QtGui.QListWidgetItem(str(agent) + '\n')
                item.setFont(serifFont)
                self.factory.ui.listWidget.addItem(item)

        # caso a mensagem recebida seja de um agente a lista de mensagens deste
        # agente é atualizada
        elif message.performative == ACLMessage.INFORM:

            display_message(
                self.factory.aid.name, 'Lista de Mensagens Recebida')

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
            self.show_messages(self.factory.agents_messages[agent])

    def onItemChanged(self, current, previous):
        for name, aid in self.factory.table.iteritems():
            if name in current.text() and not ('Sniffer' in name):
                message = ACLMessage(ACLMessage.REQUEST)
                message.set_sender(self.factory.aid)
                message.add_receiver(aid)
                message.set_content('Request messages history')

                self.factory.messages.append((aid, message))

                twisted.internet.reactor.connectTCP(
                    aid.host, aid.port, self.factory)
                break

    def show_messages(self, messages):
        """
            Este método exibe a lista de mensagens que estão em na lista de mensagens do agente selecionado
        """
        self.factory.ui.listWidget_2.clear()
        for message in messages:
            serifFont = QtGui.QFont(None, 10, QtGui.QFont.Bold)
            item = Item(message, serifFont)
            self.factory.ui.listWidget_2.addItem(item)

    def on_item_entered(self, item):

        gui = ControlACLMessageDialog()
        gui.ui.senderText.setText(item.message.sender.name)
        gui.ui.communicativeActComboBox.setCurrentIndex(
            gui.ui.communicativeActComboBox.findText(
                item.message.performative)
        )
        for receiver in item.message.receivers:
            gui.ui.receiverListWidget.addItem(receiver.name)
        try:
            gui.ui.contentText.setText(str(loads(item.message.content)))
        except:
            gui.ui.contentText.setText(str(item.message.content))

        gui.ui.protocolComboBox.setCurrentIndex(
            gui.ui.protocolComboBox.findText(
                item.message.protocol)
        )
        gui.ui.languageText.setText(item.message.language)
        gui.ui.encodingText.setText(item.message.encoding)
        gui.ui.ontologyText.setText(item.message.ontology)
        gui.ui.inReplyToText.setText(item.message.in_reply_to)
        gui.ui.replyWithText.setText(item.message.reply_with)
        gui.exec_()


class SnifferFactory(protocol.ClientFactory):

    """
        Classe SnifferFactory
        ---------------------

        Esta classe implementa o factory do protocolo do agente Sniffer
    """

    def __init__(self, aid, ams, ui):
        self.ui = ui    # instancia da interface grafica
        self.aid = aid  # identificação do agente
        self.ams = ams  # identificação do agente ams
        # armazena os agentes ativos, é um dicionário contendo chaves: nome e
        # valores: aid
        self.table = {}
        self.agents_messages = {}
        self.state = 'IDENT'
        self.messages = []  # armazena as mensagens a serem enviadas
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

#=========================================================================
# Metodos Utilitarios
#=========================================================================

AMS = {'name': 'localhost', 'port': 8000}
GUI = False


def display_message(name, data):
    """
        Metodo utilizado para exibicao de mensagens no console de comandos
    """
    date = datetime.now()
    date = date.strftime('%d/%m/%Y %H:%M:%S --> ')
    print '[' + name + '] ' + date + str(data)


def set_ams(name, port):
    """
        Metodo utilizado na inicialização do laço de execução do AMS 
    """
    global AMS

    AMS = {'name': name, 'port': port}

    amsFactory = AgentManagementFactory(port)
    twisted.internet.reactor.listenTCP(port, amsFactory)

    twisted.internet.reactor.callLater(
        5, amsFactory.protocol.connection_test_send)


def config_loop(gui=False):
    """
        Importa o elemento Qt4Reactor que integra o Loop do Twisted com o loop
        do Qt
    """
    global GUI
    GUI = gui

    if gui == False:
        try:
            from twisted.internet import reactor
        except:
            print 'Erro ao importar o modulo reactor'
    else:
        app = QtGui.QApplication(sys.argv)

        try:
            import qt4reactor
        except:
            print 'Erro ao importar o modulo qt4reactor'

        qt4reactor.install()


def start_loop(agents):
    """
        Lança o loop do twisted integrado com o loop do Qt se a opção GUI for
        verdadeira, se não lança o loop do Twisted
    """
    global AMS, GUI

    if GUI == True:
        controlAgentsGui = ControlAgentsGui()
        controlAgentsGui.show()

        # instancia um AID para o agente Sniffer
        aid = AID('Sniffer_Agent')
        # instancia um objeto Factory para o agente Sniffer
        snifferFactory = SnifferFactory(aid, AMS, controlAgentsGui.ui)
        # lança o agente como servidor na porta gerada pelo objeto AID
        twisted.internet.reactor.listenTCP(aid.port, snifferFactory)

    i = 0
    for agent in agents:
        i += 1
        twisted.internet.reactor.callLater(i, listen_agent, agent)

    # lança o loop do Twisted
    # twisted.internet.reactor.startRunning(init)
    twisted.internet.reactor.run()


def listen_agent(agent):
    # Conecta o agente ao AMS
    twisted.internet.reactor.connectTCP(
        agent.ams['name'], agent.ams['port'], agent.agentInstance)
    # Conecta o agente à porta que será utilizada para comunicação
    twisted.internet.reactor.listenTCP(agent.aid.port, agent.agentInstance)


def main():
    p = optparse.OptionParser()
    p.add_option('--port', '-p', default=8000)
    p.add_option('--gui', '-g', default=False)
    options, arguments = p.parse_args()

    config_loop(gui=bool(options.gui))
    set_ams('localhost', port=int(options.port))
    start_loop([])

if __name__ == '__main__':
    main()
