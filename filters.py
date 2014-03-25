# -*- encoding: utf-8 -*-

from messages import ACLMessage
from aid import AID

class Filter():
    '''
        Esta classe instacia um objeto filtro que tem como proposito
        selecionar mensagens com atributos pré-estabelecidos neste objeto
    '''
    def __init__(self):
        self.conversationID = None
        self.sender = None
        self.performative = None
        self.protocol = None
    
    def setSender(self, aid):
        self.sender = aid
        
    def setPerformative(self, performative):
        self.performative = performative
    
    def setConversationID(self, conversationID):
        self.conversationID = conversationID
    
    def setProtocol(self, protocol):
        self.protocol = protocol
    
    def filter(self, message):
        state = True
        
        if self.conversationID != None and self.conversationID != message.conversationID:
            state = False
        
        if self.sender != None and self.sender != message.sender:
            state = False
        
        if self.performative != None and self.performative != message.performative:
            state = False
        
        if self.protocol != None and self.protocol != message.protocol:
            state = False
            
        return state

if __name__ == '__main__':
    message = ACLMessage(ACLMessage.REQUEST)
    message.setSender(AID('lucas'))
    message.addReceiver('allana')
    message.setProtocol(ACLMessage.FIPA_REQUEST_PROTOCOL)
    
    filtro = Filter()
    filtro.setProtocol(ACLMessage.FIPA_REQUEST_PROTOCOL)
    
    if filtro.filter(message):
        print message.asXML()
    else:
        print 'A mensagem foi barrada pelo protocolo'   
    