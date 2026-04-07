#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Timed Hello World in PADE - Python 3.12.11 version with CSV logging
Adapted by Douglas Barros on March 4, 2026

This example demonstrates the use of TimedBehaviour for periodic actions.
Agents display "Hello World!" every 1 second.
"""

from pade.misc.utility import display_message, start_loop
from pade.core.agent import Agent
from pade.acl.aid import AID
from pade.behaviours.protocols import TimedBehaviour
from pade.misc.data_logger import get_shared_session_id, logger
from sys import argv

class ComportTemporal(TimedBehaviour):
    """Behaviour that executes actions at regular intervals."""
    
    def __init__(self, agent, time):
        # Modern super() syntax.
        super().__init__(agent, time)
        self.execution_count = 0

    def on_time(self):
        """Called at every configured interval."""
        super().on_time()
        self.execution_count += 1
        
        # Keep terminal output aligned with the legacy example.
        display_message(self.agent.aid.localname, 'Hello World!')
        
        # Register the timed behaviour execution
        logger.log_event(
            event_type="timed_behaviour_execution",
            agent_id=self.agent.aid.name,
            data={
                "execution_count": self.execution_count,
                "interval": self.time
            }
        )


class AgenteHelloWorld(Agent):
    """Agent that uses a timed behaviour to display messages."""
    
    def __init__(self, aid, session_id):
        super().__init__(aid=aid, debug=False)
        self.session_id = session_id

        # Create the timed behaviour (every 1 second)
        comp_temp = ComportTemporal(self, 1.0)
        self.behaviours.append(comp_temp)
        
        # Register agent creation
        logger.log_agent(
            agent_id=self.aid.name,
            session_id=self.session_id,
            name=self.aid.name,
            state="Created"
        )
    
    def on_start(self):
        """Called when the agent starts and registers with the AMS."""
        super().on_start()
        display_message(self.aid.name, 'Agent registered with the AMS - Starting timed behaviours...')
        
        # Register the active agent state
        logger.log_agent(
            agent_id=self.aid.name,
            session_id=self.session_id,
            name=self.aid.name,
            state="Active"
        )
        
        # Register the startup event
        logger.log_event(
            event_type="agent_started",
            agent_id=self.aid.name,
            data={"port": self.aid.port}
        )
    
if __name__ == '__main__':
    # Validate that the base port was provided.
    if len(argv) < 2:
        print("Usage: python agent_example_2_updated.py <base_port>")
        print("Example: python agent_example_2_updated.py 20000")
        exit(1)
    
    agents_per_process = 2
    c = 0
    agents = list()
    
    # AMS configuration
    ams_config = {'name': 'localhost', 'port': 8000}
    
    # Shared session for all agents
    session_id = get_shared_session_id()
    
    # Register the example session
    logger.log_session(
        session_id=session_id,
        name=f"TimedHelloWorld_Session_{session_id}",
        state="Started"
    )
    
    for i in range(agents_per_process):
        port = int(argv[1]) + c
        agent_name = f'agent_timed_{port}@localhost:{port}'
        
        # Create the agent
        agente_hello = AgenteHelloWorld(AID(name=agent_name), session_id)
        
        # Configure the agent AMS endpoint
        agente_hello.update_ams(ams_config)
        
        agents.append(agente_hello)
        display_message('System', f'Agent {agent_name} created')
        c += 1000
    
    display_message('System', f'Starting {len(agents)} agents with timed behaviours...')
    
    # Register the startup event
    logger.log_event(
        event_type="test_started",
        data={
            "example": "agent_example_2",
            "num_agents": len(agents),
            "base_port": argv[1],
            "behaviour_interval": 1.0
        }
    )
    
    start_loop(agents)
