# -*- coding: utf-8 -*-

# Framework para Desenvolvimento de Agentes Inteligentes KajuPy

# Copyright (C) 2014  Lucas Silveira Melo

# Este arquivo é parte do programa KajuPy
#
# KajuPy é um software livre; você pode redistribuí-lo e/ou 
# modificá-lo dentro dos termos da Licença Pública Geral GNU como 
# publicada pela Fundação do Software Livre (FSF); na versão 3 da 
# Licença, ou (na sua opinião) qualquer versão.
#
# Este programa é distribuído na esperança de que possa ser  útil, 
# mas SEM NENHUMA GARANTIA; sem uma garantia implícita de ADEQUAÇÃO a qualquer
# MERCADO ou APLICAÇÃO EM PARTICULAR. Veja a
# Licença Pública Geral GNU para maiores detalhes.
#
# Você deve ter recebido uma cópia da Licença Pública Geral GNU
# junto com este programa, se não, escreva para a Fundação do Software
# Livre(FSF) Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

from twisted.internet import protocol, reactor

from pade.core.peer import PeerProtocol

from pade.misc.utility import display_message
from pade.acl.messages import ACLMessage
from pade.acl.aid import AID
from pade.gui.interface import ControlACLMessageDialog
from pickle import dumps, loads

from PySide import QtGui


class Sniffer(PeerProtocol):

    """
        Sniffer
        -------

        Esta classe implementa o agente Sniffer que tem o objetivo de
        enviar mensagens para os agentes ativos e exibir suas mensagens
        por meio de uma GUI.
        Protocolo do Agente GUI paramonitoramento dos agentes
        e das mensagens dos agentes
    """

    def __init__(self, fact):
        PeerProtocol.__init__(self, fact)
        # conecta o agente ao agente AMS
        reactor.connectTCP(self.fact.ams['name'],
                           self.fact.ams['port'],
                           self.fact)
        # configura os sinais da interface grafica
        self.fact.ui.listWidget.currentItemChanged.connect(
            self.onItemChanged)
        self.fact.ui.listWidget_2.itemPressed.connect(self.on_item_entered)

    def connectionMade(self):
        """
            Este método é executado sempre que uma conexão é executada entre
            um cliente e um servidor
        """

        # fase de identificação do agente com o AMS
        if self.fact.state == 'IDENT':
            # cria a mensagem de registro no AMS
            msg = ACLMessage()
            msg.add_receiver(
                AID(name='AMS' + '@' + self.fact.ams['name'] + ':' + str(self.fact.ams['port'])))
            msg.set_sender(self.fact.aid)
            msg.set_performative(ACLMessage.INFORM)
            msg.set_content(dumps(self.fact.aid))

            # envia a mensagem ao AMS
            self.fact.state = 'READY'
            self.sendLine(msg.get_message())
            self.transport.loseConnection()
        else:
            PeerProtocol.connectionMade(self)

    def connectionLost(self, reason):
        if self.message is not None:
            message = PeerProtocol.connectionLost(self, reason)

            agent = message.sender.name
            for i in self.fact.agents_messages:
                if agent == i:
                    messages = self.fact.agents_messages[i]
                    messages.extend(loads(message.content))
                    self.fact.agents_messages[i] = messages
                    break
            else:
                self.fact.agents_messages[agent] = loads(message.content)

            print self.fact.agents_messages[agent]
            self.show_messages(self.fact.agents_messages[agent])

            self.message = None

    def send_message(self, message):
        PeerProtocol.send_message(self, message)

    def lineReceived(self, line):
        """
            Este método é executado sempre que uma mesagem é recebida pelo agente Sniffer
        """

        # este método é executado caso a mensagem recebida tenha sido enviada pelo AMS
        # para atualização da tabela de agentes disponíveis
        if 'AMS' in line:

            message = ACLMessage()
            message.set_message(line)

            self.fact.ui.listWidget.clear()

            # loop for verifica se os agentes enviados na lista do AMS já estão
            # cadastrados na tabela do agente
            self.fact.table = loads(message.content)

            for agent in self.fact.table:
                serifFont = QtGui.QFont(None, 10, QtGui.QFont.Bold)
                item = QtGui.QListWidgetItem(str(agent) + '\n')
                item.setFont(serifFont)
                self.fact.ui.listWidget.addItem(item)

        # caso a mensagem recebida seja de um agente a lista de mensagens deste
        # agente é atualizada
        else:
            PeerProtocol.lineReceived(self, line)

    def onItemChanged(self, current, previous):
        for name, aid in self.fact.table.iteritems():
            if name in current.text() and not ('Sniffer' in name):
                message = ACLMessage(ACLMessage.REQUEST)
                message.set_sender(self.fact.aid)
                message.add_receiver(aid)
                message.set_content('Request messages history')

                self.fact.messages.append((aid, message))

                reactor.connectTCP(aid.host, aid.port, self.fact)
                break

    def show_messages(self, messages):
        """
            Este método exibe a lista de mensagens que estão em na lista de mensagens do agente selecionado
        """
        self.fact.ui.listWidget_2.clear()
        for message in messages:
            serifFont = QtGui.QFont(None, 10, QtGui.QFont.Bold)
            item = Item(message, serifFont)
            self.fact.ui.listWidget_2.addItem(item)

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
        self.debug = False
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
