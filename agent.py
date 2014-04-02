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
            # envia as mensagens que estão na fila de mensagens da lista self.factory.mensagens, se houver mensagens
            if self.factory.messages != []:
                message = self.factory.messages.pop(0)
                self.sendLine(message.getMsg())
            
    def lineReceived(self, line):
        '''
            Este método é executado sempre que uma 
            nova mensagem é recebida pelo cliente ou pelo servidor
        '''
        
        # fase de identificação do agente com o AMS
        if self.state == 'IDENT':
            message = ACLMessage()
            message.setMsg(line)
            self.factory.table = loads(message.content)
            displayMessage(self.factory.aid.name, 'tabela atualizada: ' + str(self.factory.table.keys()))
            # alteração do estado para pronto para receber mensagens 
            self.state = 'READY'
            self.factory.onStart()
        # fase de recebimento de mensagens, o agente está printo para executar seus comportamentos
        else:
            message = ACLMessage()
            message.setMsg(line)
            # este método é executado caso a mensagem recebida tenha sido enviada pelo AMS
            # para atualização da tabela de agentes disponíveis
            if 'AMS' in message.sender.name:
                self.factory.table = loads(message.content)
                displayMessage(self.factory.aid.name, 'tabela atualizada: ' + str(self.factory.table.keys()))
            # senão o agente trata a mensagem através de seu método react()
            else:
                self.factory.react(message)
        
    def connectionLost(self, reason):
        displayMessage(self.factory.aid.name,'Perda de Conexão')

class AgentFactory(protocol.ClientFactory):
    '''
        Esta classe implementa as ações e atributos do protocolo Agent
        Tem função de armazenar informações importantes ao protocolo
    '''
    def __init__(self, aid, ams, react=None, onStart=None):
        self.aid = aid # identificação do agente
        self.ams = ams # identificação do agente ams
        self.messages = [] # @TODO armazena as mensagens recebidas
        self.react = react # metodo que executa os comportamentos dos agentes definido pelo usuario
        self.onStart = onStart # metodo que executa ações definidas pelo usuario quando o agente é iniciado
        self.table = {} # armazena os agentes ativos, é um dicionário contendo chaves: nome e valores: aid 
        self.agentProtocol = AgentProtocol(self) # instancia do protocolo agente
        
    def buildProtocol(self, addr):
        '''
            Este metodo inicializa o protocolo Agent
        '''
        return self.agentProtocol
    
    def clientConnectionFailed(self, connector, reason):
        '''
            Este método é chamado quando ocorre uma falha na conexão de um cliente com o servidor 
        '''
        displayMessage(self.aid.name, 'Falha na Conexão')
        reactor.stop()
    
    def clientConnectionLost(self, connector, reason):
        '''
            Este método chamado quando a conexão de um cliente com um servidor é perdida
        '''
        displayMessage(self.aid.name, 'Perda de Conexão')
        reactor.stop()
    
    def startedConnecting(self, connector):
        pass
    
        
#=================================
# Agent Class
#=================================
class Agent():
    '''
        A classe Agente estabelece as funcionalidades essenciais de um agente como:
        - Conexão com o AMS
        - Configurações iniciais
        - Envio de mensagens
        - Adição de comportamentos
        - metodo abstrato a ser utilizado na implementação dos comportamentos iniciais 
        - metodo abstrato a ser utlizado na implementação dos comportamentos dos agentes quando recebem uma mensagem
    '''
    def __init__(self, aid):
        self.aid = aid
        self.ams = {}
        self.agentInstance = None
        self.behaviours = []
        self.messages = []
        
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
        for behaviour in self.behaviours:
            behaviour.execute(message)
    
    def send(self, message):
        '''
            Envia uma mensagem ACL para os agentes especificados no campo receivers da mensagem ACL
        '''
        message.setSender(self.aid)
        # for percorre os destinatarios da mensagem
        for receiver in message.receivers:
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
        '''
            Metodo que definine os comportamentos iniciais de um agente
        '''
        # Este for adiciona os comportametos padronizados especificados pelo usuário
        for behaviour in self.behaviours:
            behaviour.onStart()
    
    def getBehaviours(self):
        '''
            Retorna os comportamentos padronizados do agente
        '''
        return self.behaviours
    
    def addBehaviour(self, behaviour):
        '''
            Adiciona um comportamento padronizado ao agente
        '''
        reactor.callInThread(behaviour.timedBehaviour)
        self.behaviours.append(behaviour)