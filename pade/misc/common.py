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
 Utility Module
 --------------------

 This Python module provides configuration methods of twisted loop
 where the agents will be executed.

 @author: lucas
"""

from twisted.internet import reactor

from pade.core.new_ams import AMS
from pade.core.agent import Agent
from pade.acl.aid import AID
from pade.acl.messages import ACLMessage
from pade.behaviours.protocols import FipaRequestProtocol
from pade.misc.data_logger import logger

import multiprocessing
import threading
import uuid
import datetime
from pickle import dumps, loads


class PadeSession(object):
    """
    Simplified session manager without database dependency.
    """
    
    def __init__(self, name=None, ams=None, remote_ams=False):
        self.agents = list()
        self.users = list()
        self.remote_ams = remote_ams

        if name is not None:
            self.name = name
        else:
            self.name = str(uuid.uuid1())[:13]

        if ams is not None:
            self.ams = ams
        else:
            self.ams = {'name': 'localhost', 'port': 8000}
        
        # Session creation log
        logger.log_session(
            session_id=self.name,
            name=f"PadeSession_{self.name}",
            state="created"
        )

    def add_agent(self, agent):
        """Add an agent to the session."""
        self.agents.append(agent)
        logger.log_event(
            event_type="agent_added_to_session",
            agent_id=agent.aid.name if hasattr(agent, 'aid') else "unknown",
            data={"session_name": self.name}
        )

    def add_all_agents(self, agents):
        """Add multiple agents to the session."""
        self.agents.extend(agents)
        logger.log_event(
            event_type="agents_added_to_session",
            data={
                "session_name": self.name,
                "agent_count": len(agents)
            }
        )

    def register_user(self, username, email, password):
        """
        Register a user (kept for compatibility).
        In webless version, this just logs the action.
        """
        self.users.append({
            'username': username, 
            'email': email, 
            'password': password  # Not used in webless version
        })
        
        logger.log_event(
            event_type="user_registered",
            data={
                "session_name": self.name,
                "username": username,
                "email": email
            }
        )

    def log_user_in_session(self, username, email, password):
        """
        Log user in session (kept for compatibility).
        In webless version, this just logs the action.
        """
        self.user_login = {
            'username': username,
            'email': email,
            'password': password
        }
        
        logger.log_event(
            event_type="user_logged_in",
            data={
                "session_name": self.name,
                "username": username
            }
        )

    def _initialize_session(self):
        """Initialize session without database."""
        # Session initialization log
        logger.log_event(
            event_type="session_initialized",
            data={
                "session_name": self.name,
                "ams_host": self.ams['name'],
                "ams_port": self.ams['port'],
                "agent_count": len(self.agents)
            }
        )
        
        # Starts AMS
        ams_agent = AMS(
            host=self.ams['name'],
            port=self.ams['port'],
            debug=False
        )
        
        # Initializes AMS session (without database)
        ams_agent._initialize_session()
        
        return ams_agent

    def start_loop(self, ams_debug=False, multithreading=False):
        """
        Runs twisted loop for the session.
        """
        # Loop start log
        logger.log_event(
            event_type="session_loop_started",
            data={
                "session_name": self.name,
                "ams_debug": ams_debug,
                "multithreading": multithreading
            }
        )
        
        if self.remote_ams:
            # For remote sessions (simplified without complex validation)
            logger.log_event(
                event_type="remote_session_started",
                data={"session_name": self.name}
            )
            
            # Starts agents
            self._start_agents()
            reactor.run()
        else:
            # Local session
            ams_agent = self._initialize_session()
            
            # Starts agents
            self._start_agents()
            
            reactor.run()

    def _start_agents(self):
        """Start all agents in the session."""
        i = 1.0
        for agent in self.agents:
            reactor.callLater(i, self._listen_agent, agent)
            i += 0.1
            
            # Started agent log
            logger.log_event(
                event_type="agent_started_in_session",
                agent_id=agent.aid.name if hasattr(agent, 'aid') else "unknown",
                data={
                    "session_name": self.name,
                    "delay": i
                }
            )

    def _listen_agent(self, agent):
        """Connect agent to AMS and start listening."""
        # Connects agent to AMS
        agent.update_ams(self.ams)
        agent.on_start()
        # Connects agent to port used in communication
        ILP = reactor.listenTCP(agent.aid.port, agent.agentInstance)
        agent.ILP = ILP


class AgentProcess(multiprocessing.Process):
    """
    Process to run an agent (kept for compatibility).
    """
    def __init__(self, agent, ams, delay):
        self.agent = agent
        self.ams = ams
        self.delay = delay
        multiprocessing.Process.__init__(self)

    def run(self):
        time.sleep(self.delay)
        self.agent.update_ams(self.ams)
        self.agent.on_start()
        ILP = reactor.listenTCP(self.agent.aid.port, self.agent.agentInstance)
        self.agent.ILP = ILP


# Note: The CompRegisterUser and ValidadeUserAgent classes were removed
# because they depended on the web authentication system that no longer exists.
# If necessary in the future, they can be reimplemented in a simplified way.