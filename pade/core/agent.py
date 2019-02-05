#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Framework para Desenvolvimento de Agentes Inteligentes PADE

# The MIT License (MIT)

# Copyright (c) 2015 Lucas S Melo

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.


"""
 Agent Implementing Module
 ----------------------------------

 This Python module is part of the communication and management
 infrastructure of agents, which forms the framework to create
 intelligent agents. This framework is based on the Python Twisted
 library to implement distributed systems.

 @author: Lucas S Melo
"""

from twisted.internet import protocol, reactor
from twisted.protocols.basic import LineReceiver

from pade.core.peer import PeerProtocol

from pade.acl.messages import ACLMessage
from pade.behaviours.protocols import Behaviour
from pade.behaviours.protocols import FipaRequestProtocol, FipaSubscribeProtocol
from pade.acl.aid import AID
from pade.misc.utility import display_message
from pickle import dumps, loads
import random
# Class that implements a protocol that enables
# the exchange of messages between agents.

class AgentProtocol(PeerProtocol):

    """This class implements the protocol to be followed by the
        agents during the communication process. The communication
        between agent and AMS agent, angent and Sniffer, and
        between agents is modeled in this class.

        This class does not stores persistent information, it
        is kept in the AgentFactory class.
    """

    def __init__(self, fact):
        """Initialize the attributes of the class.

        :param fact: fact instance of the protocol to be implemented
        """

        self.fact = fact

    def connectionMade(self):
        """This method is always executed when
        a conection is established between an agent
        in client mode and an agent in server mode.
        """
        # display_message(self.fact.agent_ref.aid.name, 'Connection Made')
        PeerProtocol.connectionMade(self)

    def connectionLost(self, reason):
        """This method executes anything when a connnection is lost.

        :param reason: Identifies the problem in the lost connection.
        """
        if self.message is not None:
            message = PeerProtocol.connectionLost(self, reason)

            # executes the behaviour Agent.react to the received
            # message.
            self.message = None
            self.fact.react(message)

    def send_message(self, message):
        PeerProtocol.send_message(self, message)

    def dataReceived(self, data):
        """This method is always executed when
        a new message is received by the agent,
        whether the agent is in client or server mode.

        :param line: message received by the agent.
        """
        PeerProtocol.dataReceived(self, data)

# Class that implements the ProtolFactory, which is the
# twisted standard for custom protocols.

class AgentFactory(protocol.ClientFactory):

    """This class implements the actions and attributes
    of the Agent protocol. Its main function is to store
    important information to the agent communication protocol.
    """

    def __init__(self, agent_ref):

        self.conn_count = 0
        self.agent_ref = agent_ref
        self.agent_ref.mosaik_connection = None
        self.debug = agent_ref.debug
        self.aid = agent_ref.aid  # stores the agent's identity.
        self.ams = agent_ref.ams  # stores the  ams agent's identity.

        self.messages = []  # stores the messages to be sent.

        # method that executes the agent's behaviour defined 
        # both by the user and by the System-PADE.
        self.react = agent_ref.react
        # method that executes the agent's behaviour defined both
        # by the user and by the System-PADE when the agent is initialised
        self.on_start = agent_ref.on_start
        # AID of AMS
        self.ams_aid = AID('ams@' + self.ams['name'] + ':' + str(self.ams['port']))
        # table stores the active agents, a dictionary with keys: name and
        # values: AID
        self.table = dict([('ams', self.ams_aid)])

    def buildProtocol(self, addr):
        """This method initializes the Agent protocol
        """
        protocol = AgentProtocol(self)
        return protocol

    def clientConnectionFailed(self, connector, reason):
        """This method is clled upon a failure 
        in the connection between client and server.
        """
        display_message(self.aid.name, 'Connection Failed...')
        print(reason)

    def clientConnectionLost(self, connector, reason):
        """This method is called when the connection between
        a client and server is lost.
        """
        pass


# Primitive Agent_ Class

