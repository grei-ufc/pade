#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FIPA-Subscribe protocol example with threads - Python 3.12.11 version
Adapted by Douglas Barros on March 4, 2026

This example extends the FIPA-Subscribe scenario with `call_in_thread`
to demonstrate how a blocking function can run without freezing the
Twisted reactor.
"""

from pade.misc.utility import display_message, start_loop, call_in_thread
from pade.core.agent import Agent
from pade.acl.aid import AID
from pade.acl.messages import ACLMessage
from pade.behaviours.protocols import FipaSubscribeProtocol, TimedBehaviour
from pade.misc.data_logger import get_shared_session_id, logger
from sys import argv
import random
import time
from datetime import datetime


def my_time(a, b):
    """Run a blocking function in a worker thread."""
    print('------> I will sleep now!', a)
    time.sleep(10)
    print('------> I wake up now!', b)

    logger.log_event(
        event_type="thread_execution",
        agent_id="system",
        data={"function": "my_time", "params": [a, b], "duration": 10},
    )


class SubscriberProtocol(FipaSubscribeProtocol):
    """Subscriber-side protocol."""

    def __init__(self, agent, message):
        super().__init__(agent, message, is_initiator=True)

        logger.log_event(
            event_type="subscriber_protocol_created",
            agent_id=self.agent.aid.name,
            data={"target": message.receivers[0].name if message.receivers else "unknown"},
        )

    def handle_agree(self, message):
        """Handle the publisher AGREE reply."""
        display_message(self.agent.aid.name, message.content)

        logger.log_event(
            event_type="subscribe_agree_received",
            agent_id=self.agent.aid.name,
            data={"from": message.sender.name, "content": message.content},
        )

    def handle_inform(self, message):
        """Handle a publication from the publisher."""
        display_message(self.agent.aid.name, message.content)

        logger.log_event(
            event_type="publication_received",
            agent_id=self.agent.aid.name,
            data={
                "from": message.sender.name,
                "value": message.content,
                "timestamp": datetime.now().isoformat(),
            },
        )


class PublisherProtocol(FipaSubscribeProtocol):
    """Publisher-side protocol."""

    def __init__(self, agent):
        super().__init__(agent, message=None, is_initiator=False)
        self.publication_count = 0

        logger.log_event(
            event_type="publisher_protocol_created",
            agent_id=self.agent.aid.name,
            data={},
        )

    def handle_subscribe(self, message):
        """Handle an incoming SUBSCRIBE request."""
        self.register(message.sender)
        display_message(self.agent.aid.name, message.content)

        logger.log_event(
            event_type="subscribe_received",
            agent_id=self.agent.aid.name,
            data={
                "from": message.sender.name,
                "content": message.content,
                "total_subscribers": len(self.subscribers),
            },
        )

        reply = message.create_reply()
        reply.set_performative(ACLMessage.AGREE)
        reply.set_content('Subscribe message accepted')
        self.agent.send(reply)

        logger.log_event(
            event_type="subscribe_agree_sent",
            agent_id=self.agent.aid.name,
            data={"to": message.sender.name},
        )

    def handle_cancel(self, message):
        """Handle an incoming CANCEL request."""
        self.deregister(message.sender)
        display_message(self.agent.aid.name, message.content)

        logger.log_event(
            event_type="subscribe_cancel_received",
            agent_id=self.agent.aid.name,
            data={"from": message.sender.name},
        )

    def notify(self, message):
        """Notify all registered subscribers."""
        self.publication_count += 1

        logger.log_event(
            event_type="publication_sent",
            agent_id=self.agent.aid.name,
            data={
                "publication_number": self.publication_count,
                "subscribers_count": len(self.subscribers),
                "value": message.content,
            },
        )

        super().notify(message)


class Time(TimedBehaviour):
    """Generate one random value per second."""

    def __init__(self, agent, notify_callback):
        super().__init__(agent, 1)
        self.notify_callback = notify_callback
        self.generation_count = 0

    def on_time(self):
        super().on_time()
        self.generation_count += 1

        random_value = random.random()

        message = ACLMessage(ACLMessage.INFORM)
        message.set_protocol(ACLMessage.FIPA_SUBSCRIBE_PROTOCOL)
        message.set_content(str(random_value))

        self.notify_callback(message)

        logger.log_event(
            event_type="value_generated",
            agent_id=self.agent.aid.name,
            data={
                "generation_count": self.generation_count,
                "value": random_value,
            },
        )


class AgentSubscriber(Agent):
    """Subscriber agent that receives publisher notifications."""

    def __init__(self, aid, publisher_aid):
        super().__init__(aid=aid, debug=False)
        self.publisher_aid = publisher_aid
        self.session_id = get_shared_session_id()

        logger.log_agent(
            agent_id=self.aid.name,
            session_id=self.session_id,
            name=self.aid.name,
            state="Created",
        )

        logger.log_event(
            event_type="subscriber_created",
            agent_id=self.aid.name,
            data={"publisher": publisher_aid.name},
        )

        self.call_later(8.0, self.launch_subscriber_protocol)

    def on_start(self):
        """Register the agent as active once startup completes."""
        super().on_start()

        logger.log_agent(
            agent_id=self.aid.name,
            session_id=self.session_id,
            name=self.aid.name,
            state="Active",
        )

    def launch_subscriber_protocol(self):
        """Build a fresh SUBSCRIBE message and start the protocol."""
        message = ACLMessage(ACLMessage.SUBSCRIBE)
        message.set_protocol(ACLMessage.FIPA_SUBSCRIBE_PROTOCOL)
        message.set_content('Subscription request')
        message.add_receiver(self.publisher_aid)

        self.protocol = SubscriberProtocol(self, message)
        self.behaviours.append(self.protocol)
        self.protocol.on_start()

        logger.log_event(
            event_type="subscribe_request_sent",
            agent_id=self.aid.name,
            data={"to": self.publisher_aid.name},
        )


class AgentPublisher(Agent):
    """Publisher agent that periodically publishes random values."""

    def __init__(self, aid):
        super().__init__(aid=aid, debug=False)
        self.session_id = get_shared_session_id()

        logger.log_agent(
            agent_id=self.aid.name,
            session_id=self.session_id,
            name=self.aid.name,
            state="Created",
        )

        self.protocol = PublisherProtocol(self)
        self.timed = Time(self, self.protocol.notify)

        self.behaviours.append(self.protocol)
        self.behaviours.append(self.timed)

        logger.log_event(
            event_type="publisher_created",
            agent_id=self.aid.name,
            data={},
        )

        call_in_thread(my_time, 'a', 'b')

    def on_start(self):
        """Register the agent as active once startup completes."""
        super().on_start()

        logger.log_agent(
            agent_id=self.aid.name,
            session_id=self.session_id,
            name=self.aid.name,
            state="Active",
        )


if __name__ == '__main__':
    if len(argv) < 2:
        print("Usage: python agent_example_6_updated.py <base_port>")
        print("Example: python agent_example_6_updated.py 20000")
        exit(1)

    agents = list()

    # AMS configuration used by all agents in this example.
    ams_config = {'name': 'localhost', 'port': 8000}

    # Single session shared with the integrated runtime.
    session_id = get_shared_session_id()

    logger.log_session(
        session_id=session_id,
        name=f"SubscribeThread_Session_{session_id}",
        state="Started",
    )

    base_port = int(argv[1])
    offset = 10000

    for i in range(2):
        port = base_port + (i * 1000)

        publisher_name = f'publisher_{port}@localhost:{port}'
        publisher_aid = AID(name=publisher_name)
        publisher = AgentPublisher(publisher_aid)
        publisher.update_ams(ams_config)
        agents.append(publisher)

        sub1_name = f'subscriber_1_{port + offset}@localhost:{port + offset}'
        subscriber1 = AgentSubscriber(AID(name=sub1_name), publisher_aid)
        subscriber1.update_ams(ams_config)
        agents.append(subscriber1)

        sub2_name = f'subscriber_2_{port - offset}@localhost:{port - offset}'
        subscriber2 = AgentSubscriber(AID(name=sub2_name), publisher_aid)
        subscriber2.update_ams(ams_config)
        agents.append(subscriber2)

    logger.log_event(
        event_type="test_started",
        data={
            "example": "agent_example_6",
            "num_agents": len(agents),
            "base_port": base_port,
            "num_publishers": 2,
            "subscribers_per_publisher": 2,
        },
    )

    start_loop(agents)
