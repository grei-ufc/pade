#! /usr/bin/python
# -*- coding: utf-8 -*-

from utils import startAMS, startLoop, displayMessage
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
    
    def consult(self, pedido):
        message = ACLMessage(ACLMessage.CALL_FOR_PROPOSAL)
        message.setSender(self.aid.name)
        for i in self.bookStores:
            message.addReceiver(i)
        message.setContent(dumps(pedido))
        self.sends = len(self.bookStores)
        self.send(message)
    
    def buy(self, proposta):
        message = ACLMessage(ACLMessage.REQUEST)
        message.setSender(self.aid.name)
        message.addReceiver(proposta['book store'])
        message.addContent(dumps(proposta))
        self.send(message)
    
    def analisys(self):
        self.bestPropose = self.messages[0]
        for message in self.messages:
            propose = loads(message.content)
            if propose['how much is'] < loads(self.messages[0].content)['how much is']:
                self.bestPropose = message
                
        return self.bestPropose
    
    def onStart(self):
        sleep(1)
        pedido = {'title' : 'The Lord of the Rings', 'author' : 'J. R. R. Tolkien', 'qtd' : 5}
        self.consult(pedido)
            
    def react(self, message):
        
        if message.performative == ACLMessage.PROPOSE or message.performative == ACLMessage.REJECT_PROPOSAL:
            self.receives += 1
            self.messages.append(message)
            displayMessage(self.aid.name, 'Received Propose')
            print str(loads(message.content))
        
        if self.receives == self.sends:
            message = self.analisys()
            displayMessage(self.aid.name, 'Best Propose Selected:')
            propose = loads(message.content)
            print str(propose)
        
class BookStore(Agent):
    def __init__(self, aid, booksList):
        Agent.__init__(self, aid)
        
        self.booksList = booksList
    
    def react(self, message):
        displayMessage(self.aid.name, 'Received Purchase Order')
        self.message = message
        if message.performative == ACLMessage.CALL_FOR_PROPOSAL:
            self.pedido = loads(message.content)
            self.analisys(self.pedido)
    
    def analisys(self, pedido):
        for book in self.booksList:
            if book['title'] == pedido['title'] and book['author'] == pedido['author']:
                if book['qtd'] >= pedido['qtd']:
                    message = ACLMessage(ACLMessage.PROPOSE)
                    message.setSender(self.aid.name)
                    message.addReceiver(self.message.sender)
                    book['book store'] = self.aid.name
                    message.setContent(dumps(book))
                    self.send(message)
                else:
                    message = ACLMessage(ACLMessage.REJECT_PROPOSAL)
                    message.setSender(self.aid.name)
                    message.addReceiver(self.message.sender)
                    message.setContent('Request Refused')
                    self.send(message)

if __name__ == '__main__':
    
    
    booksList_Saraiva = [{'title' : 'The Lord of the Rings', 'author' : 'J. R. R. Tolkien', 'qtd' : 10, 'how much is' : 53.50},
                         {'title' : 'Harry Potter', 'author' : 'J. K. Roling', 'qtd' : 10, 'how much is' : 33.70},
                         {'title' : 'Game of Thrones', 'author' : 'A. M. M. Martin', 'qtd' : 10,'how much is' : 23.80}
                         ]
    
    bookslist_Cultura = [{'title' : 'The Lord of the Rings', 'author' : 'J. R. R. Tolkien', 'qtd' : 10, 'how much is' : 43.50},
                         {'title' : 'Harry Potter', 'author' : 'J. K. Roling', 'qtd' : 10, 'how much is' : 31.70},
                         {'title' : 'Game of Thrones', 'author' : 'A. M. M. Martin', 'qtd' : 10, 'how much is' : 53.80}
                         ]
    
    bookslist_Nobel = [{'title' : 'The Lord of the Rings', 'author' : 'J. R. R. Tolkien', 'qtd' : 10, 'how much is' : 63.50},
                         {'title' : 'Harry Potter', 'author' : 'J. K. Roling', 'qtd' : 10, 'how much is' : 35.70},
                         {'title' : 'Game of Thrones', 'author' : 'A. M. M. Martin', 'qtd' : 10, 'how much is' : 33.80}
                         ]
    
    bookStoresInfo = [(AID(name='Saraiva'), booksList_Saraiva),
                      (AID(name='Cultura'), bookslist_Cultura),
                      (AID(name='Nobel'), bookslist_Nobel)]
    
    startAMS(8000)
    
    for bookStore in bookStoresInfo:
        agent = BookStore(bookStore[0], bookStore[1])
        agent.setAMS('localhost', 8000)
        agent.start()
     
    consumidor = Consumer(AID('Lucas'), ['Saraiva', 'Cultura', 'Nobel'])
    consumidor.setAMS('localhost', 8000)
    consumidor.start()
    
    startLoop()