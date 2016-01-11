#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Framework para Desenvolvimento de Agentes Inteligentes PADE

# The MIT License (MIT)

# Copyright (c) 2015 Lucas S Melo

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.


"""
 Módulo de Implementação de agentes
 ----------------------------------

 Este módulo Python faz parte da infraestrutura de comunicação
 e gerenciamento de agentes que compõem o framework para construção
 de agentes inteligentes implementado com base na biblioteca para
 implementação de sistemas distribuídos em Python Twisted

 @author: Lucas S Melo
"""

from twisted.internet import protocol, reactor
from twisted.protocols.basic import LineReceiver

from pade.core.peer import PeerProtocol

from pade.acl.messages import ACLMessage
from pade.behaviours.protocols import Behaviour
from pade.behaviours.protocols import FipaRequestProtocol, FipaSubscribeProtocol
from pade.acl.aid import AID
from pade.misc.utility import display_message
from pickle import dumps, loads


class AgentProtocol(PeerProtocol):

    """Esta classe implementa o protocolo que será seguido pelos
        agentes no processo de comunicação. Esta classe modela os
        atos de comunicação entre agente e agente AMS, agente e
        agente Sniffer e entre agentes.

        Esta classe não armazena informações permanentes, sendo
        esta função delegada à classe AgentFactory
    """

    def __init__(self, fact):
        """Inicializa os atributos da classe

        :param fact: instancia fact do protocolo a ser inplementado
        """

        self.fact = fact

    def connectionMade(self):
        """Este método é executado sempre que uma
        conexão é executada entre um agente no modo
        cliente e um agente no modo servidor
        """
        PeerProtocol.connectionMade(self)

    def connectionLost(self, reason):
        """Este método executa qualquer coisa quando uma conexão é perdida

        :param reason: Identifica o problema na perda de conexão
        """
        if self.message is not None:
            message = PeerProtocol.connectionLost(self, reason)

            # execução do comportamento Agent.react à mensagem
            # recebida
            self.message = None
            self.fact.react(message)

    def send_message(self, message):
        PeerProtocol.send_message(self, message)

    def lineReceived(self, line):
        """Este método é executado sempre que uma
        nova mensagem é recebida pelo agente,
        tanto no modo cliente quanto no modo servidor

        :param line: mensagem recebida pelo agente
        """
        PeerProtocol.lineReceived(self, line)

class AgentFactory(protocol.ClientFactory):

    """Esta classe implementa as ações e atributos do
    protocolo Agent sua principal função é armazenar
    informações importantes ao protocolo de comunicação
    do agente
    """

    def __init__(self, aid, ams, debug, react, on_start):
        self.aid = aid  # armazena a identificação do agente
        self.ams = ams  # armazena a identificação do agente ams

        self.messages = []  # armazena as mensagens a serem enviadas

        # metodo que executa os comportamentos dos agentes definido tanto
        # pelo usuario quanto pelo System-PADE
        self.react = react
        # metodo que executa os comportamentos dos agentes definidos tanto 
        # pelo usuario quanto pelo System-PADE quando o agente é iniciado
        self.on_start = on_start
        # AID do AMS
        self.ams_aid = AID('ams@' + ams['name'] + ':' + str(ams['port']))
        # table armazena os agentes ativos, um dicionário com chaves: nome e
        # valores: AID
        self.table = dict([('ams', self.ams_aid)])
        
        self.debug = debug

    def buildProtocol(self, addr):
        """Este metodo inicializa o protocolo Agent
        """
        return AgentProtocol(self)

    def clientConnectionFailed(self, connector, reason):
        """Este método é chamado quando ocorre uma
        falha na conexão de um cliente com o servidor
        """
        if self.debug:
            display_message(self.aid.name, 'Falha na Conexão')
        else:
            pass

        reactor.stop()

    def clientConnectionLost(self, connector, reason):
        """Este método chamado quando a conexão de
        um cliente com um servidor é perdida
        """
        pass


