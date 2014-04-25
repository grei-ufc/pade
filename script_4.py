#! /usr/bin/python
# -*- coding: utf-8 -*-

from utils import setAMS, configLoop, startLoop, displayMessage
configLoop(gui=True)

from agent import Agent
from messages import ACLMessage
from protocols import FIPA_ContractNet_Protocol
from aid import AID
from pickle import dumps, loads

class InitiatorProtocol(FIPA_ContractNet_Protocol):
    
    def __init__(self, agent, message):
        super(InitiatorProtocol, self).__init__(agent, message, isInitiator=True)
        
        
    def handlePropose(self, message):
        FIPA_ContractNet_Protocol.handlePropose(self, message)
        displayMessage(self.agent.aid.name, loads(message.content))
    
    def handleRefuse(self, message):
        FIPA_ContractNet_Protocol.handleRefuse(self, message)
        displayMessage(self.agent.aid.name, loads(message.content))
        
    def handleAllProposes(self, proposes):
        FIPA_ContractNet_Protocol.handleAllProposes(self, proposes)
        
        displayMessage(self.agent.aid.name, 'Analisando Propostas...')
        better_propose = loads(proposes[0].content)
        better_propositor = proposes[0]
        for propose in proposes:
            power_value = loads(propose.content)
            if power_value['value'] > better_propose['value']:
                better_propose = power_value
                better_propositor = propose
        
        response_1 = better_propositor.createReply()
        response_1.setPerformative(ACLMessage.ACCEPT_PROPOSAL)
        response_1.setContent('Proposta ACEITA')
        self.agent.send(response_1)
        
        for propose in proposes:
            if propose != better_propositor:
                response = propose.createReply()
                response.setPerformative(ACLMessage.REJECT_PROPOSAL)
                response.setContent('Proposta RECUSADA')
                self.agent.send(response)
                
    
    def handleInform(self, message):
        FIPA_ContractNet_Protocol.handleInform(self, message)
        displayMessage(self.agent.aid.name, message.content)

class ParticipantProtocol(FIPA_ContractNet_Protocol):
    
    def __init__(self, agent, power_values):
        super(ParticipantProtocol,self).__init__(agent, isInitiator=False)
        self.power_values = power_values
    
    def handleCFP(self, message):
        FIPA_ContractNet_Protocol.handleCFP(self, message)
        
        displayMessage(self.agent.aid.name, loads(message.content))
        response = message.createReply()
        response.setPerformative(ACLMessage.PROPOSE)
        response.setContent(dumps(self.power_values))
        self.agent.send(response)
    
    def handleAcceptPropose(self, message):
        FIPA_ContractNet_Protocol.handleAcceptPropose(self, message)
        response = message.createReply()
        response.setPerformative(ACLMessage.INFORM)
        response.setContent('RECOMPOSICAO AUTORIZADA')
        self.agent.send(response)
        displayMessage(self.agent.aid.name, message.content)
    
    def handleRejectPropose(self, message):
        FIPA_ContractNet_Protocol.handleRejectPropose(self, message)
        displayMessage(self.agent.aid.name, message.content)

class InitiatorAgent(Agent):
    
    def __init__(self, aid):
        Agent.__init__(self, aid)
        
        pedido = {'tipo' : 'pedido', 'qtd' : 100.0}
        message = ACLMessage(ACLMessage.CFP)
        message.setProtocol(ACLMessage.FIPA_CONTRACT_NET_PROTOCOL)
        message.setContent(dumps(pedido))
        message.addReceiver('participant_agent_1')
        message.addReceiver('participant_agent_2')
        behaviour = InitiatorProtocol(self, message)
        self.addBehaviour(behaviour)

class ParticipantAgent(Agent):
    
    def __init__(self, aid, power_values):
        Agent.__init__(self, aid)
        behaviour = ParticipantProtocol(self, power_values)
        self.addBehaviour(behaviour)

if __name__ == '__main__':
    
    setAMS('localhost', 8000)
    
    agent_participant_1 = ParticipantAgent(AID('participant_agent_1'), {'value' : 100.0})
    agent_participant_1.setAMS('localhost', 8000)
    agent_participant_1.start()
    
    agent_participant_2 = ParticipantAgent(AID('participant_agent_2'), {'value' : 200.0})
    agent_participant_2.setAMS('localhost', 8000)
    agent_participant_2.start()
    
    agent_initiator = InitiatorAgent(AID('initiator_agent'))
    agent_initiator.setAMS('localhost', 8000)
    agent_initiator.start()
    
    startLoop()