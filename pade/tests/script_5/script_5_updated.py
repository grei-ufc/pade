#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PADE Hello World - PADE 2026 version.

Objective:
- Test a minimal pure ACL communication flow using INFORM.
- Validate the native CSV logs generated in messages.csv.
"""

from sys import argv

from pade.misc.utility import display_message, start_loop
from pade.core.agent import Agent
from pade.acl.messages import ACLMessage
from pade.acl.aid import AID
from pade.misc.data_logger import get_shared_session_id, logger


IGNORED_SYSTEM_MESSAGES = {
    'Agent successfully identified.',
    'CONNECTION',
}


class TestAgent(Agent):
    def __init__(self, aid, peer_name=None):
        super().__init__(aid=aid, debug=False)
        self.peer_name = peer_name

    def on_start(self):
        super().on_start()
        display_message(self.aid.name, "🚀 Agent online.")

        # Bob starts the conversation by greeting Alice.
        if self.peer_name is not None:
            # A short delay helps ensure Alice is already registered in the AMS.
            self.call_later(3.0, self.send_hello)

    def send_hello(self):
        display_message(self.aid.name, "📤 Sending greeting to Alice...")
        message = ACLMessage(ACLMessage.INFORM)
        message.add_receiver(AID(name=self.peer_name))
        message.set_content('Hello Alice!')
        self.send(message)

    def react(self, message):
        """Hide transport and AMS messages to keep the terminal focused."""
        super().react(message)

        content = message.content

        if isinstance(content, bytes):
            return

        if content in IGNORED_SYSTEM_MESSAGES:
            return

        if isinstance(content, str) and content.startswith('[Agent Table:'):
            return

        display_message(self.aid.name, f"📥 Message received: {content}")


if __name__ == '__main__':
    ams_config = {'name': 'localhost', 'port': 8000}
    session_id = get_shared_session_id()
    logger.log_session(session_id=session_id, name="HelloWorld_ACL", state="Started")

    base_port = int(argv[1]) if len(argv) > 1 else 24000
    alice_name = f'Alice@localhost:{base_port}'
    bob_name = f'Bob@localhost:{base_port + 1}'

    agents = [
        TestAgent(AID(name=alice_name)),
        TestAgent(AID(name=bob_name), peer_name=alice_name),
    ]

    for agent in agents:
        agent.update_ams(ams_config)

    display_message('System', "🎬 Starting basic communication test...")
    start_loop(agents)
