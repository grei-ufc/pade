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
# Note, o que é necessário para criar um agente com comportamentos padronizados
# em protocolos?
# Primeiro, é preciso definir a classe protocolo
# Segundo é preciso associar esta classe protocolo como um comportamento do 
# agente
#===============================================================================


class ComportamentoAgenteConsumidor(FipaContractNetProtocol):
    def __init__(self, agent, message):
        super(ComportamentoAgenteConsumidor, self).__init__(agent, message, is_initiator=True)
        self.bestPropose = None
        self.bestBookStore = None
        
    def handle_propose(self, message):
        FipaContractNetProtocol.handle_propose(self, message)
        display_message(self.agent.aid.name, 'Proposta Recebida')
    
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
            response.set_content('Proposta Aceita')
            self.agent.send(response)
            
            for propose in proposes:
                if propose != self.bestPropose:
                    response = propose.create_reply()
                    response.set_performative(ACLMessage.REJECT_PROPOSAL)
                    response.set_content('Proposta Recusada')
                    self.agent.send(response)
        except:
            display_message(self.agent.aid.name, 'O Processamento não foi possivel porque nenhuma mensagem foi retornada.')
        
    def handle_inform(self, message):
        FipaContractNetProtocol.handle_inform(self, message)
        display_message(self.agent.aid.name, 'Compra Autorizada')

class ComportamentoAgenteLivraria(FipaContractNetProtocol):
    def __init__(self, agent):
        super(ComportamentoAgenteLivraria, self).__init__(agent, is_initiator=False)
    
    def handle_cfp(self, message):
        FipaContractNetProtocol.handle_cfp(self, message)
        display_message(self.agent.aid.name, 'Solicitação Recebida')
        
        pedido = loads(message.content)
        
        for book in self.agent.booksList:
            if book['title'] == pedido['title'] and book['author'] == pedido['author']:
                if book['qtd'] >= pedido['qtd']:
                    response = message.create_reply()
                    response.set_performative(ACLMessage.PROPOSE)
                    book['book store'] = self.agent.aid.name
                    response.set_content(dumps(book))
                    self.agent.send(response)
                else:
                    response = message.create_reply()
                    response.set_performative(ACLMessage.REJECT_PROPOSAL)
                    response.set_content('Requisição Recusada')
                    self.agent.send(response)
    
    def handle_accept_propose(self, message):
        FipaContractNetProtocol.handle_accept_propose(self, message)
        
        display_message(self.agent.aid.name, 'Proposta Aceita')
        
        response = message.create_reply()
        response.set_performative(ACLMessage.INFORM)
        response.set_content('Compra Autorizada')
        self.agent.send(response)
        
        
    def handle_reject_proposes(self, message):
        FipaContractNetProtocol.handle_reject_proposes(self, message)
        
        display_message(self.agent.aid.name, 'Proposta Recusada')

class AgenteConsumidor(Agent):
    
    def __init__(self, aid, bookStores, pedido):
        Agent.__init__(self, aid)
    
        self.bookStores = bookStores
        self.pedido = pedido
        
        cfp_message = ACLMessage(ACLMessage.CFP)
        cfp_message.set_protocol(ACLMessage.FIPA_CONTRACT_NET_PROTOCOL)
        for i in self.bookStores:
            cfp_message.add_receiver(i)
        cfp_message.set_content(dumps(self.pedido))
        
        comportamento = ComportamentoAgenteConsumidor(self, cfp_message)
        self.behaviours.append(comportamento)

class AgenteLivraria(Agent):
    
    def __init__(self, aid, booksList):
        Agent.__init__(self, aid)
        
        self.booksList = booksList
        
        comportamento = ComportamentoAgenteLivraria(self)
        self.behaviours.append(comportamento)

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
    
    set_ams('localhost', 8000)
    
    agents = []
    saraiva = AgenteLivraria(AID(name='Saraiva'), booksList_Saraiva)
    agents.append(saraiva)
    
    cultura = AgenteLivraria(AID(name='Cultura'), bookslist_Cultura)
    agents.append(cultura)
    
    nobel = AgenteLivraria(AID(name='Nobel'), bookslist_Nobel)
    #   agents.append(nobel)
       
    consumidor = AgenteConsumidor(AID('Lucas'), ['Saraiva', 'Cultura', 'Nobel'], pedido)
    agents.append(consumidor)
    
    start_loop(agents)