# Classe Primitiva Agent_

class Agent_(object):

    """A classe Agente estabelece as funcionalidades essenciais de um agente como:
    1. Conexão com o AMS
    2. Configurações iniciais
    3. Envio de mensagens
    4. Adição de comportamentos
    5. metodo abstrato a ser utilizado na implementação dos comportamentos iniciais
    6. metodo abstrato a ser utlizado na implementação dos comportamentos dos agentes quando recebem uma mensagem
    """

    def __init__(self, aid, debug=False):

        self.aid = aid
        self.debug = debug
        # TODO: criar um objeto aid com o aid do ams 
        self.ams = {'name': 'localhost', 'port': 8000}
        self.agentInstance = AgentFactory(aid=self.aid, ams=self.__ams, debug=self.__debug,
                                          react=self.react, on_start=self.on_start)
        self.behaviours = list()
        self.system_behaviours = list()
        self.__messages = list()

    @property
    def aid(self):
        return self.__aid

    @aid.setter
    def aid(self, value):
        if isinstance(value, AID):
            self.__aid = value
        else:
            raise ValueError('O objeto aid precisa ser do tipo AID!')

    @property
    def debug(self):
        return self.__debug

    @debug.setter
    def debug(self, value):
        if isinstance(value, bool):
            self.__debug = value
        else:
            raise ValueError('O objeto debug precisa ser do tipo bool')

    @property
    def ams(self):
        return self.__ams

    @ams.setter
    def ams(self, value):
        self.__ams = dict()
        if value == {}:
            self.__ams['name'] = 'localhost'
            self.__ams['port'] = 8000
        else:
            try:
                self.__ams['name'] = value['name']
                self.__ams['port'] = value['port']
            except Exception, e:
                raise e

    @property
    def agentInstance(self):
        return self.__agentInstance

    @agentInstance.setter
    def agentInstance(self, value):
        if isinstance(value, AgentFactory):
            self.__agentInstance = value
        else:
            raise ValueError(
                'O objeto agentInstance precisa ser do tipo AgentFactory')

    @property
    def behaviours(self):
        return self.__behaviours

    @behaviours.setter
    def behaviours(self, value):
        for v in value:
            if not issubclass(v.__class__, Behaviour):
                raise ValueError(
                    'O objeto behaviour presiza ser subclasse da classe Behaviour!')
        else:
            self.__behaviours = value

    @property
    def system_behaviours(self):
        return self.__system_behaviours

    @system_behaviours.setter
    def system_behaviours(self, value):
        for v in value:
            if not issubclass(v.__class__, Behaviour):
                raise ValueError(
                    'O objeto behaviour presiza ser subclasse da classe Behaviour!')
        else:
            self.__system_behaviours = value

    def react(self, message):
        """Este metodo deve ser SobreEscrito e será
        executado todas as vezes que o agente em
        questão receber algum tipo de dado

        :param message: ACLMessage
            mensagem recebida
        """
        # este for executa todos os protocolos FIPA associados a comportmentos
        # implementados neste agente
        if message.system_message:
            for system_behaviour in self.system_behaviours:
                system_behaviour.execute(message)
        else:
            for behaviour in self.behaviours:
                behaviour.execute(message)

    def send(self, message):
        """Envia uma mensagem ACL para os agentes
        especificados no campo receivers da mensagem ACL
        """
        message.set_sender(self.aid)
        message.set_message_id()
        message.set_datetime_now()

        # for percorre os destinatarios da mensagem
        for receiver in message.receivers:
            for name in self.agentInstance.table:
                # if verifica se o nome do destinatario está entre os agentes
                # disponíveis
                if receiver.localname in name and receiver.localname != self.aid.localname:
                    # corrige o parametro porta e host gerado aleatoriamente quando apenas um nome
                    # e dado como identificador de um destinatário
                    receiver.setPort(self.agentInstance.table[name].port)
                    receiver.setHost(self.agentInstance.table[name].host)
                    # se conecta ao agente e envia a mensagem
                    self.agentInstance.messages.append((receiver, message))
                    reactor.connectTCP(self.agentInstance.table[
                                       name].host, self.agentInstance.table[name].port, self.agentInstance)
                    break
            else:
                if self.debug:
                    display_message(
                        self.aid.localname, 'Agente ' + receiver.name + ' não esta ativo')
                else:
                    pass

    def call_later(self, time, metodo, *args):
        return reactor.callLater(time, metodo, *args)

    def send_to_all(self, message):
        """Envia mensagem de broadcast, ou seja envia mensagem
        para todos os agentes com registro na tabela de agentes

        :param message: mensagem a ser enviada a todos
        os agentes registrados na tabela do agente
        """

        for agent_aid in self.agentInstance.table.values():
                message.add_receiver(agent_aid)

        self.send(message)

    def add_all(self, message):
        message.receivers = list()
        for agent_aid in self.agentInstance.table.values():
            if 'ams' not in agent_aid.localname:
                message.add_receiver(agent_aid)

    def on_start(self):
        """Metodo que definine os comportamentos
        iniciais de um agente
        """
        # Este for adiciona os comportametos padronizados especificados pelo
        # usuário
        for behaviour in self.behaviours:
            behaviour.on_start()
        for system_behaviour in self.system_behaviours:
            system_behaviour.on_start()

