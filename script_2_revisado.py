# -*- encoding: utf-8 -*-

from utils import displayMessage, setAMS, startLoop, configLoop
configLoop(gui=True)
from agent import Agent
from messages import ACLMessage
from aid import AID
from protocols import FIPA_ContractNet_Protocol
from filters import Filter
from pickle import loads, dumps
from time import sleep

#===============================================================================
# Note, o que é necessário para criar um agente com comportamentos padronizados
# em protocolos?
# Primeiro, é preciso definir a classe protocolo
# Segundo é preciso associar esta classe protocolo como um comportamento do 
# agente
#===============================================================================


class ComportamentoAgenteConsumidor(FIPA_ContractNet_Protocol):
    def __init__(self, agent, message):
        super(ComportamentoAgenteConsumidor, self).__init__(agent, message, isInitiator=True)
        self.bestPropose = None
        self.bestBookStore = None
        
    def handlePropose(self, message):
        FIPA_ContractNet_Protocol.handlePropose(self, message)
        displayMessage(self.agent.aid.name, 'Proposta Recebida')
    
    def handleAllProposes(self, proposes):
        FIPA_ContractNet_Protocol.handleAllProposes(self, proposes)
        
        try:
            
            self.bestPropose = proposes[0]
            
            for propose in proposes:
                content = loads(propose.content)
                if content['how much is'] < loads(self.bestPropose.content)['how much is']:
                    self.bestPropose = propose
                    
            response = self.bestPropose.createReply()
            response.setPerformative(ACLMessage.ACCEPT_PROPOSAL)
            response.setContent('Proposta Aceita')
            self.agent.send(response)
            
            for propose in proposes:
                if propose != self.bestPropose:
                    response = propose.createReply()
                    response.setPerformative(ACLMessage.REJECT_PROPOSAL)
                    response.setContent('Proposta Recusada')
                    self.agent.send(response)
        except:
            displayMessage(self.agent.aid.name, 'O Processamento não foi possivel porque nenhuma mensagem foi retornada.')
        
    def handleInform(self, message):
        FIPA_ContractNet_Protocol.handleInform(self, message)
        displayMessage(self.agent.aid.name, 'Compra Autorizada')

class ComportamentoAgenteLivraria(FIPA_ContractNet_Protocol):
    def __init__(self, agent):
        super(ComportamentoAgenteLivraria, self).__init__(agent, isInitiator=False)
    
    def handleCFP(self, message):
        FIPA_ContractNet_Protocol.handleCFP(self, message)
        displayMessage(self.agent.aid.name, 'Solicitação Recebida')
        
        pedido = loads(message.content)
        
        for book in self.agent.booksList:
            if book['title'] == pedido['title'] and book['author'] == pedido['author']:
                if book['qtd'] >= pedido['qtd']:
                    response = message.createReply()
                    response.setPerformative(ACLMessage.PROPOSE)
                    book['book store'] = self.agent.aid.name
                    response.setContent(dumps(book))
                    self.agent.send(response)
                else:
                    response = message.createReply()
                    response.setPerformative(ACLMessage.REJECT_PROPOSAL)
                    response.setContent('Requisição Recusada')
                    self.agent.send(response)
    
    def handleAcceptPropose(self, message):
        FIPA_ContractNet_Protocol.handleAcceptPropose(self, message)
        
        displayMessage(self.agent.aid.name, 'Proposta Aceita')
        
        response = message.createReply()
        response.setPerformative(ACLMessage.INFORM)
        response.setContent('Compra Autorizada')
        self.agent.send(response)
        
        
    def handleRejectPropose(self, message):
        FIPA_ContractNet_Protocol.handleRejectPropose(self, message)
        
        displayMessage(self.agent.aid.name, 'Proposta Recusada')

class AgenteConsumidor(Agent):
    
    def __init__(self, aid, bookStores, pedido):
        Agent.__init__(self, aid)
    
        self.bookStores = bookStores
        self.pedido = pedido
        
        cfp_message = ACLMessage(ACLMessage.CFP)
        cfp_message.setProtocol(ACLMessage.FIPA_CONTRACT_NET_PROTOCOL)
        for i in self.bookStores:
            cfp_message.addReceiver(i)
        cfp_message.setContent(dumps(self.pedido))
        
        comportamento = ComportamentoAgenteConsumidor(self, cfp_message)
        self.addBehaviour(comportamento)

class AgenteLivraria(Agent):
    
    def __init__(self, aid, booksList):
        Agent.__init__(self, aid)
        
        self.booksList = booksList
        
        comportamento = ComportamentoAgenteLivraria(self)
        self.addBehaviour(comportamento)

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
    
    bookStoresInfo = [(AID(name='Cultura'), bookslist_Cultura),
                      (AID(name='Saraiva'), booksList_Saraiva),
                      (AID(name='Nobel'), bookslist_Nobel)]
    
    pedido = {'title' : 'The Lord of the Rings', 'author' : 'J. R. R. Tolkien', 'qtd' : 5}
    
    setAMS('localhost', 8000)
    
    agents = []
    saraiva = AgenteLivraria(AID(name='Saraiva'), booksList_Saraiva)
    saraiva.setAMS()
    agents.append(saraiva)
    
    cultura = AgenteLivraria(AID(name='Cultura'), bookslist_Cultura)
    cultura.setAMS()
    agents.append(cultura)
    
    nobel = AgenteLivraria(AID(name='Nobel'), bookslist_Nobel)
    nobel.setAMS()
    #agents.append(nobel)
       
    consumidor = AgenteConsumidor(AID('Lucas'), ['Saraiva', 'Cultura', 'Nobel'], pedido)
    consumidor.setAMS()
    agents.append(consumidor)
    
    startLoop(agents)