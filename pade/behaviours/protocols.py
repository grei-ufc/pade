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
    Protocols module
    --------------------

    This module implements the FIPA standard protocols:
    1. FipaRequestProtocol
    2. FipaContractNetProtocol
    3. FIPA_Subscribe_Protocol
"""

from twisted.internet import reactor
from pade.acl.messages import ACLMessage
from pade.acl.filters import Filter
from time import time


class Behaviour(object):

    """Class that states essential methods of a behaviour.
        All behaviours should inherit from this class.
    """

    def __init__(self, agent):
        """This method initializes the Behaviour class with an agent instance

            :param agent: agent instance that will execute the behaviours 
            established by the protocol

        """
        self.agent = agent
        self.timeout = 5

    def execute(self, message):
        """Executes the actual behaviour of the protocol
            for each type of messege received.
        """
        pass

    def timed_behaviour(self):
        """Used when the implemented protocol has restrictions
           of time, for example, the use of timeout
        """
        pass

    def on_start(self):
        """Always executed when the protocol is initialized
        """
        self.t1 = int(time())


class TimedBehaviour(Behaviour):
    """Class that implements timed behaviours
    """
    def __init__(self, agent, time):
        """ Initialize method
        """
        super(TimedBehaviour, self).__init__(agent)
        self.time = time

    def on_start(self):
        """This method overrides the on_start method from Behaviour class
            and implements aditional settings to the initialize method of TimedBehaviour behaviour.
        """
        Behaviour.on_start(self)
        self.timed_behaviour()

    def timed_behaviour(self):
        """This method is always used when the implemented behaviour 
            needs timed restrictions.
            In this case, it uses the twisted callLater method, which
            receives a method and delay as parameters to be executed

        """
        super(TimedBehaviour, self).timed_behaviour()

        reactor.callLater(self.time, self.on_time)

    def on_time(self):
        """This method executes the handle_all_proposes method if any 
            FIPA_CFP message sent by the agent does not get an answer.
        """
        reactor.callLater(self.time, self.on_time)


class FipaRequestProtocol(Behaviour):

    """This class implements the FipaRequestProtocol protocol,
        inheriting from the Behaviour class and implementing its methods.
    """

    def __init__(self, agent, message=None, is_initiator=True):
        """Inicializes the class that implements FipaRequestProtocol protocol

            :param agent: instance of the agent that will execute the protocol's
                         established behaviours.
            :param message: message to be sent by the agent when is_initiator
                         parameter is true.
            :param is_initiator: boolean type parameter that specifies if the 
                         protocol instance will act as Initiator or Participant.

        """
        super(FipaRequestProtocol, self).__init__(agent)

        self.is_initiator = is_initiator
        self.message = message

        self.filter_protocol = Filter()
        self.filter_protocol.set_protocol(ACLMessage.FIPA_REQUEST_PROTOCOL)

        self.filter_Request = Filter()
        self.filter_Request.set_performative(ACLMessage.REQUEST)

        self.filter_refuse = Filter()
        self.filter_refuse.set_performative(ACLMessage.REFUSE)

        self.filter_Agree = Filter()
        self.filter_Agree.set_performative(ACLMessage.AGREE)

        self.filter_failure = Filter()
        self.filter_failure.set_performative(ACLMessage.FAILURE)

        self.filter_inform = Filter()
        self.filter_inform.set_performative(ACLMessage.INFORM)

        if self.message is not None:
            self.filter_conversation_id = Filter()
            self.filter_conversation_id.set_conversation_id(self.message.conversation_id)

    def on_start(self):
        """
        This method overrides the on_start method from Behaviour class
            and implements aditional settings to the initialize method
            of FipaRequestProtocol protocol.
        """

        super(FipaRequestProtocol, self).on_start()

        if self.is_initiator and self.message != None:
            self.agent.send(self.message)

    def handle_request(self, message):
        """This method should be overridden when implementing a protocol.
            This method is always executed when the agent receives a 
            FIPA_REQUEST type message 

            :param message: FIPA-ACL message
        """
        pass

    def handle_refuse(self, message):
        """This method should be overridden when implementing a protocol.
            This method is always executed when the agent receives a 
            FIPA_REFUSE type message 

            :param message: FIPA-ACL message
        """
        pass

    def handle_agree(self, message):
        """This method should be overridden when implementing a protocol.
            This method is always executed when the agent receives a 
            FIPA_AGREE type message 

            :param message: FIPA-ACL message
        """
        pass

    def handle_failure(self, message):
        """This method should be overridden when implementing a protocol.
            This method is always executed when the agent receives a 
            FIPA_FAILURE type message 

            :param message: FIPA-ACL message
        """
        pass

    def handle_inform(self, message):
        """
        This method should be overridden when implementing a protocol.
            This method is always executed when the agent receives a 
            FIPA_IMFORM type message 

            :param message: FIPA-ACL message
        """
        pass

    def execute(self, message):
        """This method overrides the execute method from Behaviour class.
            The selection of the method to be executed after the receival
            of a message is implemented here.

            :param message: FIPA-ACL message
        """

        self.message = message

        if self.filter_protocol.filter(self.message):

            if self.filter_Request.filter(self.message):
                self.handle_request(message)

            elif self.filter_refuse.filter(self.message):
                self.handle_refuse(message)

            elif self.filter_Agree.filter(self.message):
                self.handle_agree(message)

            elif self.filter_failure.filter(self.message):
                self.handle_failure(message)

            elif self.filter_inform.filter(self.message):
                self.handle_inform(message)

            else:
                return
        else:
            return


class FipaContractNetProtocol(Behaviour):

    """This class implements the FipaContractNetProtocol protocol,
        inheriting from the Behaviour class and implementing its methods.
    """

    def __init__(self, agent, message=None, is_initiator=True):
        """
        Inicializes the class that implements FipaContractNetProtocol protocol.

            :param agent: instance of the agent that will execute the protocol's
                         established behaviours.
            :param message: message to be sent by the agent when is_initiator
                         parameter is true.
            :param is_initiator: boolean type parameter that specifies if the 
                         protocol instance will act as Initiator or Participant.
        """
        super(FipaContractNetProtocol, self).__init__(agent)

        self.is_initiator = is_initiator
        self.received_qty = 0

        self.proposes = []

        self.message = message

        self.filter_protocol = Filter()
        self.filter_protocol.set_protocol(ACLMessage.FIPA_CONTRACT_NET_PROTOCOL)

        self.filter_cfp = Filter()
        self.filter_cfp.set_performative(ACLMessage.CFP)

        self.filter_refuse = Filter()
        self.filter_refuse.set_performative(ACLMessage.REFUSE)

        self.filter_propose = Filter()
        self.filter_propose.set_performative(ACLMessage.PROPOSE)

        self.filter_accept_propose = Filter()
        self.filter_accept_propose.set_performative(ACLMessage.ACCEPT_PROPOSAL)

        self.filter_reject_propose = Filter()
        self.filter_reject_propose.set_performative(ACLMessage.REJECT_PROPOSAL)

        self.filter_failure = Filter()
        self.filter_failure.set_performative(ACLMessage.FAILURE)

        self.filter_inform = Filter()
        self.filter_inform.set_performative(ACLMessage.INFORM)

        if self.message is not None:
            self.filter_conversation_id = Filter()
            self.filter_conversation_id.set_conversation_id(self.message.conversation_id)

    def on_start(self):
        """This method overrides the on_start method from Behaviour class
            and implements aditional settings to the initialize method
            of FipaContractNetProtocol protocol.
        """
        super(FipaContractNetProtocol, self).on_start()

        if self.is_initiator and self.message is not None:

            if self.message.performative == ACLMessage.CFP:

                self.cfp_qty = len(self.message.receivers)
                self.received_qty = 0
                self.proposes = []
                self.agent.send(self.message)

                self.timed_behaviour()

    def handle_cfp(self, message):
        """This method should be overridden when implementing a protocol.
            This method is always executed when the agent receives a 
            FIPA_CFP type message 

            :param message: FIPA-ACL message
        """
        pass

    def handle_propose(self, message):
        """This method should be overridden when implementing a protocol.
            This method is always executed when the agent receives a 
            FIPA_PROPOSE type message 

            :param message: FIPA-ACL message
        """
        self.received_qty += 1
        if self.received_qty == self.cfp_qty:
            pass
            # delayed_calls = reactor.getDelayedCalls()
            # for call in delayed_calls:
            #     call.cancel()

    def handle_refuse(self, message):
        """This method should be overridden when implementing a protocol.
            This method is always executed when the agent receives a 
            FIPA_REFUSE type message 

            :param message: FIPA-ACL message
        """
        self.received_qty += 1
        if self.received_qty == self.cfp_qty:
            pass
            # delayed_calls = reactor.getDelayedCalls()
            # for call in delayed_calls:
            #     call.cancel()

    def handle_all_proposes(self, proposes):
        """This method should be overridden when implementing a protocol.
            This method is executed in two cases:
            *The quantity of answer received is equal to the quantity of
            requests received
            *The timeout is reached

            :param proposes: list containing the answers of the requests
            sent by the Initiator.
        """
        self.received_qty = 0

    def handle_inform(self, message):
        """This method should be overridden when implementing a protocol.
            This method is always executed when the agent receives a 
            FIPA_IMFORM type message 

            :param message: FIPA-ACL message
        """
        pass

    def handle_reject_propose(self, message):
        """This method should be overridden when implementing a protocol.
            This method is always executed when the agent receives a 
            FIPA_REJECT_PROPOSE type message 

            :param message: FIPA-ACL message
        """
        pass

    def handle_accept_propose(self, message):
        """This method should be overridden when implementing a protocol.
            This method is always executed when the agent receives a 
            FIPA_ACCEPT_PROPOSE type message 

            :param message: FIPA-ACL message
        """
        pass

    def timed_behaviour(self):
        """This method is always used when the implemented protocol 
            needs timed restrictions, for instance, the FipaContractNetProtocol.
            In this case, it uses the twisted callLater method, which
            receives a method and time delay as parameters to be executed
        """
        super(FipaContractNetProtocol, self).timed_behaviour()

        #reactor.callLater(self.timeout, self.execute_on_timeout)

    def execute_on_timeout(self):
        """This method executes the handle_all_proposes method if any 
            FIPA_CFP message sent by the agent does not get an answer.
        """

        self.handle_all_proposes(self.proposes)

    def execute(self, message):
        """This method overrides the execute method from Behaviour class.
            The selection of the method to be executed after the receival
            of a message is implemented here.

            :param message: FIPA-ACL message
        """

        super(FipaContractNetProtocol, self).execute(message)

        self.message = message

        if self.filter_protocol.filter(self.message):
            if self.filter_cfp.filter(self.message):
                if not self.is_initiator:
                    self.handle_cfp(message)

            elif self.filter_propose.filter(self.message):
                if self.is_initiator:
                    self.proposes.append(message)
                    self.handle_propose(message)

                    if self.received_qty == self.cfp_qty:
                        self.handle_all_proposes(self.proposes)

            elif self.filter_refuse.filter(self.message):
                if self.is_initiator:
                    self.proposes.append(message)
                    self.handle_refuse(message)

                    if self.received_qty == self.cfp_qty:
                        self.handle_all_proposes(self.proposes)

            elif self.filter_accept_propose.filter(self.message):
                if not self.is_initiator:
                    self.handle_accept_propose(message)

            elif self.filter_reject_propose.filter(self.message):
                if not self.is_initiator:
                    self.handle_reject_propose(message)

            elif self.filter_failure.filter(self.message):
                if self.is_initiator:
                    self.handle_failure(message)

            elif self.filter_inform.filter(self.message):
                if self.is_initiator:
                    self.handle_inform(message)

            else:
                return

        else:
            return


class FipaSubscribeProtocol(Behaviour):
    """This class implements the FipaSubscribeProtocol protocol,
        inheriting from the Behaviour class and implementing its methods.
    """

    def __init__(self, agent, message=None, is_initiator=True):
        """Initialize method
        """

        super(FipaSubscribeProtocol, self).__init__(agent)

        self.is_initiator = is_initiator
        self.message = message
        self.subscribers = set()

        self.filter_protocol = Filter()
        self.filter_protocol.set_protocol(ACLMessage.FIPA_SUBSCRIBE_PROTOCOL)

        self.filter_subscribe = Filter()
        self.filter_subscribe.set_performative(ACLMessage.SUBSCRIBE)

        self.filter_agree = Filter()
        self.filter_agree.set_performative(ACLMessage.AGREE)

        self.filter_inform = Filter()
        self.filter_inform.set_performative(ACLMessage.INFORM)

        self.filter_refuse = Filter()
        self.filter_refuse.set_performative(ACLMessage.REFUSE)

        self.filter_cancel = Filter()
        self.filter_cancel.set_performative(ACLMessage.CANCEL)

        self.filter_failure = Filter()
        self.filter_failure.set_performative(ACLMessage.FAILURE)

        if self.message is not None:
            self.filter_conversation_id = Filter()
            self.filter_conversation_id.set_conversation_id(self.message.conversation_id)

    def on_start(self):
        """his method overrides the on_start method from Behaviour class
            and implements aditional settings to the initialize method
            of FipaSubscribeProtocol protocol.
        """
        super(FipaSubscribeProtocol, self).on_start()


        if self.is_initiator and self.message != None:
            if self.message.performative == ACLMessage.SUBSCRIBE:
                self.agent.send(self.message)
                # self.timed_behaviour()

    def handle_subscribe(self, message):
        """
            handle_subscribe

        """
        pass

    def handle_agree(self, message):
        """
            handle_agree

        """
        pass

    def handle_refuse(self, message):
        """
            handle_refuse

        """
        pass

    def handle_inform(self, message):
        """
            handle_inform

        """
        pass

    def handle_cancel(self, message):
        """
            handle_cancel

        """
        pass

    def execute(self, message):
        """This method overrides the execute method from Behaviour class.
            The selection of the method to be executed after the receival
            of a message is implemented here.

            :param message: FIPA-ACL message
        """
        super(FipaSubscribeProtocol, self).execute(message)

        self.message = message

        if self.filter_protocol.filter(self.message):
            if self.filter_subscribe.filter(self.message):
                self.handle_subscribe(message)

            elif self.filter_cancel.filter(self.message):
                self.handle_cancel(message)

            elif self.filter_inform.filter(self.message):
                self.handle_inform(message)

            elif self.filter_agree.filter(self.message):
                self.handle_agree(message)

            elif self.filter_failure.filter(self.message):
                self.handle_failure(message)
            else:
                return

        else:
            return

    def register(self, aid):
        """register

        """
        self.subscribers.add(aid)

    def deregister(self, aid):
        """deregister

        """
        self.subscribers.remove(aid)

    def notify(self, message):
        """notify

        """
        for sub in self.subscribers:
            message.add_receiver(sub)
        self.agent.send(message)
