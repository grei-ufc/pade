#! /usr/bin/python
# -*- coding: utf-8 -*-

from utils import startAMS, startLoop, displayMessage
from agent import Agent
from messages import ACLMessage

class helloWorld(Agent):
    
    def __init__(self, name, port):
        '''
            Inicializa a classe que implementa os comportamentos do agente
        '''
        Agent.__init__(self, name, port)
    
    def react(self, message):
        
        self.message = message
        
        if 'agent_1' in self.message.receivers:
            displayMessage(self.name, 'Recebida mensagem: ' + self.message.content)
            message = ACLMessage(ACLMessage.CONFIRM)
            message.setSender(self.name)
            message.addReceiver('agent_3')
            message.setContent('OK')
            displayMessage(self.name, 'Enviada mensagem: ' + self.message.content)
            self.send(message)
         
        if 'agent_3' in self.message.receivers:
            displayMessage(self.name, 'Recebida mensagem: ' + self.message.content)
        
    
    def onStart(self):
        if self.name == 'agent_3':
            message = ACLMessage(ACLMessage.INFORM)
            message.setSender(self.name)
            message.addReceiver('agent_1')
            message.setContent('51A PART')
            displayMessage(self.name, 'Enviada mensagem: ' + message.content)
            self.send(message)
            
# lista de agentes e as portas que serão utilizadas na comunicação
names = ['agent_1', 'agent_2', 'agent_3']
ports = [4000, 4001, 4002]

# porta que será utilizada para comunicação com o agente AMS
amsport = 8000

# configura os parametros do agente AMS
startAMS(amsport)

# instancia uma classe agente e configura os parametros dos agentes que seguem a classe
agents = {}
for name, port in zip(names, ports):
    agent = helloWorld(name, port)
    agent.setAMS('localhost', amsport)
    agent.start()
    agents[name] = agent
    
# inicializa o Sistema Multiagente em Rede
startLoop()