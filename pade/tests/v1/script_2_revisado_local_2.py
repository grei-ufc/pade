# -*- encoding: utf-8 -*-

from utils import display_message, set_ams, start_loop, config_loop
config_loop()
from agent import Agent
from messages import ACLMessage
from aid import AID
from protocols import FipaContractNetProtocol
from filters import Filter
from pickle import loads, dumps
from time import sleep

#===============================================================================
# What is needed to create an agent with standardized protocols behaviours?
# First, the protocol class needs to be defined
# Second, this protocol class needs to be associated with the agent's 
# behaviour
#===============================================================================



class ConsumerAgentBehaviour(FipaContractNetProtocol):
    def __init__(self, agent, message):
        super(ConsumerAgentBehaviour, self).__init__(agent, message, is_initiator=True)
        self.bestPropose = None
        self.bestBookStore = None
        
    def handle_propose(self, message):
        FipaContractNetProtocol.handle_propose(self, message)
        display_message(self.agent.aid.name, 'Proposal Received')
    
    def handle_all_proposes(self, proposes):
        FipaContractNetProtocol.handle_all_proposes(self, proposes)
        
        try:
            
            self.bestPropose = proposes[0]
            
            for propose in proposes:
                content = loads(propose.content)
                if content['how much is'] < loads(self.bestPropose.content)['how much is']:
                    self.bestPropose = propose
                    
            response = self.bestPropose.create_reply()
            response.set_performative(ACLMessage.ACCEPT_PROPOSAL)
            response.set_content('Proposal Accepted')
            self.agent.send(response)
            
            for propose in proposes:
                if propose != self.bestPropose:
                    response = propose.create_reply()
                    response.set_performative(ACLMessage.REJECT_PROPOSAL)
                    response.set_content('Proposal Rejected')
                    self.agent.send(response)
        except:
            display_message(self.agent.aid.name, 'Unable to process because no message has returned.')
        
    def handle_inform(self, message):
        FipaContractNetProtocol.handle_inform(self, message)
        display_message(self.agent.aid.name, 'Purchase Approved')

class ConsumerAgent(Agent):
    
    def __init__(self, aid, bookStores, order):
        Agent.__init__(self, aid)
    
        self.bookStores = bookStores
        self.order = order
        
        cfp_message = ACLMessage(ACLMessage.CFP)
        cfp_message.set_protocol(ACLMessage.FIPA_CONTRACT_NET_PROTOCOL)
        for i in self.bookStores:
            cfp_message.add_receiver(i)
        cfp_message.set_content(dumps(self.order))
        
        behav_ = ConsumerAgentBehaviour(self, cfp_message)
        self.addBehaviour(behav_)

if __name__ == '__main__':
    
    agents = []
    order = {'title' : 'The Lord of the Rings', 'author' : 'J. R. R. Tolkien', 'qty' : 5}
       
    #consumidor = ConsumerAgent(AID('Lucas@192.168.0.100:2004'), ['Saraiva', 'Cultura', 'Nobel'], order)
    consumidor = ConsumerAgent(AID('Lucas'), ['Saraiva', 'Cultura', 'Nobel'], order)
    
    consumidor.set_ams()
    agents.append(consumidor)
    
    start_loop(agents)