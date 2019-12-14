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
"""
    FIPA-ACL message creation and handling module
    -----------------------------------------------------

    This module contains a class which implements an ACLMessage
    type object. This object is the standard FIPA message used
    in the exchange of messages between agents.

"""

import xml.etree.ElementTree as ET
from xml.dom import minidom
from datetime import datetime
from uuid import uuid1
from pade.acl.aid import AID


class ACLMessage(ET.Element):
    """Class that implements a ACLMessage message type
    """

    ACCEPT_PROPOSAL = 'accept-proposal'
    AGREE = 'agree'
    CANCEL = 'cancel'
    CFP = 'cfp'
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
    FIPA_SUBSCRIBE_PROTOCOL = 'fipa-subscribe-protocol'

    performatives = ['accept-proposal', 'agree', 'cancel',
                    'cfp', 'call-for-proposal', 'confirm', 'disconfirm',
                    'failure', 'inform', 'not-understood',
                    'propose', 'query-if', 'query-ref',
                    'refuse', 'reject-proposal', 'request',
                    'request-when', 'request-whenever', 'subscribe',
                    'inform-if', 'proxy', 'propagate']

    protocols = ['fipa-request protocol', 'fipa-query protocol', 'fipa-request-when protocol',
                 'fipa-contract-net protocol']

    def __init__(self, performative=None):
        """ This method initializes a ACLMessage object when it is instantiated.

            :param performative: Type of the message to be created according to FIPA standard.
            It can be INFORM, CFP, AGREE, PROPOSE...
            All these types are attributes of ACLMessafe class.
        """
        super(ACLMessage, self).__init__('ACLMessage')

        self.append(ET.Element('performative'))
        self.append(ET.Element('system-message'))
        self.append(ET.Element('sender'))
        self.append(ET.Element('receivers'))
        self.append(ET.Element('reply-to'))
        self.append(ET.Element('content'))
        self.append(ET.Element('language'))
        self.append(ET.Element('enconding'))
        self.append(ET.Element('ontology'))
        self.append(ET.Element('protocol'))
        self.append(ET.Element('conversationID'))
        self.append(ET.Element('messageID'))
        self.append(ET.Element('reply-with'))
        self.append(ET.Element('in-reply-to'))
        self.append(ET.Element('reply-by'))
        self.append(ET.Element('reply-by'))
        self.append(ET.Element('datetime'))
        
        if performative != None:
            if performative.lower() in self.performatives:
                self.performative = performative.lower()
                self.find('performative').text = self.performative
        else:
            self.performative = None

        self.conversation_id = str(uuid1())
        self.find('conversationID').text = self.conversation_id

        self.messageID = str(uuid1())
        self.find('messageID').text = self.messageID

        self.datetime = datetime.now()
        datetime_tag = self.find('datetime')
        day = ET.Element('day')
        day.text = str(self.datetime.day)
        datetime_tag.append(day)
        month = ET.Element('month')
        month.text = str(self.datetime.month)
        datetime_tag.append(month)
        year = ET.Element('year')
        year.text = str(self.datetime.year)
        datetime_tag.append(year)
        hour = ET.Element('hour')
        hour.text = str(self.datetime.hour)
        datetime_tag.append(hour)
        minute = ET.Element('minute')
        minute.text = str(self.datetime.minute)
        datetime_tag.append(minute)
        second = ET.Element('second')
        second.text = str(self.datetime.second)
        datetime_tag.append(second)
        microsecond = ET.Element('microsecond')
        microsecond.text = str(self.datetime.microsecond)
        datetime_tag.append(microsecond)

        self.system_message = False
        self.datetime = None
        self.sender = None
        self.receivers = list()
        self.reply_to = list()
        self.content = None
        self.language = None
        self.encoding = None
        self.ontology = None
        self.protocol = None
        self.reply_with = None
        self.in_reply_to = None
        self.reply_by = None

    def set_performative(self, performative):
        """Method to set the Performative parameter of the ACL message.

           :param performative: performative type of the message.
           It can be any of the attributes of the ACLMessage class.
        """
        self.performative = performative
        self.find('performative').text = str(performative).lower()

    def set_system_message(self, is_system_message):
        self.system_message = is_system_message
        self.find('system-message').text = str(is_system_message)

    def set_datetime_now(self):
        self.datetime = datetime.now()
        datetime_tag = self.find('datetime')

        datetime_tag.find('day').text = str(self.datetime.day)
        datetime_tag.find('month').text = str(self.datetime.month)
        datetime_tag.find('year').text = str(self.datetime.year)
        datetime_tag.find('hour').text = str(self.datetime.hour)
        datetime_tag.find('minute').text = str(self.datetime.minute)
        datetime_tag.find('second').text = str(self.datetime.second)
        datetime_tag.find('microsecond').text = str(self.datetime.microsecond)

    def set_sender(self, aid):
        """Method to set the agent that will send the message.

        :param aid: AID type object that identifies the agent that will send the message.
        """
        if isinstance(aid, AID):
            self.sender = aid
            self.find('sender').text = str(self.sender.name)
        else:
            self.set_sender(AID(name=aid))

    def add_receiver(self, aid):
        """Method used to add recipients for the message being created.

        :param aid: AID type object that identifies the agent that will receive the message.
        """

        if isinstance(aid, AID):
            self.receivers.append(aid)
            receivers = self.find('receivers')
            receiver = ET.Element('receiver')
            receiver.text = str(aid.name)
            receivers.append(receiver)
        else:
            self.add_receiver(AID(name=aid))

    def add_reply_to(self, aid):
        """Method used to add the agents that should receive the answer of the message.

        :param aid: AID type object that identifies the agent that will receive the answer of this message.

        """
        if isinstance(aid, AID):
            self.reply_to.append[aid]
            reply_to = self.find('reply_to')
            receiver = ET.Element('receiver')
            receiver.text = str(aid.name)
            reply_to.append(receiver)
        else:
            self.add_reply_to(AID(name=aid))

    def set_content(self, data):
        self.content = data
        self.find('content').text = str(data)

    def set_language(self, data):
        self.language = data
        self.find('language').text = str(data)

    def set_encoding(self, data):
        self.encoding = data
        self.find('encoding').text = str(data)

    def set_ontology(self, data):
        self.ontology = data
        self.find('ontology').text = str(data)

    def set_protocol(self, data):
        self.protocol = data
        self.find('protocol').text = str(data)

    def set_conversation_id(self, data):
        self.conversation_id = data
        self.find('conversationID').text = str(data)

    def set_message_id(self):
        self.messageID = str(uuid1())
        self.find('messageID').text = self.messageID

    def set_reply_with(self, data):
        self.reply_with = data
        self.find('reply-with').text = str(data)

    def set_in_reply_to(self, data):
        self.in_reply_to = data
        self.find('in-reply-to').text = str(data)

    def set_reply_by(self, data):
        self.reply_by = data
        self.find('reply-by').text = str(data)

    def get_message(self):
        return ET.tostring(self)

    def as_xml(self):
        domElement = minidom.parseString(ET.tostring(self))
        return domElement.toprettyxml()

    def __str__(self):
        """
            returns a printable version of the message in ACL string representation
        """

        p = '('

        p = p + str(self.performative) + '\n'

        if self.conversation_id:
            p = p + ":conversationID " + self.conversation_id + '\n'

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

    def set_message(self, data):
        aclmsg = ET.fromstring(data)

        try:
            self.performative = aclmsg.find('performative').text
            self.find('performative').text = self.performative
        except:
            pass

        try:
            system_message = aclmsg.find('system-message').text
            if system_message == 'True':
                self.system_message = True
                self.find('system-message').text = system_message
            else:
                self.system_message = False
                self.find('system-message').text = system_message
        except:
            pass

        try:
            self.conversation_id = aclmsg.find('conversationID').text
            self.find('conversationID').text = self.conversation_id
        except:
            pass

        try:
            self.messageID = aclmsg.find('messageID').text
            self.find('messageID').text = self.messageID
        except:
            pass

        try:
            datetime_tag = aclmsg.find('datetime')
            my_datetime_tag = self.find('datetime')

            day = int(datetime_tag.findtext('day'))
            my_datetime_tag.find('day').text = str(day)
            month = int(datetime_tag.findtext('month'))
            my_datetime_tag.find('month').text = str(month)
            year = int(datetime_tag.findtext('year'))
            my_datetime_tag.find('year').text = str(year)
            hour = int(datetime_tag.findtext('hour'))
            my_datetime_tag.find('hour').text = str(hour)
            minute = int(datetime_tag.findtext('minute'))
            my_datetime_tag.find('minute').text = str(minute)
            second = int(datetime_tag.findtext('second'))
            my_datetime_tag.find('second').text = str(second)
            microsecond = int(datetime_tag.findtext('microsecond'))
            my_datetime_tag.find('microsecond').text = str(microsecond)

            self.datetime = datetime(year=year,
                                     month=month,
                                     day=day,
                                     hour=hour,
                                     minute=minute,
                                     second=second,
                                     microsecond=microsecond)
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

    def create_reply(self):
        """Creates a reply for the message
        Duplicates all the message structures
        exchanges the 'from' AID with the 'to' AID
        """

        message = ACLMessage()

        message.set_performative(self.performative)
        message.set_system_message(is_system_message=self.system_message)

        if self.language:
            message.set_language(self.language)
        if self.ontology:
            message.set_ontology(self.ontology)
        if self.protocol:
            message.set_protocol(self.protocol)
        if self.conversation_id:
            message.set_conversation_id(self.conversation_id)

        for i in self.reply_to:
            message.add_receiver(i)

        if not self.reply_to:
            message.add_receiver(self.sender)

        if self.reply_with:
            message.set_in_reply_to(self.reply_with)

        return message

    def __setstate__(self, state):
        self.__init__()
        self.__dict__.update(state)

    def __getstate__(self):
        # Copy the object's state from self.__dict__ which contains
        # all our instance attributes. Always use the dict.copy()
        # method to avoid modifying the original state.
        state = self.__dict__.copy()
        # Remove the unpicklable entries.
        return state

if __name__ == '__main__':

    msg = ACLMessage()
    msg.set_message('<?xml version="1.0" ?><ACLMessage"><performative>inform</performative><sender>Lucas@localhost:7352</sender><receivers><receiver>Allana@localhost:5851</receiver></receivers><reply-to/><content>51A Feeder 21I5</content><language/><enconding/><ontology/><protocol/><conversationID/><reply-with/><in-reply-to/><reply-by/></ACLMessage>')
    # msg.set_sender(AID(name='Lucas'))
    # msg.add_receiver(AID(name='Allana'))
    # msg.set_content('51A Feeder 21I5')
    # msg.ACLMessageRepresentation = ACLMessage.ACLMessageAsXML

    print(msg.get_message())
    print(msg.sender)
    print(msg.receivers[0])
