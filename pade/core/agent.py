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

Agent Implementing Module
-------------------------

This Python module is part of the communication and management
infrastructure of agents, which forms the framework to create
intelligent agents. This framework is based on the Python Twisted
library to implement distributed systems.

@author: Lucas S Melo
"""

from twisted.internet import protocol, reactor

from pade.core.peer import PeerProtocol
from pade.acl.messages import ACLMessage
from pade.behaviours.protocols import Behaviour
from pade.behaviours.protocols import FipaRequestProtocol, FipaSubscribeProtocol
from pade.acl.aid import AID
from pade.misc.utility import display_message

from pickle import dumps, loads
import random


class AgentProtocol(PeerProtocol):
    """This class implements the protocol to be followed by the
    agents during the communication process. The communication
    between agent and AMS agent, angent and Sniffer, and
    between agents is modeled in this class.
    
    This class does not stores persistent information, it
    is kept in the AgentFactory class.
    
    Attributes
    ----------
    fact : factory protocol
        Description
    message : ACLMessage
        Message object in the FIPA-ACL standard
    """

    def __init__(self, fact):
        """Init AgentProtocol class
        
        Parameters
        ----------
        fact : factory protocol
            instance of AgentFactory
        """
        self.fact = fact


    def connectionMade(self):
        """This method is always executed when
        a conection is established between an agent
        in client mode and an agent in server mode.
        Now, nothing is made here.
        """
        PeerProtocol.connectionMade(self)

    def connectionLost(self, reason):
        """This method is always executede when a connnection is lost.
        
        Parameters
        ----------
        reason : twisted exception
            Identifies the problem in the lost connection.
        """
        if self.message is not None:
            message = PeerProtocol.connectionLost(self, reason)
            self.message = None
            # executes the behaviour Agent.react to the received message.
            self.fact.react(message)

    def send_message(self, message):
        """This method call the functionality send_message from
        the peer protocol 
        
        Parameters
        ----------
        message : ACLMessage
            Message object in the FIPA-ACL standard
        """
        PeerProtocol.send_message(self, message)

    def dataReceived(self, data):
        """This method is always executed when
        a new data is received by the agent,
        whether the agent is in client or server mode.

        Parameters
        ----------
        data : bytes
            some data received by the agent.
        """
        PeerProtocol.dataReceived(self, data)


class AgentFactory(protocol.ClientFactory):

    """This class implements the actions and attributes
    of the Agent protocol. Its main function is to store
    important information to the agent communication protocol.
    
    Attributes
    ----------
    agent_ref : Agent
        Agent object
    aid : AID
        Agent AID
    ams : dictionary
        A dictionary of form: {'name': ams_IP, 'port': ams_port}
    ams_aid : AID
        AID of AMS
    conn_count : int
        Number of active connections
    debug : Boolean
        If True activate the debug mode
    messages : list
        List of messages to be sent to another agents
    on_start : method
        method that executes the agent's behaviour defined both
        by the user and by the System-PADE when the agent is initialised
    react : method
        method that executes the agent's behaviour defined 
        both by the user and by the System-PADE.
    table : dictionary
        table stores the active agents, a dictionary with keys: name and
        values: AID
    """

    def __init__(self, agent_ref):
        """Init the AgentFactory class
        
        Parameters
        ----------
        agent_ref : Agent
            agent object instance
        """
        self.conn_count = 0
        self.agent_ref = agent_ref
        self.agent_ref.mosaik_connection = None
        self.debug = agent_ref.debug
        self.aid = agent_ref.aid  # stores the agent's identity.
        self.ams = agent_ref.ams  # stores the  ams agent's identity.
        self.messages = []
        self.react = agent_ref.react
        self.on_start = agent_ref.on_start
        self.ams_aid = AID('ams@' + self.ams['name'] + ':' + str(self.ams['port']))
        self.table = dict([('ams', self.ams_aid)])

    def buildProtocol(self, addr):
        """This method initializes the Agent protocol
        
        Parameters
        ----------
        addr : TYPE
            Description
        
        Returns
        -------
        AgentProtocol
            return a protocol instance
        """
        protocol = AgentProtocol(self)
        return protocol

    def clientConnectionFailed(self, connector, reason):
        """This method is called upon a failure 
        in the connection between client and server.
        
        Parameters
        ----------
        connector : TYPE
            Description
        reason : TYPE
            Description
        """
        pass

    def clientConnectionLost(self, connector, reason):
        """This method is called when the connection between
        a client and server is lost.
        
        Parameters
        ----------
        connector : TYPE
            Description
        reason : TYPE
            Description
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
    
    Attributes
    ----------
    agentInstance : Agent
        Agent instance
    aid : AID
        Agent AID
    ams : dictionary
        A dictionary with AMS information {'name': ams_IP, 'port': ams_port}
    behaviours : list
        Agent's behaviours list
    debug : boollean
        if True activate the debug mode
    ILP : TYPE
        Description
    mosaik_connection : mosaik conn class object
        an object that is instantiated if a mosaik session is implemented
    sniffer : dictionary
        Sniffer address
    system_behaviours : list
        List of PADE system's behaviours
    """

    def __init__(self, aid, debug=False):
        """Initialization
        
        Parameters
        ----------
        aid : AID
            Agent AID
        debug : bool, optional
            Description
        """
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
        """Summary
        
        Returns
        -------
        TYPE
            Description
        """
        return self.__aid

    @aid.setter
    def aid(self, value):
        """AID setter
        """
        if isinstance(value, AID):
            self.__aid = value
        else:
            raise ValueError('aid object type must be AID!')

    @property
    def debug(self):
        """Summary
        """
        return self.__debug

    @debug.setter
    def debug(self, value):
        """Debug
        """
        if isinstance(value, bool):
            self.__debug = value
        else:
            raise ValueError('debug object type must be bool')

    @property
    def ams(self):
        """AMS
        """
        return self.__ams

    @ams.setter
    def ams(self, value):
        """AMS
        """
        self.__ams = dict()
        if value == dict():
            self.__ams['name'] = 'localhost'
            self.__ams['port'] = 8000
        else:
            try:
                self.__ams['name'] = value['name']
                self.__ams['port'] = value['port']
            except Exception as e:
                raise e

    @property
    def sniffer(self):
        """Sniffer
        """
        return self.__sniffer

    @sniffer.setter
    def sniffer(self, value):
        """Sniffer
        """
        self.__sniffer = dict()
        if value == dict():
            self.__sniffer['name'] = 'localhost'
            self.__sniffer['port'] = 8001
        else:
            try:
                self.__sniffer['name'] = value['name']
                self.__sniffer['port'] = value['port']
            except Exception as e:
                raise e

    @property
    def behaviours(self):
        """Summary
        
        Returns
        -------
        TYPE
            Description
        """
        return self.__behaviours

    @behaviours.setter
    def behaviours(self, value):
        """Summary
        
        Parameters
        ----------
        value : TYPE
            Description
        
        Raises
        ------
        ValueError
            Description
        """
        for v in value:
            if not issubclass(v.__class__, Behaviour):
                raise ValueError(
                    'behaviour must be a subclass of the Behaviour class!')
        else:
            self.__behaviours = value

    @property
    def system_behaviours(self):
        """Summary
        
        Returns
        -------
        TYPE
            Description
        """
        return self.__system_behaviours

    @system_behaviours.setter
    def system_behaviours(self, value):
        """Summary
        
        Parameters
        ----------
        value : TYPE
            Description
        
        Raises
        ------
        ValueError
            Description
        """
        for v in value:
            if not issubclass(v.__class__, Behaviour):
                raise ValueError(
                    'behaviour must be a subclass of the Behaviour class!')
        else:
            self.__system_behaviours = value

    def react(self, message):
        """
        Processes messages received by the agent.
        """
        from pade.misc.utility import format_message_content, display_message
        from pade.misc.data_logger import logger
        from pickle import dumps
        
        # Safe sender extraction
        sender_obj = getattr(message, 'sender', None)
        sender_name = getattr(sender_obj, 'name', '') if sender_obj else ""
        
        # Keep message-level telemetry in events.csv only. The Sniffer is the
        # single source of truth for messages.csv to avoid duplicate rows.
        is_system = getattr(message, 'system_message', False)
        if not is_system and 'ams' not in sender_name:
            try:
                logger.log_event(
                    event_type="message_received",
                    agent_id=self.aid.name,
                    data={
                        "message_id": str(getattr(message, 'messageID', '') or ""),
                        "conversation_id": str(getattr(message, 'conversation_id', '') or ""),
                        "performative": str(getattr(message, 'performative', '') or ""),
                        "sender": str(sender_name),
                    },
                )
            except Exception as e:
                display_message(self.aid.name, f'⚠️ LOGGER ERROR (REACT): {e}')
        
        # Formats the content for safe terminal display
        formatted_content = format_message_content(getattr(message, 'content', ''))
        
        # Log the received message (only in debug mode)
        if self.debug:
            display_message(self.aid.name, f'📨 Mensagem: {formatted_content}')
        
        # Normal message processing
        if is_system:
            for system_behaviour in self.system_behaviours:
                system_behaviour.execute(message)
        else:
            for behaviour in self.behaviours:
                behaviour.execute(message)

        if 'ams' not in sender_name and 'sniffer' not in self.aid.name:
            _message = ACLMessage(ACLMessage.INFORM)
            sniffer_aid = AID('sniffer@' + self.sniffer['name'] + ':' + str(self.sniffer['port']))
            _message.add_receiver(sniffer_aid)
            _message.set_content(dumps({'ref' : 'MESSAGE', 'message' : message}))
            _message.set_system_message(is_system_message=True)
            self.send(_message)

    def send(self, message):
        """This method calls the method self._send to sends 
        an ACL message to the agents specified in the receivers
        """
        message.set_sender(self.aid)
        
        # Shielding against the absence of functions in the message object
        if hasattr(message, 'set_message_id'):
            message.set_message_id()
        if hasattr(message, 'set_datetime_now'):
            message.set_datetime_now()

        from pade.misc.data_logger import logger
        from twisted.internet import reactor
        
        sender_obj = getattr(message, 'sender', None)
        sender_name = getattr(sender_obj, 'name', '') if sender_obj else ""
        
        # Keep outbound telemetry in events.csv only. The Sniffer writes the
        # canonical rows to messages.csv after intercepting delivered messages.
        is_system = getattr(message, 'system_message', False)
        if not is_system and 'ams' not in sender_name:
            recvs_list = getattr(message, 'receivers', [])
            logger.log_event(
                event_type="message_sent",
                agent_id=self.aid.name,
                data={
                    "message_id": str(getattr(message, 'messageID', '') or ""),
                    "conversation_id": str(getattr(message, 'conversation_id', '') or ""),
                    "performative": str(getattr(message, 'performative', '') or ""),
                    "receivers": [getattr(r, 'name', str(r)) for r in recvs_list],
                },
            )

        c = 0.0
        receivers_list = getattr(message, 'receivers', [])
        if len(receivers_list) >= 20:
            receivers_chunks = [receivers_list[i:i+20] for i in range(0, len(receivers_list), 20)]
            for r in receivers_chunks:
                reactor.callLater(c, self._send, message, r)
                c += 0.5
        else:
            self._send(message, receivers_list)

    def _send(self, message, receivers):
        """This method effectively sends the message to receivers
        by connecting the receiver and sender sockets in a network
        
        Parameters
        ----------
        message : ACLMessage
            Message to be sent
        receivers : list
            List of receivers agents
        """
        from pade.misc.utility import display_message
        
        # "for" iterates on the message receivers
        for receiver in receivers:
            found = False
            for name in self.agentInstance.table:
                # "if" verifies if the receiver name is among the available agents
                if receiver.localname in name and receiver.localname != self.aid.localname:
                    found = True
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
                               receiver.name))
                    try:
                        reactor.connectTCP(self.agentInstance.table[
                                           name].host, self.agentInstance.table[name].port, self.agentInstance)
                    except Exception as e:
                        self.agentInstance.messages.pop()
                        display_message(self.aid.name, f'Error delivery message: {e}')
                    break
            
            if not found:
                if self.debug:
                    display_message(self.aid.localname, 'Agent ' + receiver.name + ' is not active')

    def call_later(self, time, method, *args):
        """Call a method after some time delay
        
        Parameters
        ----------
        time : float
            time delay
        method : method
            a callback
        *args
            callback args
        """
        return reactor.callLater(time, method, *args)

    def send_to_all(self, message):
        """This method sends a broadcast message, in other words, it sends
        a message to all agents registered on the table of agents

        Parameters
        ----------
        message : ACLMessage
            message to be sent to all agents registeres on the table
            of agents.
        """

        for agent_aid in self.agentInstance.table.values():
                message.add_receiver(agent_aid)

        self.send(message)

    def add_all(self, message):
        """Add all registered agents in the receivers list message
        
        Parameters
        ----------
        message : ACLMessage
            Some message
        """
        message.receivers = list()
        for agent_aid in self.agentInstance.table.values():
            if 'ams' not in agent_aid.localname:
                message.add_receiver(agent_aid)

    def on_start(self):
        """This method defines the initial behaviours 
        of an agent.
        """

        # This loop adds the standard behaviours specified
        # by the user.
        for system_behaviour in self.system_behaviours:
            system_behaviour.on_start()
        
        reactor.callLater(2.0, self.__launch_agent_behaviours)
    
    def __launch_agent_behaviours(self):
        """Aux method to send behaviours
        """
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
        
        Parameters
        ----------
        ams : dictionary
            AMS dictionary {'name': ams_IP, 'port': ams_port}
        """
        self.ams = ams
        self.agentInstance = AgentFactory(agent_ref=self)