# Comportamentos PADE que compõem a classe Agent

class SubscribeBehaviour(FipaSubscribeProtocol):
    def __init__(self, agent, message):
        super(SubscribeBehaviour, self).__init__(agent,
                                                 message,
                                                 is_initiator=True)

    def handle_agree(self, message):
        display_message(self.agent.aid.name, 'Processo de identificação concluído.')

    def handle_refuse(self, message):
        display_message(self.agent.aid.name, message.content)

    def handle_inform(self, message):
        display_message(self.agent.aid.name, 'Atualizacao de tabela')
        self.agent.agentInstance.table = loads(message.content)


class CompConnection(FipaRequestProtocol):
    """Comportamento FIPA Request
    do agente Horario"""
    def __init__(self, agent):
        super(CompConnection, self).__init__(agent=agent,
                                             message=None,
                                             is_initiator=False)

    def handle_request(self, message):
        super(CompConnection, self).handle_request(message)
        display_message(self.agent.aid.localname, 'mensagem request recebida')
        reply = message.create_reply()
        reply.set_performative(ACLMessage.INFORM)
        reply.set_content('Im Live')
        self.agent.send(reply)


# Classe principal Agent

class Agent(Agent_):
    def __init__(self, aid, debug=False):
        super(Agent, self).__init__(aid=aid, debug=debug)

        message = ACLMessage(ACLMessage.SUBSCRIBE)
        message.set_protocol(ACLMessage.FIPA_SUBSCRIBE_PROTOCOL)
        ams_aid = AID('ams@' + self.ams['name'] + ':' + str(self.ams['port']))
        message.add_receiver(ams_aid)
        message.set_content('IDENT')
        message.set_system_message(is_system_message=True)

        self.comport_ident = SubscribeBehaviour(self, message)
        self.comport_connection = CompConnection(self)

        self.system_behaviours.append(self.comport_ident)
        self.system_behaviours.append(self.comport_connection)

    def react(self, message):
        super(Agent, self).react(message)

        # envia mensagem recebida para o AMS
        # montagem da mensagem a ser enviada ao AMS
        _message = ACLMessage(ACLMessage.INFORM)
        ams_aid = AID('ams@' + self.ams['name'] + ':' + str(self.ams['port']))
        _message.add_receiver(ams_aid)
        _message.set_content(dumps({
        'ref' : 'MESSAGE',
        'message' : message}))
        _message.set_system_message(is_system_message=True)
        self.send(_message)
        print 'mensagem enviada para ams'
        # fim da montagem da mensagem