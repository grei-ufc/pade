#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
FIPA Request Protocol - PADE 2026 version.

Flow: REQUEST -> AGREE -> INFORM
Scenario: one initiator requests an action; the participant agrees and
confirms completion.
"""

from sys import argv

from pade.misc.utility import display_message, start_loop
from pade.core.agent import Agent
from pade.acl.messages import ACLMessage
from pade.acl.aid import AID
from pade.behaviours.protocols import FipaRequestProtocol
from pade.misc.data_logger import get_shared_session_id, logger


# --- BEHAVIOURS (PROTOCOL LOGIC) ---

class RequestInitiator(FipaRequestProtocol):
    """Initiator logic: send the request and process confirmations."""
    def __init__(self, agent, message):
        super().__init__(agent, message, is_initiator=True)

    def handle_agree(self, message):
        """Executed when the participant accepts the request."""
        display_message(self.agent.aid.name, f"🤝 Received AGREE from {message.sender.name}: {message.content}")

    def handle_inform(self, message):
        """Executed when the participant confirms task completion."""
        display_message(self.agent.aid.name, f"✅ Received INFORM from {message.sender.name}: {message.content}")

class RequestParticipant(FipaRequestProtocol):
    """Participant logic: receive the request and send responses."""
    def __init__(self, agent):
        super().__init__(agent, message=None, is_initiator=False)

    def handle_request(self, message):
        """Process the initial request."""
        super().handle_request(message)
        display_message(self.agent.aid.name, f"📥 Request received from {message.sender.name}: {message.content}")

        # 1. Send AGREE
        response = message.create_reply()
        response.set_performative(ACLMessage.AGREE)
        response.set_content('Request Accepted')
        self.agent.send(response)

        # 2. Send INFORM
        response_2 = message.create_reply()
        response_2.set_performative(ACLMessage.INFORM)
        response_2.set_content('Task Completed Successfully')
        self.agent.send(response_2)


# --- AGENT CLASSES ---

class AgentInitiator(Agent):
    def __init__(self, aid, participant_name):
        super().__init__(aid=aid, debug=False)
        self.participant_name = participant_name

    def on_start(self):
        super().on_start()
        display_message(self.aid.name, "🚀 Initiator agent online.")
        # A short delay helps ensure AMS registration has completed.
        self.call_later(4.0, self.launch_request)

    def launch_request(self):
        display_message(self.aid.name, "📤 Sending REQUEST...")

        message = ACLMessage(ACLMessage.REQUEST)
        message.set_protocol(ACLMessage.FIPA_REQUEST_PROTOCOL)
        message.add_receiver(AID(name=self.participant_name))
        message.set_content('Perform Task Alpha')

        # Start the behaviour and trigger the request message.
        behav = RequestInitiator(self, message)
        self.behaviours.append(behav)
        behav.on_start()

class AgentParticipant(Agent):
    def __init__(self, aid):
        super().__init__(aid=aid, debug=False)

    def on_start(self):
        super().on_start()
        display_message(self.aid.name, "🏪 Participant agent waiting for requests.")
        self.behaviours.append(RequestParticipant(self))


# --- EXECUTION ---

if __name__ == '__main__':
    # Runtime and logging configuration.
    ams_config = {'name': 'localhost', 'port': 8000}
    session_id = get_shared_session_id()
    logger.log_session(session_id=session_id, name="FipaRequest_Test", state="Started")

    base_port = int(argv[1]) if len(argv) > 1 else 24000
    participant_name = f'agent_participant_1@localhost:{base_port}'
    initiator_name = f'agent_initiator@localhost:{base_port + 1}'

    # Instantiate the agents.
    agents = [
        AgentParticipant(AID(name=participant_name)),
        AgentInitiator(AID(name=initiator_name), participant_name),
    ]

    for ag in agents:
        ag.update_ams(ams_config)

    display_message('System', "🎬 Starting FIPA Request protocol test...")
    start_loop(agents)
