#! /usr/bin/python
# -*- coding: utf-8 -*-

"""
Created on Thu Jan 30 14:30:06 2014

@author: lucas
"""

import xml.etree.ElementTree as ET
from datetime import datetime

class ACLMessage(ET.Element):
    '''
        Classe que implementa uma mensagem do tipo ACLMessage
    '''
    
    ACCEPT_PROPOSAL = 'accept-proposal'
    AGREE = 'agree'
    CANCEL = 'cancel'
    CFP = 'cfp'
    CALL_FOR_PROPOSAL = 'call-for-proposal'
    CONFIRM = 'confirm'
    DISCONFIRM = 'disconfirm'
    FAILURE = 'failure'
    INFORM = 'inform'
    NOT_UNDERSTOOD = 'not-understood'
    PROPOSE = 'propose'
    QUERY_IF = 'query-if'
    QUERY_REF = 'query-ref'
    REFUSE = 'refuse'
    REJECT_PROPOSAL = 'reject-proposal'
    REQUEST = 'request'
    REQUEST_WHEN = 'request-when'
    REQUEST_WHENEVER = 'request-whenever'
    SUBSCRIBE = 'subscribe'
    INFORM_IF = 'inform-if'
    PROXY = 'proxy'
    PROPAGATE = 'propagate'
    
    FIPA_REQUEST_PROTOCOL = 'fipa-request protocol'
    FIPA_QUERY_PROTOCOL = 'fipa-query protocol'
    FIPA_REQUEST_WHEN_PROTOCOL = 'fipa-request-when protocol'
    FIPA_CONTRACT_NET_PROTOCOL = 'fipa-contract-net protocol'
    
    ACLMessageAsXML = 'ACLMessageXML'
    ACLMessageAsString = 'ACLMessageString'
    
    def __init__(self, performative=None):
        '''
            metodo de inicialização
        '''
        super(ACLMessage, self).__init__('ACLMessage', attrib = {'date' : datetime.now().strftime('%d/%m/%Y - %H:%M:%S:%f')})
        
        self.performaives = ['accept-proposal', 'agree', 'cancel',
                             'cfp', 'call-for-proposal', 'confirm', 'disconfirm',
                             'failure', 'inform', 'not-understood',
                             'propose', 'query-if', 'query-ref',
                             'refuse', 'reject-proposal', 'request',
                             'request-when', 'request-whenever', 'subscribe',
                             'inform-if', 'proxy', 'propagate']
        
        self.protocols = ['fipa-request protocol', 'fipa-query protocol', 'fipa-request-when protocol',
                          'fipa-contract-net protocol']
                             
        self.append(ET.Element('performative'))
        self.append(ET.Element('sender'))
        self.append(ET.Element('receivers'))
        self.append(ET.Element('reply-to'))
        self.append(ET.Element('content'))
        self.append(ET.Element('language'))
        self.append(ET.Element('enconding'))
        self.append(ET.Element('ontology'))
        self.append(ET.Element('protocol'))
        self.append(ET.Element('conversation-id'))
        self.append(ET.Element('reply-with'))
        self.append(ET.Element('in-reply-to'))
        self.append(ET.Element('reply-by'))
        
        if performative != None:
            if performative.lower() in self.performaives:
                self.performative = performative.lower()
                self.find('performative').text = self.performative
            
        self.sender = None
        self.receivers = []
        self.reply_to = []
        self.content = None
        self.language = None
        self.encoding = None
        self.ontology = None
        self.protocol = None
        self.conversation_id = None
        self.reply_with = None
        self.in_reply_to = None
        self.reply_by = None
        
        self.ACLMessageRepresentation = self.ACLMessageAsXML
    
    def setPerformative(self, data):
        '''
            Metodo que seta o parametro Performtive da mensagem ACL
        '''
        self.performative = data
        self.find('performative').text = str(data).lower()
        
    def setSender(self, data):
        self.sender = data
        self.find('sender').text = str(data)
    
    def addReceiver(self, data):
        self.receivers.append(data)
        receivers = self.find('receivers')
        receiver = ET.Element('receiver')
        receiver.text = str(data)
        receivers.append(receiver)
    
    def addReply_to(self, data):
        self.reply_to.append[data]
        reply_to = self.find('reply_to')
        receiver = ET.Element('receiver')
        receiver.text = str(data)
        reply_to.append(receiver)
        
    def setContent(self, data):
        self.content = data
        self.find('content').text = str(data)
        
    def setLanguage(self, data):
        self.language = data
        self.find('language').text = str(data)
        
    def setEncoding(self, data):
        self.encoding = data
        self.find('encoding').text = str(data)
    
    def setOntology(self, data):
        self.ontology = data
        self.find('ontology').text = str(data)
    
    def setProtocol(self, data):
        self.protocol = data
        self.find('protocol').text = str(data)
    
    def setConversationId(self, data):
        self.conversation_id = data
        self.find('conversation_id').text = str(data)
    
    def setReply_with(self, data):
        self.reply_with = data
        self.find('reply-with').text = str(data)
    
    def setIn_reply_to(self, data):
        self.in_reply_to = data
        self.find('in-reply-to').text = str(data)
    
    def setReply_by(self, data):
        self.reply_by = data
        self.find('reply-by').text = str(data)
        
    def getMsg(self):
        if self.ACLMessageRepresentation == self.ACLMessageAsXML:
            return ET.tostring(self)
        elif self.ACLMessageRepresentation == self.ACLMessageAsString:
            return self.asString()
    
    def asString(self):
        """
        returns a printable version of the message in ACL string representation
        """

        p = '('

        p = p + str(self.performative) + '\n'
        if self.sender:
            p = p + ":sender " + str(self.sender) + "\n"

        if self.receivers:
            p = p + ":receiver\n (set\n"
            for i in self.receivers:
                p = p + str(i) + '\n'

            p = p + ")\n"
        if self.content:
            p = p + ':content "' + str(self.content) + '"\n'

        if self.reply_with:
            p = p + ":reply-with " + self.reply_with + '\n'

        if self.reply_by:
            p = p + ":reply-by " + self.reply_by + '\n'

        if self.in_reply_to:
            p = p + ":in-reply-to " + self.in_reply_to + '\n'

        if self.reply_to:
            p = p + ":reply-to \n" + '(set\n'
            for i in self.reply_to:
                p = p + i + '\n'
            p = p + ")\n"

        if self.language:
            p = p + ":language " + self.language + '\n'

        if self.encoding:
            p = p + ":encoding " + self.encoding + '\n'

        if self.ontology:
            p = p + ":ontology " + self.ontology + '\n'

        if self.protocol:
            p = p + ":protocol " + self.protocol + '\n'

        if self.conversation_id:
            p = p + ":conversation-id " + self.conversation_id + '\n'

        p = p + ")\n"

        return p
    
    def setMsg(self, data):
        aclmsg = ET.fromstring(data)
        
        try:
            self.performative = aclmsg.find('performative').text
            self.find('performative').text = self.performative
        except:
            pass
        
        try:
            self.sender = aclmsg.find('sender').text
            self.find('sender').text = self.sender
        except:
            pass
        
        try:
            receivers = aclmsg.find('receivers').getchildren()
            
            for receiver in receivers:
                self.receivers.append(receiver.text)
                r = ET.Element('receiver')
                r.text = receiver.text
                self.find('receivers').append(r)
        except:
            pass
        
        try:
            receivers = aclmsg.find('reply-to').getchildren()
            
            for receiver in receivers:
                self.reply_to.append(receiver.text)
                r = ET.Element('receiver')
                r.text = receiver.text
                self.find('reply-to').append(r)
        except:
            pass
        
        try:
            self.content = aclmsg.find('content').text
            self.find('content').text = self.content
        except:
            pass
        
        try:
            self.language = aclmsg.find('language').text
            self.find('language').text = self.language
        except:
            pass
        
        try:
            self.encoding = aclmsg.find('encoding').text
            self.find('encoding').text = self.encoding
        except:
            pass
        
        try:
            self.ontology = aclmsg.find('ontology').text
            self.find('ontology').text = self.ontology
        except:
            pass
        
        try:
            self.protocol = aclmsg.find('protocol').text
            self.find('protocol').text = self.protocol
        except:
            pass
        
        try:
            self.conversation_id = aclmsg.find('conversation-id').text
            self.find('conversation-id').text = self.conversation_id
        except:
            pass
        
        try:
            self.reply_with = aclmsg.find('reply-with').text
            self.find('reply-with').text = self.reply_with
        except:
            pass
        
        try:
            self.in_reply_to = aclmsg.find('in-reply-to').text
            self.find('in-reply-to').text = self.in_reply_to
        except:
            pass
        
        try:
            self.reply_by = aclmsg.find('reply-by').text
            self.find('reply-by').text = self.reply_by
        except:
            pass
    
if __name__ == '__main__':
    msg = ACLMessage(ACLMessage.INFORM)