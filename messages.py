#! /usr/bin/python
# -*- coding: utf-8 -*-

"""
Created on Thu Jan 30 14:30:06 2014

@author: lucas
"""

import xml.etree.ElementTree as ET
from xml.dom import minidom
from datetime import datetime
from uuid import uuid1
from aid import AID

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
    
    performaives = [         'accept-proposal', 'agree', 'cancel',
                             'cfp', 'call-for-proposal', 'confirm', 'disconfirm',
                             'failure', 'inform', 'not-understood',
                             'propose', 'query-if', 'query-ref',
                             'refuse', 'reject-proposal', 'request',
                             'request-when', 'request-whenever', 'subscribe',
                             'inform-if', 'proxy', 'propagate']
        
    protocols = ['fipa-request protocol', 'fipa-query protocol', 'fipa-request-when protocol',
                          'fipa-contract-net protocol']
    
    def __init__(self, performative=None):
        '''
            metodo de inicialização
        '''
        super(ACLMessage, self).__init__('ACLMessage', attrib = {'date' : datetime.now().strftime('%d/%m/%Y - %H:%M:%S:%f')})
                             
        self.append(ET.Element('performative'))
        self.append(ET.Element('sender'))
        self.append(ET.Element('receivers'))
        self.append(ET.Element('reply-to'))
        self.append(ET.Element('content'))
        self.append(ET.Element('language'))
        self.append(ET.Element('enconding'))
        self.append(ET.Element('ontology'))
        self.append(ET.Element('protocol'))
        self.append(ET.Element('conversationID'))
        self.append(ET.Element('reply-with'))
        self.append(ET.Element('in-reply-to'))
        self.append(ET.Element('reply-by'))
        
        if performative != None:
            if performative.lower() in self.performaives:
                self.performative = performative.lower()
                self.find('performative').text = self.performative
        
        self.conversationID = str(uuid1())
        self.find('conversationID').text = self.conversationID
        
        self.sender = None
        self.receivers = []
        self.reply_to = []
        self.content = None
        self.language = None
        self.encoding = None
        self.ontology = None
        self.protocol = None
        self.reply_with = None
        self.in_reply_to = None
        self.reply_by = None
    
    def setPerformative(self, data):
        '''
            Metodo que seta o parametro Performtive da mensagem ACL
        '''
        self.performative = data
        self.find('performative').text = str(data).lower()
        
    def setSender(self, data):
        if isinstance(data, AID):
            self.sender = data
            self.find('sender').text = str(self.sender.name)
        else:
            self.setSender(AID(name=data))
    
    def addReceiver(self, data):
        if isinstance(data, AID):
            self.receivers.append(data)
            receivers = self.find('receivers')
            receiver = ET.Element('receiver')
            receiver.text = str(data.name)
            receivers.append(receiver)
        else:
            self.addReceiver(AID(name=data))
    
    def addReply_to(self, data):
        if isinstance(data, AID):
            self.reply_to.append[data]
            reply_to = self.find('reply_to')
            receiver = ET.Element('receiver')
            receiver.text = str(data.name)
            reply_to.append(receiver)
        else:
            self.addReply_to(AID(name=data))
        
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
        self.conversationID = data
        self.find('conversationID').text = str(data)
    
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
        return ET.tostring(self)
               
    
    def asXML(self):
        domElement = minidom.parseString(ET.tostring(self))
        return domElement.toprettyxml()
        
    def __str__(self):
        '''
            returns a printable version of the message in ACL string representation
        '''

        p = '('

        p = p + str(self.performative) + '\n'
        
        if self.conversationID:
            p = p + ":conversationID " + self.conversationID + '\n'
            
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
            self.conversationID = aclmsg.find('conversationID').text
            self.find('conversationID').text = self.conversationID
        except:
            pass
        
        try:
            self.sender = AID(name = aclmsg.find('sender').text)
            self.find('sender').text = self.sender.name
        except:
            pass
        
        try:
            receivers = aclmsg.find('receivers').getchildren()
            
            for receiver in receivers:
                aid = AID(name=receiver.text)
                self.receivers.append(aid)
                r = ET.Element('receiver')
                r.text = aid.name
                self.find('receivers').append(r)
        except:
            pass
        
        try:
            receivers = aclmsg.find('reply-to').getchildren()
            
            for receiver in receivers:
                aid = AID(name=receiver.text)
                self.reply_to.append(aid)
                r = ET.Element('receiver')
                r.text = aid.name
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
    
    def createReply(self):
        '''
        Creates a reply for the message
        Duplicates all the message structures
        exchanges the 'from' AID with the 'to' AID
        '''

        message = ACLMessage()

        message.setPerformative(self.performative)
        
        if self.language:
            message.setLanguage(self.language)
        if self.ontology:
            message.setOntology(self.ontology)
        if self.protocol:
            message.setProtocol(self.protocol)
        if self.conversationID:
            message.setConversationId(self.conversationID)

        for i in self.reply_to:
            message.addReceiver(i)

        if not self.reply_to:
            message.addReceiver(self.sender)

        if self.reply_with:
            message.setIn_reply_to(self.reply_with)

        return message
    
if __name__ == '__main__':
    
    msg = ACLMessage()
    msg.setMsg('<?xml version="1.0" ?><ACLMessage date="19/03/2014 - 15:51:03:207172"><performative>inform</performative><sender>Lucas@localhost:7352</sender><receivers><receiver>Allana@localhost:5851</receiver></receivers><reply-to/><content>51A Feeder 21I5</content><language/><enconding/><ontology/><protocol/><conversationID/><reply-with/><in-reply-to/><reply-by/></ACLMessage>')
    #msg.setSender(AID(name='Lucas'))
    #msg.addReceiver(AID(name='Allana'))
    #msg.setContent('51A Feeder 21I5')
    #msg.ACLMessageRepresentation = ACLMessage.ACLMessageAsXML
    
    print msg.getMsg()
    print msg.sender
    print msg.receivers[0]