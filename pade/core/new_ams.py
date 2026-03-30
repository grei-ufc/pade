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
from pade.core.agent import Agent_
from pade.acl.messages import ACLMessage
from pade.acl.aid import AID
from pade.behaviours.protocols import TimedBehaviour, FipaRequestProtocol, FipaSubscribeProtocol
from pade.misc.utility import display_message
from pade.misc.data_logger import get_shared_session_id, logger

from pickle import dumps, loads
from datetime import datetime
import uuid
from terminaltables import AsciiTable

from twisted.internet.defer import inlineCallbacks
from twisted.internet import reactor

import random
import sys

# Behaviour that sends the connection verification messages.

class ComportSendConnMessages(TimedBehaviour):
    def __init__(self, agent, message, time):
        super(ComportSendConnMessages, self).__init__(agent, time)
        self.message = message

    def on_time(self):
        super(ComportSendConnMessages, self).on_time()
        self.agent.add_all(self.message)
        self.agent.send(self.message)
        if self.agent.debug:
            display_message(self.agent.aid.name, 'Checking connection...')

# Behaviour that verifies the answer time of the agents
# and decides whether to disconnect them or not.

class ComportVerifyConnTimed(TimedBehaviour):
    def __init__(self, agent, time):
        super(ComportVerifyConnTimed, self).__init__(agent, time)

    def on_time(self):
        super(ComportVerifyConnTimed, self).on_time()
        desconnect_agents = list()
        table = list([['agent', 'delta']])
        for agent_name, date in self.agent.agents_conn_time.items():
            now = datetime.now()
            delta = now - date
            table.append([agent_name, str(delta.total_seconds())])
            if delta.total_seconds() > 20.0:
                desconnect_agents.append(agent_name)
                self.agent.agentInstance.table.pop(agent_name)
                display_message(self.agent.aid.name, 'Agent {} disconnected.'.format(agent_name))    

        for agent_name in desconnect_agents:
            self.agent.agents_conn_time.pop(agent_name)

        if self.agent.debug:
            display_message(self.agent.aid.name, 'Calculating response time of the agents...')
            table = AsciiTable(table)
            print(table.table)


class CompConnectionVerify(FipaRequestProtocol):
    """FIPA Request Behaviour of the Clock agent.
    """
    def __init__(self, agent, message):
        super(CompConnectionVerify, self).__init__(agent=agent,
                                           message=message,
                                           is_initiator=True)
        

    def handle_inform(self, message):
        date = datetime.now()
        self.agent.agents_conn_time[message.sender.name] = date
        # Log da conexão
        logger.log_event(
            event_type="agent_connection_verified",
            agent_id=message.sender.name,
            data={"timestamp": date.isoformat()}
        )


class PublisherBehaviour(FipaSubscribeProtocol):
    """
    FipaSubscribe behaviour of Publisher type that implements
    a publisher-subscriber communication, which has the AMS agent
    as the publisher and the agents of the platform as subscribers.
    """

    STATE = 0

    def __init__(self, agent):
        super(PublisherBehaviour, self).__init__(agent,
                                                 message=None,
                                                 is_initiator=False)

    def handle_subscribe(self, message):
        sender = message.sender
        
        # New agent registration
        display_message(self.agent.aid.name, f'🔍 [AMS] NEW SUBSCRIBER: {sender.name}')
        
        # Check by name, not by object
        if sender.name in self.agent.agentInstance.table:
            display_message(self.agent.aid.name,
                            'Failure when Identifying agent ' + sender.name)

            # prepares the answer message
            reply = message.create_reply()
            reply.set_content(
                'There is already an agent with this identifier. Please, choose another one.')
            # sends the message
            self.agent.send(reply)
            
            # Error Log
            logger.log_event(
                event_type="agent_registration_failed",
                agent_id=sender.name,
                data={"reason": "duplicate_identifier"}
            )
        else:
            display_message(self.agent.aid.name, f'🔍 [AMS] Registering new agent: {sender.name}')
            
            # Registers the agent in the table of agents
            self.agent.agentInstance.table[sender.name] = sender
            # Registers the agent as a subscriber in the protocol.
            self.register(message.sender)
            # Registers the agent in the table of time.
            self.agent.agents_conn_time[sender.name] = datetime.now()

            # Current table log
            display_message(self.agent.aid.name, f'🔍 [AMS] Table NOW contains: {list(self.agent.agentInstance.table.keys())}')

            # Registered agent log
            logger.log_agent(
                agent_id=sender.name,
                session_id=self.agent.session_id,
                name=sender.name,
                state="Active"
            )
            
            display_message(
                self.agent.aid.name, 'Agent ' + sender.name + ' successfully identified.')

            # prepares and sends answer messages to the agent
            reply = message.create_reply()
            reply.set_performative(ACLMessage.AGREE)
            reply.set_content('Agent successfully identified.')
            self.agent.send(reply)

            # FORCES IMMEDIATE table notification
            display_message(self.agent.aid.name, f'🔍 [AMS] Forcing table notification NOW!')
            self.notify()

            # prepares and sends the update message to all registered agents.
            if self.STATE == 0:
                display_message(self.agent.aid.name, f'🔍 [AMS] Scheduling periodic notification in 10s')
                reactor.callLater(10.0, self.notify)
                self.STATE = 1

    def handle_cancel(self, message):
        self.deregister(self, message.sender)
        display_message(self.agent.aid.name, message.content)
        
        # Cancellation Log
        logger.log_event(
            event_type="agent_subscription_cancelled",
            agent_id=message.sender.name
        )

    def notify(self):
        """Sends table update to all agents."""
        from pade.misc.utility import display_message
        
        table_size = len(self.agent.agentInstance.table)
        display_message(self.agent.aid.name, f'🔍 [AMS] NOTIFY called! Sending table with {table_size} agents')
        
        if table_size == 0:
            display_message(self.agent.aid.name, f'🔍 [AMS] ⚠️ Empty table, nothing to send!')
            return
        
        agent_list = list(self.agent.agentInstance.table.keys())
        display_message(self.agent.aid.name, f'🔍 [AMS] Agents in table: {agent_list}')
        
        subscriber_count = len(self.subscribers)
        display_message(self.agent.aid.name, f'🔍 [AMS] Sending to {subscriber_count} subscribers: {[sub.name for sub in self.subscribers]}')
        
        # Serialize the table only once
        serialized = dumps(self.agent.agentInstance.table)
        display_message(self.agent.aid.name, f'🔍 [AMS] Serialized message size: {len(serialized)} bytes')
        
        # Sends to each subscriber individually
        for sub in self.subscribers:
            display_message(self.agent.aid.name, f'🔍 [AMS] Sending to {sub.name}')
            
            # Creates a NEW message for each receiver (instead of trying to copy)
            msg = ACLMessage(ACLMessage.INFORM)
            msg.set_protocol(ACLMessage.FIPA_SUBSCRIBE_PROTOCOL)
            msg.set_content(serialized)
            msg.set_system_message(is_system_message=True)
            msg.add_receiver(sub)
            
            self.agent.send(msg)

