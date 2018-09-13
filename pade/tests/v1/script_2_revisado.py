# -*- encoding: utf-8 -*-

from utils import display_message, set_ams, start_loop, config_loop
config_loop(gui=True)
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
            response.set_content('Propostal Accepted')
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

class BookstoreAgentBehaviour(FipaContractNetProtocol):
    def __init__(self, agent):
        super(BookstoreAgentBehaviour, self).__init__(agent, is_initiator=False)
    
    def handle_cfp(self, message):
        FipaContractNetProtocol.handle_cfp(self, message)
        display_message(self.agent.aid.name, 'Request Received.')
        
        order = loads(message.content)
        
        for book in self.agent.booksList:
            if book['title'] == order['title'] and book['author'] == order['author']:
                if book['qty'] >= order['qty']:
                    response = message.create_reply()
                    response.set_performative(ACLMessage.PROPOSE)
                    book['book store'] = self.agent.aid.name
                    response.set_content(dumps(book))
                    self.agent.send(response)
                else:
                    response = message.create_reply()
                    response.set_performative(ACLMessage.REJECT_PROPOSAL)
                    response.set_content('Request Rejected')
                    self.agent.send(response)
    
    def handle_accept_propose(self, message):
        FipaContractNetProtocol.handle_accept_propose(self, message)
        
        display_message(self.agent.aid.name, 'Proposal Accepted')
        
        response = message.create_reply()
        response.set_performative(ACLMessage.INFORM)
        response.set_content('Purchase Approved')
        self.agent.send(response)
        
        
    def handle_reject_proposes(self, message):
        FipaContractNetProtocol.handle_reject_proposes(self, message)
        
        display_message(self.agent.aid.name, 'Proposal Rejected')

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
        self.behaviours.append(behav_)

class BookstoreAgent(Agent):
    
    def __init__(self, aid, booksList):
        Agent.__init__(self, aid)
        
        self.booksList = booksList
        
        behav_= BookstoreAgentBehaviour(self)
        self.behaviours.append(behav_)

if __name__ == '__main__':
    booksList_Saraiva = [{'title' : 'The Lord of the Rings', 'author' : 'J. R. R. Tolkien', 'qty' : 10, 'how much is' : 53.50},
                         {'title' : 'Harry Potter', 'author' : 'J. K. Roling', 'qty' : 10, 'how much is' : 33.70},
                         {'title' : 'Game of Thrones', 'author' : 'A. M. M. Martin', 'qty' : 10,'how much is' : 23.80}
                         ]
    
    bookslist_Cultura = [{'title' : 'The Lord of the Rings', 'author' : 'J. R. R. Tolkien', 'qty' : 10, 'how much is' : 43.50},
                         {'title' : 'Harry Potter', 'author' : 'J. K. Roling', 'qty' : 10, 'how much is' : 31.70},
                         {'title' : 'Game of Thrones', 'author' : 'A. M. M. Martin', 'qty' : 10, 'how much is' : 53.80}
                         ]
    
    bookslist_Nobel = [{'title' : 'The Lord of the Rings', 'author' : 'J. R. R. Tolkien', 'qty' : 10, 'how much is' : 63.50},
                         {'title' : 'Harry Potter', 'author' : 'J. K. Roling', 'qty' : 10, 'how much is' : 35.70},
                         {'title' : 'Game of Thrones', 'author' : 'A. M. M. Martin', 'qty' : 10, 'how much is' : 33.80}
                         ]
    
    bookStoresInfo = [(AID(name='Cultura'), bookslist_Cultura),
                      (AID(name='Saraiva'), booksList_Saraiva),
                      (AID(name='Nobel'), bookslist_Nobel)]
    
    order = {'title' : 'The Lord of the Rings', 'author' : 'J. R. R. Tolkien', 'qty' : 5}
    
    set_ams('localhost', 8000)
    
    agents = []
    saraiva = BookstoreAgent(AID(name='Saraiva'), booksList_Saraiva)
    agents.append(saraiva)
    
    cultura = BookstoreAgent(AID(name='Cultura'), bookslist_Cultura)
    agents.append(cultura)
    
    nobel = BookstoreAgent(AID(name='Nobel'), bookslist_Nobel)
    #   agents.append(nobel)
       
    consumidor = ConsumerAgent(AID('Lucas'), ['Saraiva', 'Cultura', 'Nobel'], order)
    agents.append(consumidor)
    
    start_loop(agents)