class Agent_(object):

    """The Agent class establishes the essential functionalities of an agent, such as:
    1. Connection with AMS
    2. Initial configurations
    3. Message sending
    4. Behaviour adding
    5. abstract method to be used when implementing the initial behaviours
    6. abstract method to be used when implementing the agents' behaviour when they receive a message
    """

    def __init__(self, aid, debug=False):
        self.mosaik_connection = None
        self.aid = aid
        self.debug = debug
        
        # ALL: create a aid object with the aid of ams
        self.ams = dict()
        self.sniffer = dict()
        self.behaviours = list()
        self.system_behaviours = list()
        self.__messages = list()
        self.ILP = None

    @property
    def aid(self):
        return self.__aid

    @aid.setter
    def aid(self, value):
        if isinstance(value, AID):
            self.__aid = value
        else:
            raise ValueError('aid object type must be AID!')

    @property
    def debug(self):
        return self.__debug

    @debug.setter
    def debug(self, value):
        if isinstance(value, bool):
            self.__debug = value
        else:
            raise ValueError('debug object type must be bool')

    @property
    def ams(self):
        return self.__ams

    @ams.setter
    def ams(self, value):
        self.__ams = dict()
        if value == dict():
            self.__ams['name'] = 'localhost'
            self.__ams['port'] = 8000
        else:
            try:
                self.__ams['name'] = value['name']
                self.__ams['port'] = value['port']
            except (Exception, e):
                raise e

    @property
    def sniffer(self):
        return self.__sniffer

    @sniffer.setter
    def sniffer(self, value):
        self.__sniffer = dict()
        if value == dict():
            self.__sniffer['name'] = 'localhost'
            self.__sniffer['port'] = 8001
        else:
            try:
                self.__sniffer['name'] = value['name']
                self.__sniffer['port'] = value['port']
            except (Exception, e):
                raise e
    """
    #agentInstance will only be created after the session is created, not in the agent instantiation
    @property
    def agentInstance(self):
        return self.__agentInstance

    @agentInstance.setter
    def agentInstance(self, value):
        if isinstance(value, AgentFactory):
            self.__agentInstance = value
        else:
            raise ValueError(
                'agentInstance object type must be AgentFactory')
    """
    @property
    def behaviours(self):
        return self.__behaviours

    @behaviours.setter
    def behaviours(self, value):
        for v in value:
            if not issubclass(v.__class__, Behaviour):
                raise ValueError(
                    'behaviour must be a subclass of the Behaviour class!')
        else:
            self.__behaviours = value

    @property
    def system_behaviours(self):
        return self.__system_behaviours

    @system_behaviours.setter
    def system_behaviours(self, value):
        for v in value:
            if not issubclass(v.__class__, Behaviour):
                raise ValueError(
                    'behaviour must be a subclass of the Behaviour class!')
        else:
            self.__system_behaviours = value

    def react(self, message):
        """This method should be overriden and will
        be executed all the times the agent receives
        any type of data.

        :param message: ACLMessage
            received message
        """
        # this "for" executes all FIPA protocols associated to behaviours
        # implemented in this agent
        if message.system_message:
            for system_behaviour in self.system_behaviours:
                system_behaviour.execute(message)
        else:
            for behaviour in self.behaviours:
                behaviour.execute(message)

    def send(self, message):
        """This method sends an ACL message to the agents specified
        in the receivers parameter of the ACL message.
        """
        message.set_sender(self.aid)
        message.set_message_id()
        message.set_datetime_now()

        c = 0.0
        if len(message.receivers) >= 20:
            receivers = [message.receivers[i:i+20] for i in range(0, len(message.receivers), 20)]
            for r in receivers:
                reactor.callLater(c, self._send, message, r)
                c += 0.5
        else:
            self._send(message, message.receivers)

    def _send(self, message, receivers):
        # "for" iterates on the message receivers
        for receiver in receivers:
            for name in self.agentInstance.table:
                # "if" verifies if the receiver name is among the available agents
                if receiver.localname in name and receiver.localname != self.aid.localname:
                    # corrects the port and host parameters randomly generated when only a name
                    # is given as a identifier of a receiver.
                    receiver.setPort(self.agentInstance.table[name].port)
                    receiver.setHost(self.agentInstance.table[name].host)
                    # makes a connection to the agent and sends the message.
                    self.agentInstance.messages.append((receiver, message))
                    if self.debug:
                        print(('[MESSAGE DELIVERY]',
                               message.performative,
                               'FROM',
                               message.sender.name,
                               'TO',
                               message.receivers))
                    try:
                        reactor.connectTCP(self.agentInstance.table[
                                           name].host, self.agentInstance.table[name].port, self.agentInstance)
                    except:
                        self.agentInstance.messages.pop()
                        display_message(self.aid.name, 'Error delivery message!')
                    break
            else:
                if self.debug:
                    display_message(
                        self.aid.localname, 'Agent ' + receiver.name + ' is not active')
                else:
                    pass

    def call_later(self, time, method, *args):
        return reactor.callLater(time, method, *args)

    def send_to_all(self, message):
        """
        This method sends a broadcast message, in other words, it sends
        a message to all agents registered on the table of agents

        :param message: message to be sent to all agents registeres
        on the table of agents.
        """

        for agent_aid in self.agentInstance.table.values():
                message.add_receiver(agent_aid)

        self.send(message)

    def add_all(self, message):
        message.receivers = list()
        for agent_aid in self.agentInstance.table.values():
            if 'ams' not in agent_aid.localname:
                message.add_receiver(agent_aid)

    def on_start(self):
        """This method defines the initial behaviours 
        of an agent.
        """
        # This "for" adds the standard behaviours specified
        # by the user.
        for system_behaviour in self.system_behaviours:
            system_behaviour.on_start()
        
        reactor.callLater(2.0, self.__launch_agent_behaviours)
    
    def __launch_agent_behaviours(self):
        for behaviour in self.behaviours:
            behaviour.on_start()

    def pause_agent(self):
        """This method makes the agent stops listeing to its port
        """
        self.ILP.stopListening()

    def resume_agent(self):
        """This method resumes the agent after it has been pause. Still not working
        """
        print(self.system_behaviours,self.behaviours)
        self.on_start()
        self.ILP.startListening()

    def update_ams(self,ams):
        """This method instantiates the ams agent
        """
        self.ams = ams
        self.agentInstance = AgentFactory(agent_ref=self)
        