# ===========================================================
# This are the PADE System behaviours
# ===========================================================

class SubscribeBehaviour(FipaSubscribeProtocol):
    """
    This class implements the behaviour of the 
    agent that identifies it to the AMS.
    """
    def __init__(self, agent, message):
        """Summary
        
        Parameters
        ----------
        agent : TYPE
            Description
        message : TYPE
            Description
        """
        super(SubscribeBehaviour, self).__init__(agent,
                                                 message,
                                                 is_initiator=True)
    def handle_agree(self, message):
        """Summary
        
        Parameters
        ----------
        message : TYPE
            Description
        """
        # display_message(self.agent.aid.name, 'Identification process done.')
        pass

    def handle_refuse(self, message):
        """Summary
        
        Parameters
        ----------
        message : TYPE
            Description
        """
        if self.agent.debug:
            display_message(self.agent.aid.name, message.content)

    def handle_inform(self, message):
        """Summary - Versão silenciosa para propagação da tabela
        
        Parameters
        ----------
        message : TYPE
            Description
        """
        from pade.misc.utility import display_message
        
        try:
            table = loads(message.content)
            # Updates the local table
            self.agent.agentInstance.table = table
        except Exception as e:
            display_message(self.agent.aid.name, f'🔍 [SUBSCRIBE_AGENT] ERROR deserializing: {e}')
            import traceback
            traceback.print_exc()


