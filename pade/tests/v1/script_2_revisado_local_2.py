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
        self.addBehaviour(comportamento)

if __name__ == '__main__':
    
    agents = []
    pedido = {'title' : 'The Lord of the Rings', 'author' : 'J. R. R. Tolkien', 'qtd' : 5}
       
    #consumidor = AgenteConsumidor(AID('Lucas@192.168.0.100:2004'), ['Saraiva', 'Cultura', 'Nobel'], pedido)
    consumidor = AgenteConsumidor(AID('Lucas'), ['Saraiva', 'Cultura', 'Nobel'], pedido)
    
    consumidor.set_ams()
    agents.append(consumidor)
    
    start_loop(agents)