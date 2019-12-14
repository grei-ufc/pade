"""Framework for Intelligent Agents Development - PADE

The MIT License (MIT)

Copyright (c) 2019 Lucas S Melo

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

from pade.acl.aid import AID
from pade.acl.messages import ACLMessage

class Filter():
    '''
        This class instantiates a filter object. The filter has the purpose of 
        selecting messages with pre established attributes in the filter object
    '''
    def __init__(self):
        self.conversation_id = None
        self.sender = None
        self.performative = None
        self.protocol = None
    
    def set_sender(self, aid):
        self.sender = aid
        
    def set_performative(self, performative):
        self.performative = performative
    
    def set_conversation_id(self, conversation_id):
        self.conversation_id = conversation_id
    
    def set_protocol(self, protocol):
        self.protocol = protocol
    
    def filter(self, message):
        state = True
        
        if self.conversation_id != None and self.conversation_id != message.conversation_id:
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
    message.set_sender(AID('john'))
    message.add_receiver('mary')
    message.set_protocol(ACLMessage.FIPA_REQUEST_PROTOCOL)
    
    filtro = Filter()
    filtro.set_protocol(ACLMessage.FIPA_REQUEST_PROTOCOL)
    
    if filtro.filter(message):
        print(message.as_xml())
    else:
        print('The message was blocked by the protocol.')
