# Hello world in PADE - Python 3.12.11 version
#
# Created by Lucas S Melo on July 21, 2015 - Fortaleza, Ceará - Brazil
#
# Adapted by Douglas Barros on March 4, 2026 - Fortaleza, Ceará - Brazil

from pade.misc.utility import display_message, start_loop, format_message_content
from pade.core.agent import Agent
from pade.acl.aid import AID
from pade.acl.messages import ACLMessage
from pade.misc.data_logger import get_shared_session_id, logger
from sys import argv

class AgenteHelloWorld(Agent):
    def __init__(self, aid, peer_aid, session_id):
        super().__init__(aid=aid, debug=False)  # Use debug=True to inspect formatted react() messages.
        self.peer_aid = peer_aid
        self.session_id = session_id
        
        # OPTION 1: Terminal-only output (not intercepted by Sniffer/messages.csv)
        display_message(self.aid.localname, 'Hello World! (Terminal Only)')
        
        # Register agent creation in agents.csv
        logger.log_agent(
            agent_id=self.aid.name,
            session_id=self.session_id,
            name=self.aid.name,
            state="Created"
        )
    
    def on_start(self):
        """Called when the agent starts and registers with the AMS."""
        super().on_start()
        display_message(self.aid.name, 'Agent ready and registered with the AMS!')
        
        # Register the active agent state
        logger.log_agent(
            agent_id=self.aid.name,
            session_id=self.session_id,
            name=self.aid.name,
            state="Active"
        )
        
        # Register the startup event in events.csv
        logger.log_event(
            event_type="agent_started",
            agent_id=self.aid.name,
            data={"port": self.aid.port}
        )

        # Send to a neighboring agent instead of self-sending. This guarantees
        # real network traffic and keeps messages.csv under the Sniffer's control.
        self.call_later(3.0, self.send_network_hello)

    def send_network_hello(self):
        """Send a FIPA-ACL message to a neighboring agent."""
        message = ACLMessage(ACLMessage.INFORM)
        message.add_receiver(self.peer_aid)
        message.set_ontology('hello_ontology')
        message.set_content('Hello World Message! (Network)')
        self.send(message)
    
    def react(self, message):
        """Process incoming messages to keep compatibility with the legacy example."""
        super().react(message)
        
        # Safely format the message content for display.
        formatted_content = format_message_content(message.content)
        
        # If debug=True, show the received FIPA payload.
        if self.debug and message.content:
            display_message(self.aid.name, f'Received message: {formatted_content}')


if __name__ == '__main__':
    # Validate that the base port was provided.
    if len(argv) < 2:
        print("Usage: python agent_example_1_updated.py <base_port>")
        print("Example: python agent_example_1_updated.py 20000")
        exit(1)
    
    agents_per_process = 3
    c = 0
    agents = list()
    
    # AMS configuration
    ams_config = {'name': 'localhost', 'port': 8000}
    
    # Shared session for all agents
    session_id = get_shared_session_id()
    
    # Register the example session in sessions.csv
    logger.log_session(
        session_id=session_id,
        name=f"HelloWorld_Session_{session_id}",
        state="Started"
    )
    
    aids = []
    for i in range(agents_per_process):
        port = int(argv[1]) + c
        agent_name = f'agent_hello_{port}@localhost:{port}'  # f-string (Python 3.6+)
        aids.append(AID(name=agent_name))
        c += 1000

    for index, aid in enumerate(aids):
        peer_aid = aids[(index + 1) % len(aids)]

        # Create the agent
        agente_hello = AgenteHelloWorld(aid, peer_aid, session_id)

        # Configure the agent AMS endpoint
        agente_hello.update_ams(ams_config)

        agents.append(agente_hello)
        display_message('System', f'Agent {aid.name} created')
    
    display_message('System', f'Starting {len(agents)} agents...')
    
    # Register the example startup event in events.csv
    logger.log_event(
        event_type="test_started",
        data={
            "example": "agent_example_1",
            "num_agents": len(agents),
            "base_port": argv[1]
        }
    )
    
    start_loop(agents)
