# -*- encoding: utf-8 -*-

from pade.acl.aid import AID
from pade.acl.messages import ACLMessage

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
    
    def set_sender(self, aid):
        self.sender = aid
        
    def set_performative(self, performative):
        self.performative = performative
    
    def setConversationID(self, conversationID):
        self.conversationID = conversationID
    
    def set_protocol(self, protocol):
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
    message.set_sender(AID('lucas'))
    message.add_receiver('allana')
    message.set_protocol(ACLMessage.FIPA_REQUEST_PROTOCOL)
    
    filtro = Filter()
    filtro.set_protocol(ACLMessage.FIPA_REQUEST_PROTOCOL)
    
    if filtro.filter(message):
        print message.as_xml()
    else:
        print 'A mensagem foi barrada pelo protocolo'
