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

#import sys
#sys.path.insert(1, '..')

from twisted.internet import protocol, reactor
from twisted.protocols.basic import LineReceiver

from pade.misc.utility import display_message
from pade.acl.messages import ACLMessage
from pade.acl.aid import AID
from pade.gui.interface import ControlACLMessageDialog
from pickle import dumps, loads

from PySide import QtGui

class Sniffer(LineReceiver):

    """
        Sniffer
        -------

        Esta classe implementa o agente Sniffer que tem o objetivo de 
        enviar mensagens para os agentes ativos e exibir suas mensagens
        por meio de uma GUI.
        Protocolo do Agente GUI paramonitoramento dos agentes
        e das mensagens dos agentes
    """

    # MAX_LENGTH = 62768
    message = None

    def __init__(self, factory):
        self.factory = factory
        # conecta o agente ao agente AMS
        reactor.connectTCP(self.factory.ams['name'], 
                           self.factory.ams['port'],
                           self.factory)
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
                    self.send_message(message[1].get_message())
                    self.factory.messages.remove(message)
                    break

    def connectionLost(self, reason):
        if self.message is not None:
            print 'Mensagem recebida!'
            print self.message
            message = ACLMessage()
            message.set_message(self.message)

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

            self.message = None

    def lineLengthExceeded(self, line):
        print 'A mensagem e muito grande!!!'
        return LineReceiver.lineLengthExceeded(self, line)

    def send_message(self, message):
        l = len(message)
        if l > 14384:

            while len(message) > 0:
                message, m = message[14384:], message[:14384]
                print 'enviando mensagem...'
                self.sendLine(m)
        else:
            self.sendLine(message)
        self.transport.loseConnection()

    def lineReceived(self, line):
        """
            Este método é executado sempre que uma mesagem é recebida pelo agente Sniffer
        """

        # este método é executado caso a mensagem recebida tenha sido enviada pelo AMS
        # para atualização da tabela de agentes disponíveis
        if 'AMS' in line:

            message = ACLMessage()
            message.set_message(line)

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
        else:
            # recebe uma parte da mensagem enviada
            print 'Recebendo mensagem...'
            if self.message is not None:
                self.message += line
            else:
                self.message = line

    def onItemChanged(self, current, previous):
        for name, aid in self.factory.table.iteritems():
            if name in current.text() and not ('Sniffer' in name):
                message = ACLMessage(ACLMessage.REQUEST)
                message.set_sender(self.factory.aid)
                message.add_receiver(aid)
                message.set_content('Request messages history')

                self.factory.messages.append((aid, message))

                reactor.connectTCP(aid.host, aid.port, self.factory)
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