class CompConnection(FipaRequestProtocol):
    """
    This class implements the agent's behaviour
    that answers the solicitations the AMS
    makes to detect if the agent is connected or not. 
    """
    def __init__(self, agent):
        """Summary
        
        Parameters
        ----------
        agent : TYPE
            Description
        """
        super(CompConnection, self).__init__(agent=agent,
                                             message=None,
                                             is_initiator=False)

    def handle_request(self, message):
        """Summary
        
        Parameters
        ----------
        message : TYPE
            Description
        """
        super(CompConnection, self).handle_request(message)
        reply = message.create_reply()
        reply.set_performative(ACLMessage.INFORM)
        reply.set_content('Im Live')
        reactor.callLater(random.uniform(0.0, 1.0), self.agent.send, reply)


# Main Agent Class

class Agent(Agent_):

    """Summary
    
    Attributes
    ----------
    comport_connection : TYPE
        Description
    comport_ident : TYPE
        Description
    """
    
    def __init__(self, aid, debug=False):
        """Summary
        
        Parameters
        ----------
        aid : TYPE
            Description
        debug : bool, optional
            Description
        """
        super(Agent, self).__init__(aid=aid, debug=debug)
        
        self.comport_connection = CompConnection(self)        
        self.system_behaviours.append(self.comport_connection)
        self._identification_sent = False  # Flag to prevent duplicate identification

    def update_ams(self, ams):
        """Summary
        
        Parameters
        ----------
        ams : TYPE
            Description
        """
        # FIX: Prevents duplicate identification sending
        if hasattr(self, '_identification_sent') and self._identification_sent:
            return
        
        super(Agent, self).update_ams(ams)
        message = ACLMessage(ACLMessage.SUBSCRIBE)
        message.set_protocol(ACLMessage.FIPA_SUBSCRIBE_PROTOCOL)
        ams_aid = AID('ams@' + self.ams['name'] + ':' + str(self.ams['port']))
        message.add_receiver(ams_aid)
        message.set_content('IDENT')
        message.set_system_message(is_system_message=True)
        self.comport_ident = SubscribeBehaviour(self, message)
        self.system_behaviours.append(self.comport_ident)
        self._identification_sent = True  # Marca como enviado

    def react(self, message):
        """
        Processes messages received by the agent.
        """
        super(Agent, self).react(message)
