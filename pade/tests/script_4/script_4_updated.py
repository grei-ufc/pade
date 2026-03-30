#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
FIPA ContractNet Protocol - Energy recomposition scenario.

Flow:
- The initiator requests generation support from participants.
- Each participant proposes its available power.
- The initiator selects the highest available power value.
"""

import json
from sys import argv

from pade.misc.utility import display_message, start_loop
from pade.core.agent import Agent
from pade.acl.messages import ACLMessage
from pade.acl.aid import AID
from pade.behaviours.protocols import FipaContractNetProtocol
from pade.misc.data_logger import get_shared_session_id, logger


def _load_json_payload(raw_content):
    """Decode JSON content from either str or bytes."""
    if isinstance(raw_content, bytes):
        raw_content = raw_content.decode('utf-8')
    return json.loads(raw_content)


# --- BEHAVIOURS (PROTOCOL LOGIC) ---

class InitiatorProtocol(FipaContractNetProtocol):
    """Initiator logic: request power and choose the highest offer."""

    def __init__(self, agent, message):
        super().__init__(agent, message, is_initiator=True)

    def handle_propose(self, message):
        super().handle_propose(message)
        display_message(self.agent.aid.name, f"💰 Power proposal received from {message.sender.name}")

    def handle_refuse(self, message):
        super().handle_refuse(message)
        display_message(self.agent.aid.name, f"❌ {message.sender.name} refused the CFP (REFUSE)")

    def handle_all_proposes(self, proposes):
        """Evaluate all proposals and select the highest available power."""
        super().handle_all_proposes(proposes)

        if not proposes:
            display_message(self.agent.aid.name, '⚠️ No recomposition proposals were received.')
            return

        display_message(self.agent.aid.name, f'🔍 Analyzing {len(proposes)} power proposals...')

        try:
            best_proposal = _load_json_payload(proposes[0].content)
            best_participant = proposes[0]

            for propose in proposes:
                power_value = _load_json_payload(propose.content)
                if power_value['value'] > best_proposal['value']:
                    best_proposal = power_value
                    best_participant = propose

            display_message(
                self.agent.aid.name,
                f"🏆 Best offer: {best_participant.sender.name} with {best_proposal['value']} kW"
            )

            for propose in proposes:
                response = propose.create_reply()
                if propose == best_participant:
                    response.set_performative(ACLMessage.ACCEPT_PROPOSAL)
                    response.set_content('Proposal ACCEPTED - Starting recomposition')
                else:
                    response.set_performative(ACLMessage.REJECT_PROPOSAL)
                    response.set_content('Proposal REJECTED - Value too low')
                self.agent.send(response)

        except Exception as exc:
            display_message(self.agent.aid.name, f"⚠️ Error while evaluating recomposition proposals: {exc}")

    def handle_inform(self, message):
        super().handle_inform(message)
        display_message(self.agent.aid.name, f"📦 Final confirmation from {message.sender.name}: {message.content}")


class ParticipantProtocol(FipaContractNetProtocol):
    """Participant logic: propose its available power."""

    def __init__(self, agent, power_values):
        super().__init__(agent, is_initiator=False)
        self.power_values = power_values

    def handle_cfp(self, message):
        super().handle_cfp(message)
        display_message(self.agent.aid.name, "📋 Received Call For Proposal (CFP) for recomposition.")

        response = message.create_reply()
        response.set_performative(ACLMessage.PROPOSE)
        response.set_content(json.dumps(self.power_values))
        self.agent.send(response)

    def handle_accept_propose(self, message):
        super().handle_accept_propose(message)
        display_message(self.agent.aid.name, "✅ Proposal ACCEPTED. Starting switching operation...")

        response = message.create_reply()
        response.set_performative(ACLMessage.INFORM)
        response.set_content('RECOMPOSITION APPROVED AND ACTIVE')
        self.agent.send(response)

    def handle_reject_proposes(self, message):
        super().handle_reject_proposes(message)
        display_message(self.agent.aid.name, "📉 Proposal rejected by the central system.")


# --- AGENT CLASSES ---

class InitiatorAgent(Agent):
    def __init__(self, aid, participants):
        super().__init__(aid=aid, debug=False)
        self.participants = participants

    def on_start(self):
        super().on_start()
        display_message(self.aid.name, "🚀 Recomposition management agent online.")
        self.call_later(4.0, self.launch_cfp)

    def launch_cfp(self):
        display_message(self.aid.name, "📤 Launching CFP to all participants...")

        order = {'type': 'recomposition_order', 'qty': 100.0}
        message = ACLMessage(ACLMessage.CFP)
        message.set_protocol(ACLMessage.FIPA_CONTRACT_NET_PROTOCOL)

        for participant in self.participants:
            message.add_receiver(AID(name=participant))

        message.set_content(json.dumps(order))

        behaviour = InitiatorProtocol(self, message)
        self.behaviours.append(behaviour)
        behaviour.on_start()


class ParticipantAgent(Agent):
    def __init__(self, aid, power_values):
        super().__init__(aid=aid, debug=False)
        self.power_values = power_values

    def on_start(self):
        super().on_start()
        display_message(self.aid.name, f"🏭 Power unit available: {self.power_values['value']} kW")
        self.behaviours.append(ParticipantProtocol(self, self.power_values))


# --- EXECUTION ---

if __name__ == '__main__':
    ams_config = {'name': 'localhost', 'port': 8000}
    session_id = get_shared_session_id()
    logger.log_session(session_id=session_id, name="Recomposition_Test", state="Started")

    base_port = int(argv[1]) if len(argv) > 1 else 24000

    participant_1_name = f'participant_agent_1@localhost:{base_port}'
    participant_2_name = f'participant_agent_2@localhost:{base_port + 1}'
    initiator_name = f'initiator_agent@localhost:{base_port + 2}'

    agents = [
        ParticipantAgent(AID(name=participant_1_name), {'value': 100.0}),
        ParticipantAgent(AID(name=participant_2_name), {'value': 200.0}),
        InitiatorAgent(AID(name=initiator_name), [participant_1_name, participant_2_name]),
    ]

    for agent in agents:
        agent.update_ams(ams_config)

    display_message('System', "🎬 Starting energy recomposition simulation...")
    start_loop(agents)
