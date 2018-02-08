#! /usr/bin/python
# -*- coding: utf-8 -*-

from utils import set_ams, config_loop, start_loop, display_message
config_loop(gui=True)

from agent import Agent
from messages import ACLMessage
from aid import AID
from pickle import dumps, loads
from time import sleep

class Consumer(Agent):
    
    def __init__(self, aid, bookStores):
        Agent.__init__(self, aid)
        
        self.bookStores = bookStores
        self.bestPropose = None
        self.bestBookStore = None
        self.proposes = []
        self.messages = []
        self.sends = 0
        self.receives = 0
    
    def consult(self, order):
        message = ACLMessage(ACLMessage.CALL_FOR_PROPOSAL)
        for i in self.bookStores:
            message.add_receiver(i)
        message.set_content(dumps(order))
        self.sends = len(self.bookStores)
        self.send(message)
    
    def buy(self, proposal):
        message = ACLMessage(ACLMessage.REQUEST)
        message.add_receiver(proposal['book store'])
        message.addContent(dumps(proposal))
        self.send(message)
    
    def analisys(self):
        self.bestPropose = self.messages[0]
        for message in self.messages:
            propose = loads(message.content)
            if propose['how much is'] < loads(self.messages[0].content)['how much is']:
                self.bestPropose = message
                
        return self.bestPropose
    
    def on_start
on_start(self):
        Agent.on_start
on_start(self)
        sleep(1)
        order = {'title' : 'The Lord of the Rings', 'author' : 'J. R. R. Tolkien', 'qty' : 5}
        self.consult(order)
            
    def react(self, message):
        
        if message.performative == ACLMessage.PROPOSE or message.performative == ACLMessage.REJECT_PROPOSAL:
            self.receives += 1
            self.messages.append(message)
            display_message(self.aid.name, 'Received Proposal')
            print str(loads(message.content))
        
        if self.receives == self.sends:
            message = self.analisys()
            display_message(self.aid.name, 'Best Proposal Selected:')
            propose = loads(message.content)
            print str(propose)
        
class BookStore(Agent):
    def __init__(self, aid, booksList):
        Agent.__init__(self, aid)
        
        self.booksList = booksList
    
    def on_start
on_start(self):
        pass
    
    def react(self, message):
        display_message(self.aid.name, 'Received Purchase Order')
        self.message = message
        if message.performative == ACLMessage.CALL_FOR_PROPOSAL:
            self.order = loads(message.content)
            self.analisys(self.order)
    
    def analisys(self, order):
        for book in self.booksList:
            if book['title'] == order['title'] and book['author'] == order['author']:
                if book['qty'] >= order['qty']:
                    message = ACLMessage(ACLMessage.PROPOSE)
                    message.add_receiver(self.message.sender)
                    book['book store'] = self.aid.name
                    message.set_content(dumps(book))
                    self.send(message)
                else:
                    message = ACLMessage(ACLMessage.REJECT_PROPOSAL)
                    message.add_receiver(self.message.sender)
                    message.set_content('Request Rejected')
                    self.send(message)

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
    
    bookStoresInfo = [(AID(name='Saraiva'), booksList_Saraiva),
                      (AID(name='Cultura'), bookslist_Cultura),
                      (AID(name='Nobel'), bookslist_Nobel)]
    
    set_ams('localhost', 8000)
    
    for bookStore in bookStoresInfo:
        agent = BookStore(bookStore[0], bookStore[1])
        agent.set_ams('localhost', 8000)
        agent.start()
    
    consumidor = Consumer(AID('Lucas'), ['Saraiva', 'Cultura', 'Nobel'])
    consumidor.set_ams('localhost', 8000)
    consumidor.start()
    
    start_loop()