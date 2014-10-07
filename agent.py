#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
 Módulo de Implementação de agentes
 ----------------------------------

 Este módulo Python faz parte da infraestrutura de comunicação 
 e gerenciamento de agentes que compõem o framework para construção 
 de agentes inteligentes implementado com base na biblioteca para 
 implementação de sistemas distribuídos em Python Twisted

 @author: lucas
"""

from twisted.internet import protocol, reactor
from twisted.protocols.basic import LineReceiver
from messages import ACLMessage
from protocols import Behaviour
from aid import AID
from utils import display_message
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


class AgentProtocol(LineReceiver):

    """
        Classe AgentProtocol
        --------------------

        Esta classe implementa o protocolo que será seguido pelos 
        agentes no processo de comunicação. Esta classe modela os
        atos de comunicação entre agente e agente AMS, agente e 
        agente Sniffer e entre agentes.

        Esta classe não armazena informações permanentes, sendo 
        esta função delegada à classe AgentFactory
    """
    MAX_LENGTH = 32768

    def __init__(self, factory):
        """
            Método de inicializacao da classe AgentProtocol
            -----------------------------------------------

            Inicializa os atributos da classe

            Parâmetros
            ----------
            factory : instancia factory do protocolo a ser inplementado
        """

        self.factory = factory
        # esta variavel é setada para a fase de identificação 1
        self.factory.state = 'IDENT1'

    def connectionMade(self):
        """
            connectionMade
            --------------

            Este método é executado sempre que uma conexão é executada entre 
            um agente no modo cliente e um agente no modo servidor
        """

        # fase 1 de identificação do agente com o AMS
        if self.factory.state == 'IDENT1':
            # cria a mensagem de registro no AMS
            msg = ACLMessage()
            msg.add_receiver(
                AID(
                    name='AMS' + '@' + self.factory.ams['name'] +
                    ':' + str(self.factory.ams['port'])
                    ))
            msg.set_sender(self.factory.aid)
            msg.set_performative(ACLMessage.INFORM)
            msg.set_content(dumps(self.factory.aid))

            # envia a mensagem ao AMS e atualiza a flag de identificação para a
            # fase 2
            self.factory.state = 'IDENT2'
            self.sendLine(msg.get_message())
            self.transport.loseConnection()

        # se não é a fase de identificação 1 então o agente tenta enviar as mensagens presentes
        # na fila de envio representada pela variável self.factory.messages
        else:
            # captura o host conectado ao agente por meio do metodo
            # self.transport.getPeer()
            peer = self.transport.getPeer()
            display_message(
                self.factory.aid.name, 'Conexao estabelecida com ' + str(peer.port))

            sended_message = None
            # for percorre a lista de mensagens para serem enviadas
            for message in self.factory.messages:
                if int(message[0].port) == int(peer.port):
                    try:
                        self.sendLine(message[1].get_message())
                        sended_message = message
                    except:
                        print 'Erro no envio da mensagem'
                    break
            # Se alguma mensagem foi enviada, o agente, que está
            # no modo cliente, encerra a conexão. Isto é verificado na variável
            # sended_message
            if sended_message != None:
                self.factory.messages.remove(sended_message)
                self.transport.loseConnection()

    def connectionLost(self, reason):
        """
            connectionLost
            --------------

            Este método executa qualquer coisa quando uma conexão é perdida

            Parâmetros
            ----------
            reason: Identifica o problema na perda de conexão
        """
        pass

    def lineLengthExceeded(self, line):
        """
            lineLengthExceeded
            ------------------

            Este método exibi um aviso quando uma mensagem muito grande é recebida
        """
        display_message(self.factory.aid.name,
                        'A mensagem excedeu o tamanho máximo!')

    def lineReceived(self, line):
        """
            lineReceived
            ------------

            Este método é executado sempre que uma 
            nova mensagem é recebida pelo agente, tanto no modo cliente 
            quanto no modo servidor

            Parâmetros
            ----------
            line : mensagem recebida pelo agente

        """

        # Intancia um objeto mensagem com os dados recebidos
        message = ACLMessage()
        message.set_message(line)

        display_message(self.factory.aid.name,
                        'Mensagem recebida de: ' + str(message.sender.name))

        # TODO: Melhorar o armazenamento e a troca deste tipo de mensagem
        # entre o agente e o agente Sniffer

        # armazena a mensagem recebida
        self.factory.messages_history.append(message)
        self.factory.recent_message_history.append(message)

        # fase 2 de identificação do agente com o AMS. Nesta fase o agente AMS retorna uma mensagem
        # ao agente com uma tabela de todos os agentes presentes na rede
        if self.factory.state == 'IDENT2' and 'AMS' in message.sender.name:
            self.factory.table = loads(message.content)
            display_message(
                self.factory.aid.name, 'Tabela atualizada: ' + str(self.factory.table.keys()))
            # alteração do estado de em fase de identificação
            # para pronto para receber mensagens
            self.factory.state = 'READY'
            self.factory.on_start()
        # caso o agente não esteja na fase 2 de identificação, então estará na fase
        # de recebimento de mensagens, e assim estará pronto para executar seus
        # comportamentos
        else:
            # este método é executado caso a mensagem recebida tenha sido enviada pelo AMS
            # para atualização da tabela de agentes disponíveis
            if 'AMS' in message.sender.name:
                self.factory.table = loads(message.content)
                display_message(
                    self.factory.aid.name, 'Tabela atualizada: ' + str(self.factory.table.keys()))

            # este método é executado caso a mensagem recebida tenha sido enviada pelo Agente Sniffer
            # que requisita a tabela de mensagens do agente
            elif 'Sniffer' in message.sender.name:
                # se for a primeira mensagem recebida do agente Sniffer, então seu endereço, isto é nome
                # e porta, é armazenado na variável do tipo dicionário
                # self.factory.sniffer
                if self.factory.sniffer == None:
                    self.factory.sniffer = {
                        'name': self.factory.ams['name'], 'port': message.sender.port}
                display_message(
                    self.factory.aid.name, 'Solicitação do Sniffer Recebida')
                self.sniffer_message(message)

            # senão o agente trata a mensagem através de seu método react()
            else:
                self.factory.react(message)

    def sniffer_message(self, message):
        """
            sniffer_message
            --------------

            Este método trata a mensagem enviada pelo agente Sniffer
            e cria uma mensagem de resposta ao agente Sniffer

            Parâmetros
            ----------
            message : mensagem recebida pelo agente, enviada pelo
                      agente Sniffer
        """

        reply = message.create_reply()
        reply.set_performative(ACLMessage.INFORM)
        reply.set_sender(self.factory.aid)
        reply.set_content(dumps(self.factory.recent_message_history))
        self.factory.recent_message_history = []

        sniffer_aid = AID(name='Sniffer_Agent' + '@' + self.factory.sniffer[
                          'name'] + ':' + str(self.factory.sniffer['port']))
        self.factory.messages.append((sniffer_aid, reply))
        reactor.connectTCP(self.factory.sniffer['name'], int(
            self.factory.sniffer['port']), self.factory)


class AgentFactory(protocol.ClientFactory):

    """
        AgentFactory
        ------------

        Esta classe implementa as ações e atributos do protocolo Agent
        sua principal função é armazenar informações importantes ao 
        protocolo de comunicação  do agente
    """

    def __init__(self, aid, ams, react=None, on_start=None):
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
        self.state = 'IDENT'
        # metodo que executa ações definidas pelo usuario quando o agente é
        # iniciado
        self.on_start = on_start
        # armazena os agentes ativos, é um dicionário contendo chaves: nome e
        # valores: aid
        self.table = {}
        # instancia do protocolo agente
        self.agentProtocol = AgentProtocol(self)

    def buildProtocol(self, addr):
        """
            buildProtocol
            -------------

            Este metodo inicializa o protocolo Agent
        """
        return self.agentProtocol

    def clientConnectionFailed(self, connector, reason):
        """
            clientConnectionFailed
            ----------------------

            Este método é chamado quando ocorre uma falha na conexão de um cliente com o servidor 
        """
        display_message(self.aid.name, 'Falha na Conexão')
        reactor.stop()

    def clientConnectionLost(self, connector, reason):
        """
            clientConnectionLost
            --------------------

            Este método chamado quando a conexão de um cliente com um servidor é perdida
        """
        pass


class Agent(object):

    """
        Classe Agente
        -------------

        A classe Agente estabelece as funcionalidades essenciais de um agente como:
        1. Conexão com o AMS
        2. Configurações iniciais
        3. Envio de mensagens
        4. Adição de comportamentos
        5. metodo abstrato a ser utilizado na implementação dos comportamentos iniciais 
        6. metodo abstrato a ser utlizado na implementação dos comportamentos dos agentes quando recebem uma mensagem
    """

    def __init__(self, aid):

        self.aid = aid
        self.ams = {'name': 'localhost', 'port': 8000}
        self.agentInstance = AgentFactory(self.aid, self.__ams,
                                          self.react, self.on_start)
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

        self.__agentInstance = AgentFactory(self.aid,
                                            self.__ams,
                                            self.react,
                                            self.on_start)

    @property
    def agentInstance(self):
        return self.__agentInstance

    @agentInstance.setter
    def agentInstance(self, value):
        if isinstance(value, AgentFactory):
            self.__agentInstance = AgentFactory(self.aid, self.__ams,
                                                self.react, self.on_start)
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
        """
            react
            -----

            Este metodo deve ser SobreEscrito e será executado todas as vezes que
            o agente em questão receber algum tipo de dado
        """
        # este for executa todos os protocolos FIPA associados a comportmentos
        # implementados neste agente
        for behaviour in self.behaviours:
            behaviour.execute(message)

    def send(self, message):
        """
            send
            ----

            Envia uma mensagem ACL para os agentes especificados no campo receivers da mensagem ACL
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
                    receiver.port = self.agentInstance.table[name].port
                    receiver.host = self.agentInstance.table[name].host
                    # se conecta ao agente e envia a mensagem
                    self.agentInstance.messages.append((receiver, message))
                    reactor.connectTCP(self.agentInstance.table[
                                       name].host, self.agentInstance.table[name].port, self.agentInstance)
                    break
            else:
                display_message(
                    self.aid.localname, 'Agente ' + receiver.name + ' não esta ativo')

    def on_start(self):
        """
            on_start
            --------

            Metodo que definine os comportamentos iniciais de um agente
        """
        # Este for adiciona os comportametos padronizados especificados pelo
        # usuário
        for behaviour in self.behaviours:
            behaviour.on_start()
