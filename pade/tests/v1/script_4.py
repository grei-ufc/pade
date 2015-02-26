#! /usr/bin/python
# -*- coding: utf-8 -*-

from utils import set_ams, config_loop, start_loop, display_message
config_loop(gui=True)

from agent import Agent
from messages import ACLMessage
from protocols import FipaContractNetProtocol
from aid import AID
from pickle import dumps, loads

class InitiatorProtocol(FipaContractNetProtocol):
    
    def __init__(self, agent, message):
        super(InitiatorProtocol, self).__init__(agent, message, is_initiator=True)
        
        
    def handle_propose(self, message):
        FipaContractNetProtocol.handle_propose(self, message)
        display_message(self.agent.aid.name, loads(message.content))
    
    def handle_refuse(self, message):
        FipaContractNetProtocol.handle_refuse(self, message)
        display_message(self.agent.aid.name, loads(message.content))
        
    def handle_all_proposes(self, proposes):
        FipaContractNetProtocol.handle_all_proposes(self, proposes)
        
        display_message(self.agent.aid.name, 'Analisando Propostas...')
        better_propose = loads(proposes[0].content)
        better_propositor = proposes[0]
        for propose in proposes:
            power_value = loads(propose.content)
            if power_value['value'] > better_propose['value']:
                better_propose = power_value
                better_propositor = propose
        
        response_1 = better_propositor.create_reply()
        response_1.set_performative(ACLMessage.ACCEPT_PROPOSAL)
        response_1.set_content('Proposta ACEITA')
        self.agent.send(response_1)
        
        for propose in proposes:
            if propose != better_propositor:
                response = propose.create_reply()
                response.set_performative(ACLMessage.REJECT_PROPOSAL)
                response.set_content('Proposta RECUSADA')
                self.agent.send(response)
                
    
    def handle_inform(self, message):
        FipaContractNetProtocol.handle_inform(self, message)
        display_message(self.agent.aid.name, message.content)

class ParticipantProtocol(FipaContractNetProtocol):
    
    def __init__(self, agent, power_values):
        super(ParticipantProtocol,self).__init__(agent, is_initiator=False)
        self.power_values = power_values
    
    def handle_cfp(self, message):
        FipaContractNetProtocol.handle_cfp(self, message)
        
        display_message(self.agent.aid.name, loads(message.content))
        response = message.create_reply()
        response.set_performative(ACLMessage.PROPOSE)
        response.set_content(dumps(self.power_values))
        self.agent.send(response)
    
    def handle_accept_propose(self, message):
        FipaContractNetProtocol.handle_accept_propose(self, message)
        response = message.create_reply()
        response.set_performative(ACLMessage.INFORM)
        response.set_content('RECOMPOSICAO AUTORIZADA')
        self.agent.send(response)
        display_message(self.agent.aid.name, message.content)
    
    def handle_reject_proposes(self, message):
        FipaContractNetProtocol.handle_reject_proposes(self, message)
        display_message(self.agent.aid.name, message.content)

class InitiatorAgent(Agent):
    
    def __init__(self, aid):
        Agent.__init__(self, aid)
        
        pedido = {'tipo' : 'pedido', 'qtd' : 100.0}
        message = ACLMessage(ACLMessage.CFP)
        message.set_protocol(ACLMessage.FIPA_CONTRACT_NET_PROTOCOL)
        message.set_content(dumps(pedido))
        message.add_receiver('participant_agent_1')
        message.add_receiver('participant_agent_2')
        behaviour = InitiatorProtocol(self, message)
        self.addBehaviour(behaviour)

class ParticipantAgent(Agent):
    
    def __init__(self, aid, power_values):
        Agent.__init__(self, aid)
        behaviour = ParticipantProtocol(self, power_values)
        self.addBehaviour(behaviour)

if __name__ == '__main__':
    
    set_ams('localhost', 8000)
    
    agent_participant_1 = ParticipantAgent(AID('participant_agent_1'), {'value' : 100.0})
    agent_participant_1.set_ams('localhost', 8000)
    agent_participant_1.start()
    
    agent_participant_2 = ParticipantAgent(AID('participant_agent_2'), {'value' : 200.0})
    agent_participant_2.set_ams('localhost', 8000)
    agent_participant_2.start()
    
    agent_initiator = InitiatorAgent(AID('initiator_agent'))
    agent_initiator.set_ams('localhost', 8000)
    agent_initiator.start()
    
    start_loop()