class CompVerifyRegister(FipaRequestProtocol):
    def __init__(self, agent):
        """FIPA Request Behaviour to verify the user registration"""
        super(CompVerifyRegister, self).__init__(agent=agent,
                                                 message=None,
                                                 is_initiator=False)

    def handle_request(self, message):
        super(CompVerifyRegister, self).handle_request(message)
        
        # CRITICAL FIX FOR PYTHON 3.12: Convert str to bytes before loads
        raw_content = message.content
        if isinstance(raw_content, str):
            raw_content = raw_content.encode('utf-8', errors='ignore')
            
        try:
            content = loads(raw_content)
        except Exception as e:
            display_message(self.agent.aid.name, f'Error decoding validation request: {e}')
            content = {} # Fallback
            
        display_message(self.agent.aid.name,
                        'Validating agent ' + message.sender.name + ' session.')


class AMS(Agent_):
    """This is the class that implements the AMS agent."""

    agents = list()
    ams_debug = False

    def __init__(self, host='localhost', port=8000, main_ams=True, debug=False):
        self.session_id = get_shared_session_id()
        self.ams = {'name': host, 'port': port}
        self.ams_aid = AID('ams@' + str(host) + ':' + str(port))
        
        super(AMS, self).__init__(self.ams_aid, debug=debug)
        self.ams = {'name': str(host), 'port': str(port)}
        super(AMS, self).update_ams(self.ams)
        
        self.host = host
        self.port = port
        self.main_ams = main_ams
        self.agents_conn_time = dict()
        
        # AMS Initialization Log
        logger.log_event(
            event_type="ams_initialized",
            data={
                "host": host,
                "port": port,
                "session_id": self.session_id
            }
        )

        self.comport_ident = PublisherBehaviour(self)

        # message to check the connection.
        message = ACLMessage(ACLMessage.REQUEST)
        message.set_protocol(ACLMessage.FIPA_REQUEST_PROTOCOL)
        self.add_all(message)
        message.set_content('CONNECTION')
        message.set_system_message(is_system_message=True)

        self.comport_conn_verify = CompConnectionVerify(self, message)
        self.comport_send_conn_messages = ComportSendConnMessages(self, message, 10.0)
        self.comport_conn_verify_timed = ComportVerifyConnTimed(self, 20.0)
        self.comport_conn_verify_reg = CompVerifyRegister(self)

        self.system_behaviours.append(self.comport_ident)
        self.system_behaviours.append(self.comport_conn_verify)
        self.system_behaviours.append(self.comport_send_conn_messages)
        self.system_behaviours.append(self.comport_conn_verify_timed)
        self.system_behaviours.append(self.comport_conn_verify_reg)
        self.on_start()

    def react(self, message):
        super(AMS, self).react(message)

    def _initialize_session(self):
        """Inicializa a sessão sem banco de dados."""
        display_message('AMS', f'Initializing session: {self.session_id}')
        
        # Session Log
        logger.log_session(
            session_id=self.session_id,
            name=f"AMS_Session_{self.session_id}",
            state="Active"
        )
        
        # Starts the Twisted server
        reactor.listenTCP(self.aid.port, self.agentInstance)
        
        display_message('AMS', f'AMS service running on {self.host}:{self.port}')

    def on_agent_registered(self, agent_name):
        """Callback when an agent is registered."""
        logger.log_event(
            event_type="agent_registered",
            agent_id=agent_name,
            data={"session_id": self.session_id}
        )


if __name__ == '__main__':
    if len(sys.argv) < 4:
        print("Usage: python new_ams.py <username> <email> <password> <port>")
        print("Note: username, email, password are kept for compatibility but not used in webless version")
        sys.exit(1)
    
    display_message('AMS', 'Initializing PADE AMS service...')
    
    port = int(sys.argv[4])
    ams = AMS(port=port)
    
    # Initializes the session (without database)
    ams._initialize_session()
    
    reactor.callLater(0.1,
                      display_message,
                      f'ams@{ams.host}:{ams.port}',
                      'PADE AMS service running right now....')
    
    # Service Start Log
    logger.log_event(
        event_type="ams_service_started",
        data={
            "host": ams.host,
            "port": ams.port,
            "session_id": ams.session_id
        }
    )
    
    reactor.run()
