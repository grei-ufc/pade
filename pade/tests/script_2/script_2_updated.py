#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Unified FIPA ContractNet example for PADE 2026.

This script consolidates the negotiation flow into a single file:
- 1 Consumer agent (Initiator)
- 3 Bookstore agents (Participants: Saraiva, Cultura, Nobel)
- Flow: CFP -> PROPOSE -> ACCEPT/REJECT -> INFORM
"""

import json
from sys import argv

from pade.misc.utility import display_message, start_loop
from pade.core.agent import Agent
from pade.acl.messages import ACLMessage
from pade.acl.aid import AID
from pade.behaviours.protocols import FipaContractNetProtocol
from pade.misc.data_logger import get_shared_session_id, logger


class BookstoreAgentBehaviour(FipaContractNetProtocol):
    """Bookstore-side protocol logic."""

    def __init__(self, agent):
        super().__init__(agent, is_initiator=False)
        self.protocol = ACLMessage.FIPA_CONTRACT_NET_PROTOCOL

    def handle_cfp(self, message):
        super().handle_cfp(message)
        display_message(
            self.agent.aid.name,
            f'📋 CFP received from {message.sender.name}. Checking inventory...'
        )

        try:
            order = json.loads(message.content)

            for book in self.agent.books_list:
                if str(book['title']).strip() == str(order['title']).strip():
                    if book['qty'] >= order['qty']:
                        display_message(
                            self.agent.aid.name,
                            f"💡 Book found! Proposal: R$ {book['how much is']}"
                        )

                        response = message.create_reply()
                        response.set_performative(ACLMessage.PROPOSE)

                        proposal_data = book.copy()
                        proposal_data['store_id'] = self.agent.aid.name
                        response.set_content(json.dumps(proposal_data))
                        self.agent.send(response)
                        return

            display_message(
                self.agent.aid.name,
                f"❌ Book '{order.get('title')}' is not available."
            )

        except Exception as exc:
            display_message(self.agent.aid.name, f"⚠️ Error while processing CFP: {exc}")

    def handle_accept_propose(self, message):
        super().handle_accept_propose(message)
        display_message(self.agent.aid.name, '✅ My proposal won! Sending receipt.')

        reply = message.create_reply()
        reply.set_performative(ACLMessage.INFORM)
        reply.set_content('Purchase Approved')
        self.agent.send(reply)

    def handle_reject_propose(self, message):
        super().handle_reject_propose(message)
        display_message(self.agent.aid.name, '📉 Proposal rejected.')


class ConsumerAgentBehaviour(FipaContractNetProtocol):
    """Consumer-side protocol logic."""

    def handle_propose(self, message):
        super().handle_propose(message)
        display_message(self.agent.aid.name, f'💰 Proposal received from {message.sender.name}')

    def handle_all_proposes(self, proposes):
        """Evaluate all received proposals and choose the best one."""
        super().handle_all_proposes(proposes)

        if not proposes:
            display_message(self.agent.aid.name, '⚠️ No bookstore sent any proposals.')
            return

        display_message(self.agent.aid.name, f'🔍 Analyzing {len(proposes)} proposals...')

        best_propose = None
        lower_price = float('inf')

        try:
            for proposal in proposes:
                data = json.loads(proposal.content)

                price = data['how much is']
                if price < lower_price:
                    lower_price = price
                    best_propose = proposal

            display_message(
                self.agent.aid.name,
                f'🏆 Winner: {best_propose.sender.name} for R$ {lower_price}'
            )

            for proposal in proposes:
                reply = proposal.create_reply()
                if proposal == best_propose:
                    reply.set_performative(ACLMessage.ACCEPT_PROPOSAL)
                    reply.set_content('Proposal Accepted')
                else:
                    reply.set_performative(ACLMessage.REJECT_PROPOSAL)
                    reply.set_content('Price too high')
                self.agent.send(reply)

        except Exception as exc:
            display_message(self.agent.aid.name, f"⚠️ Error while evaluating proposals: {exc}")

    def handle_inform(self, message):
        super().handle_inform(message)
        display_message(self.agent.aid.name, '📦 Purchase completed successfully!')


class BookstoreAgent(Agent):
    def __init__(self, aid, books_list):
        super().__init__(aid=aid, debug=False)
        self.books_list = books_list

    def on_start(self):
        super().on_start()
        display_message(self.aid.name, "🏪 Bookstore is open and waiting for CFPs.")
        self.behaviours.append(BookstoreAgentBehaviour(self))


class ConsumerAgent(Agent):
    def __init__(self, aid, stores, order):
        super().__init__(aid, debug=False)
        self.stores = stores
        self.order = order

    def on_start(self):
        super().on_start()
        display_message(self.aid.name, "🛒 Consumer is ready. Starting search in 4 seconds...")
        self.call_later(4.0, self.launch_cfp)

    def launch_cfp(self):
        display_message(self.aid.name, "📤 Launching Call for Proposal (CFP)...")

        message = ACLMessage(ACLMessage.CFP)
        message.set_protocol(ACLMessage.FIPA_CONTRACT_NET_PROTOCOL)

        for store in self.stores:
            message.add_receiver(AID(name=store))

        message.set_content(json.dumps(self.order))

        behaviour = ConsumerAgentBehaviour(self, message)
        self.behaviours.append(behaviour)
        behaviour.on_start()


if __name__ == '__main__':
    ams_config = {'name': 'localhost', 'port': 8000}
    session_id = get_shared_session_id()
    logger.log_session(session_id=session_id, name="Negotiation_Test", state="Started")

    base_port = int(argv[1]) if len(argv) > 1 else 24000

    saraiva_stock = [
        {
            'title': 'The Lord of the Rings',
            'author': 'J. R. R. Tolkien',
            'qty': 10,
            'how much is': 53.50,
        }
    ]
    cultura_stock = [
        {
            'title': 'The Lord of the Rings',
            'author': 'J. R. R. Tolkien',
            'qty': 10,
            'how much is': 43.50,
        }
    ]
    nobel_stock = [
        {
            'title': 'The Lord of the Rings',
            'author': 'J. R. R. Tolkien',
            'qty': 10,
            'how much is': 63.50,
        }
    ]

    order = {'title': 'The Lord of the Rings', 'author': 'J. R. R. Tolkien', 'qty': 5}

    saraiva_name = f'Saraiva@localhost:{base_port}'
    cultura_name = f'Cultura@localhost:{base_port + 1}'
    nobel_name = f'Nobel@localhost:{base_port + 2}'
    consumer_name = f'Consumer@localhost:{base_port + 3}'

    agents = [
        BookstoreAgent(AID(name=saraiva_name), saraiva_stock),
        BookstoreAgent(AID(name=cultura_name), cultura_stock),
        BookstoreAgent(AID(name=nobel_name), nobel_stock),
        ConsumerAgent(
            AID(name=consumer_name),
            [saraiva_name, cultura_name, nobel_name],
            order,
        ),
    ]

    for agent in agents:
        agent.update_ams(ams_config)

    display_message('System', "🚀 Starting ContractNet negotiation environment...")
    start_loop(agents)
