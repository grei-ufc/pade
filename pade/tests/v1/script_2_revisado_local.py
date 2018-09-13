# -*- encoding: utf-8 -*-

from utils import display_message, set_ams, start_loop, config_loop
#config_loop(gui=True)
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


class BookstoreAgentBehaviour(FipaContractNetProtocol):
    def __init__(self, agent):
        super(BookstoreAgentBehaviour, self).__init__(agent, is_initiator=False)
    
    def handle_cfp(self, message):
        FipaContractNetProtocol.handle_cfp(self, message)
        display_message(self.agent.aid.name, 'Request Received')
        
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

class BookstoreAgent(Agent):
    
    def __init__(self, aid, booksList):
        Agent.__init__(self, aid)
        
        self.booksList = booksList
        
        behav_ = BookstoreAgentBehaviour(self)
        self.addBehaviour(behav_)

if __name__ == '__main__':
    booksList_Saraiva = [{'title' : 'The Lord of the Rings', 'author' : 'J. R. R. Tolkien', 'qty' : 10, 'how much is' : 53.50},
                         {'title' : 'Harry Potter', 'author' : 'J. K. Roling', 'qty' : 10, 'how much is' : 33.70},
                         {'title' : 'Game of Thrones', 'author' : 'A. M. M. Martin', 'qty' : 10,'how much is' : 23.80}
                         ]
    
    bookslist_Cultura = [{'title' : 'The Lord of the Rings', 'author' : 'J. R. R. Tolkien', 'qty' : 10, 'how much is' : 43.50},
                         {'title' : 'Harry Potter', 'author' : 'J. K. Roling', 'qty' : 10, 'how much is' : 31.70},
                         {'title' : 'Game of Thrones', 'author' : 'A. M. M. Martin', 'qty' : 10, 'how much is' : 53.80}
                         ]
    
    bookStoresInfo = [(AID(name='Cultura'), bookslist_Cultura),
                      (AID(name='Saraiva'), booksList_Saraiva)]
    
    order = {'title' : 'The Lord of the Rings', 'author' : 'J. R. R. Tolkien', 'qty' : 5}
    
    #set_ams('localhost', 8000)
    
    agents = []
    #saraiva = BookstoreAgent(AID(name='Saraiva@192.168.0.100:2002'), booksList_Saraiva)
    saraiva = BookstoreAgent(AID(name='Saraiva'), booksList_Saraiva)
    saraiva.set_ams()
    agents.append(saraiva)
    
    #cultura = BookstoreAgent(AID(name='Cultura@192.168.0.100:2003'), bookslist_Cultura)
    cultura = BookstoreAgent(AID(name='Cultura'), bookslist_Cultura)
    cultura.set_ams()
    agents.append(cultura)
    
    start_loop(agents)