# PADE behaviours that compose the Agent class.

class SubscribeBehaviour(FipaSubscribeProtocol):
    """
        This class implements the behaviour of the 
        agent that identifies it to the AMS.
    """
    def __init__(self, agent, message):
        super(SubscribeBehaviour, self).__init__(agent,
                                                 message,
                                                 is_initiator=True)
    def handle_agree(self, message):
        display_message(self.agent.aid.name, 'Identification process done.')

    def handle_refuse(self, message):
        if self.agent.debug:
            display_message(self.agent.aid.name, message.content)

    def handle_inform(self, message):
        if self.agent.debug:
            display_message(self.agent.aid.name, 'Table update')
        self.agent.agentInstance.table = loads(message.content)


class CompConnection(FipaRequestProtocol):
    """
        This class implements the agent's behaviour
        that answers the solicitations the AMS
        makes to detect if the agent is connected or not. 
    """
    def __init__(self, agent):
        super(CompConnection, self).__init__(agent=agent,
                                             message=None,
                                             is_initiator=False)

    def handle_request(self, message):
        super(CompConnection, self).handle_request(message)
        if self.agent.debug:
            display_message(self.agent.aid.localname, 'request message received')
        reply = message.create_reply()
        reply.set_performative(ACLMessage.INFORM)
        reply.set_content('Im Live')
        reactor.callLater(random.uniform(0.0, 1.0), self.agent.send, reply)


# Main Agent Class

class Agent(Agent_):
    def __init__(self, aid, debug=False):
        super(Agent, self).__init__(aid=aid, debug=debug)
        
        self.comport_connection = CompConnection(self)        
        self.system_behaviours.append(self.comport_connection)

    def update_ams(self,ams):
        super(Agent,self).update_ams(ams)
        message = ACLMessage(ACLMessage.SUBSCRIBE)
        message.set_protocol(ACLMessage.FIPA_SUBSCRIBE_PROTOCOL)
        ams_aid = AID('ams@' + self.ams['name'] + ':' + str(self.ams['port']))
        message.add_receiver(ams_aid)
        message.set_content('IDENT')
        message.set_system_message(is_system_message=True)
        self.comport_ident = SubscribeBehaviour(self, message)
        self.system_behaviours.append(self.comport_ident)

    def react(self, message):
        super(Agent, self).react(message)

        if 'ams' not in message.sender.name and 'sniffer' not in self.aid.name:
            # sends the received message to Sniffer
            # building of the message to be sent to Sniffer.
            _message = ACLMessage(ACLMessage.INFORM)
            sniffer_aid = AID('sniffer@' + self.sniffer['name'] + ':' + str(self.sniffer['port']))
            _message.add_receiver(sniffer_aid)
            _message.set_content(dumps({
            'ref' : 'MESSAGE',
            'message' : message}))
            _message.set_system_message(is_system_message=True)
            self.send(_message)
