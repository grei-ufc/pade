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
from pade.acl.aid import AID
from pade.misc.utility import display_message
from pickle import dumps, loads


class AttributeDescriptor(object):

    def __init__(self, instance):
        self.__attribute = None
        self.__instance = instance

    def __get__(self, instance, owner):
        return self.__attribute

    def __set__(self, instance, attribute):
        if isinstance(attribute, self.__instance):
            self.__attribute = attribute


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

        # fase 1 de identificação do agente com o AMS
        if self.fact.state == 'IDENT1':
            # cria a mensagem de registro no AMS
            msg = ACLMessage()
            msg.add_receiver(
                AID(
                    name='AMS' + '@' + self.fact.ams['name'] +
                    ':' + str(self.fact.ams['port'])
                ))
            msg.set_sender(self.fact.aid)
            msg.set_performative(ACLMessage.INFORM)
            msg.set_content(dumps(self.fact.aid))

            # envia a mensagem ao AMS e atualiza a flag de identificação para a
            # fase 2
            self.fact.state = 'IDENT2'
            self.send_message(msg.get_message())
        # se não é a fase de identificação 1 então o agente tenta enviar as mensagens presentes
        # na fila de envio representada pela variável self.fact.messages
        else:
            # captura o host conectado ao agente por meio do metodo
            # self.transport.getPeer()
            PeerProtocol.connectionMade(self)

    def connectionLost(self, reason):
        """Este método executa qualquer coisa quando uma conexão é perdida

        :param reason: Identifica o problema na perda de conexão
        """
        if self.message is not None:
            message = PeerProtocol.connectionLost(self, reason)

            # armazena a mensagem recebida
            self.fact.messages_history.append(message)
            self.fact.recent_message_history.append(message)

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

        # TODO: Melhorar o armazenamento e a troca deste tipo de mensagem
        # entre o agente e o agente Sniffer

        # fase 2 de identificação do agente com o AMS. Nesta fase o agente AMS retorna uma mensagem
        # ao agente com uma tabela de todos os agentes presentes na rede
        if self.fact.state == 'IDENT2' and 'AMS' in line:
            message = ACLMessage()
            message.set_message(line)

            self.fact.table = loads(message.content)

            if self.fact.debug:
                display_message(
                    self.fact.aid.name, 'Tabela atualizada: ' + str(self.fact.table.keys()))
            else:
                pass

            # alteração do estado de em fase de identificação
            # para pronto para receber mensagens
            self.fact.state = 'READY'
            self.fact.on_start()
            # self.transport.loseConnection()
        # caso o agente não esteja na fase 2 de identificação, então estará na fase
        # de recebimento de mensagens, e assim estará pronto para executar seus
        # comportamentos
        else:
            # este método é executado caso a mensagem recebida tenha sido enviada pelo AMS
            # para atualização da tabela de agentes disponíveis
            if 'AMS' in line:
                message = ACLMessage()
                message.set_message(line)
                self.fact.table = loads(message.content)
                if self.fact.debug:
                    display_message(
                        self.fact.aid.name, 'Tabela atualizada: ' + str(self.fact.table.keys()))
                else:
                    pass
                self.transport.loseConnection()
            # este método é executado caso a mensagem recebida tenha sido enviada pelo Agente Sniffer
            # que requisita a tabela de mensagens do agente
            elif 'Sniffer' in line:
                # se for a primeira mensagem recebida do agente Sniffer, então seu endereço, isto é nome
                # e porta, é armazenado na variável do tipo dicionário
                # self.fact.sniffer
                message = ACLMessage()
                message.set_message(line)
                if self.fact.sniffer == None:
                    self.fact.sniffer = {
                        'name': self.fact.ams['name'], 'port': message.sender.port}

                if self.fact.debug:
                    display_message(
                        self.fact.aid.name, 'Solicitação do Sniffer Recebida')
                else:
                    pass

                self.sniffer_message(message)
                self.transport.loseConnection()
            # recebe uma parte da mensagem enviada
            else:
                PeerProtocol.lineReceived(self, line)

    def sniffer_message(self, message):
        """Este método trata a mensagem enviada pelo agente Sniffer
        e cria uma mensagem de resposta ao agente Sniffer

        :param message: mensagem recebida pelo agente, enviada pelo
                  agente Sniffer
        """

        reply = message.create_reply()
        reply.set_performative(ACLMessage.INFORM)
        reply.set_sender(self.fact.aid)
        reply.set_content(dumps(self.fact.recent_message_history))
        self.fact.recent_message_history = []

        sniffer_aid = AID(name='Sniffer_Agent' + '@' + self.fact.sniffer[
                          'name'] + ':' + str(self.fact.sniffer['port']))
        self.fact.messages.append((sniffer_aid, reply))
        reactor.connectTCP(self.fact.sniffer['name'], int(
            self.fact.sniffer['port']), self.fact)


class AgentFactory(protocol.ClientFactory):

    """Esta classe implementa as ações e atributos do
    protocolo Agent sua principal função é armazenar
    informações importantes ao protocolo de comunicação
    do agente
    """

    def __init__(self, aid, ams, debug, react, on_start):
        self.aid = aid  # armazena a identificação do agente
        self.ams = ams  # armazena a identificação do agente ams
        self.sniffer = None  # armazena a identificação do agente sniffer
        self.messages = []  # armazena as mensagens a serem enviadas
        self.messages_history = []  # armazena as mensagens recebidas
        # armazena as cinco últimas mensagens recebidas
        self.recent_message_history = []
        # metodo que executa os comportamentos dos agentes definido pelo
        # usuario
        self.react = react
        # armazena os estados de execução do protocolo agente
        self.state = 'IDENT1'
        # metodo que executa ações definidas pelo usuario quando o agente é
        # iniciado
        self.on_start = on_start
        # armazena os agentes ativos, é um dicionário contendo chaves: nome e
        # valores: aid
        self.table = {}
        # instancia do protocolo agente
        self.debug = debug

        self.con = 0

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


class Agent(object):

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
        self.ams = {'name': 'localhost', 'port': 8000}
        self.agentInstance = AgentFactory(aid=self.aid, ams=self.__ams, debug=self.__debug,
                                          react=self.react, on_start=self.on_start)
        self.behaviours = []
        self.__messages = []

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

    def react(self, message):
        """Este metodo deve ser SobreEscrito e será
        executado todas as vezes que o agente em
        questão receber algum tipo de dado

        :param message: ACLMessage
            mensagem recebida
        """
        # este for executa todos os protocolos FIPA associados a comportmentos
        # implementados neste agente
        for behaviour in self.behaviours:
            behaviour.execute(message)

    def send(self, message):
        """Envia uma mensagem ACL para os agentes
        especificados no campo receivers da mensagem ACL
        """
        message.set_sender(self.aid)
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
            if 'Sniffer_Agent' not in agent_aid.localname:
                message.add_receiver(agent_aid)

        self.send(message)

    def add_all(self, message):
        for agent_aid in self.agentInstance.table.values():
            if 'Sniffer_Agent' not in agent_aid.localname:
                message.add_receiver(agent_aid)

    def on_start(self):
        """Metodo que definine os comportamentos
        iniciais de um agente
        """
        # Este for adiciona os comportametos padronizados especificados pelo
        # usuário
        for behaviour in self.behaviours:
            behaviour.on_start()
