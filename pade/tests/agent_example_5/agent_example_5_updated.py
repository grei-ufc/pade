#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FIPA-Subscribe protocol example (Publisher-Subscriber) - Python 3.12.11 version
Adapted by Douglas Barros on March 4, 2026

This example demonstrates the FIPA-Subscribe protocol:
- AgentPublisher: publishes random numbers every second
- AgentSubscriber: subscribes and receives the publications
"""

from pade.misc.utility import display_message, start_loop
from pade.core.agent import Agent
from pade.acl.aid import AID
from pade.acl.messages import ACLMessage
from pade.behaviours.protocols import FipaSubscribeProtocol, TimedBehaviour
from pade.misc.data_logger import get_shared_session_id, logger
from sys import argv
import random
from datetime import datetime

class SubscriberProtocol(FipaSubscribeProtocol):
    """
    Subscriber-side protocol.
    Sends SUBSCRIBE and receives publications (INFORM).
    """
    
    def __init__(self, agent, message):
        # Modern super() syntax.
        super().__init__(agent, message, is_initiator=True)
        
        logger.log_event(
            event_type="subscriber_protocol_created",
            agent_id=self.agent.aid.name,
            data={"target": message.receivers[0].name if message.receivers else "unknown"}
        )

    def handle_agree(self, message):
        """Handle subscription confirmation."""
        display_message(self.agent.aid.name, message.content)
        
        logger.log_event(
            event_type="subscribe_agree_received",
            agent_id=self.agent.aid.name,
            data={"from": message.sender.name, "content": message.content}
        )

    def handle_inform(self, message):
        """Handle publisher notifications."""
        display_message(self.agent.aid.name, message.content)
        
        logger.log_event(
            event_type="publication_received",
            agent_id=self.agent.aid.name,
            data={
                "from": message.sender.name,
                "value": message.content,
                "timestamp": datetime.now().isoformat()
            }
        )


class PublisherProtocol(FipaSubscribeProtocol):
    """
    Publisher-side protocol.
    Receives subscriptions and notifies all subscribers.
    """
    
    def __init__(self, agent):
        super().__init__(agent, message=None, is_initiator=False)
        self.publication_count = 0
        
        logger.log_event(
            event_type="publisher_protocol_created",
            agent_id=self.agent.aid.name,
            data={}
        )

    def handle_subscribe(self, message):
        """Handle a subscription request."""
        self.register(message.sender)
        display_message(
            self.agent.aid.name,
            '{} from {}'.format(message.content, message.sender.name)
        )
        
        logger.log_event(
            event_type="subscribe_received",
            agent_id=self.agent.aid.name,
            data={
                "from": message.sender.name,
                "content": message.content,
                "total_subscribers": len(self.subscribers)
            }
        )
        
        # Reply with AGREE.
        resposta = message.create_reply()
        resposta.set_performative(ACLMessage.AGREE)
        resposta.set_content('Subscribe message accepted')
        self.agent.send(resposta)
        
        logger.log_event(
            event_type="subscribe_agree_sent",
            agent_id=self.agent.aid.name,
            data={"to": message.sender.name}
        )

    def handle_cancel(self, message):
        """Handle subscription cancellation."""
        self.deregister(message.sender)
        display_message(self.agent.aid.name, message.content)
        
        logger.log_event(
            event_type="subscribe_cancel_received",
            agent_id=self.agent.aid.name,
            data={"from": message.sender.name}
        )

    def notify(self, message):
        """Publish a message to all subscribers."""
        self.publication_count += 1
        
        logger.log_event(
            event_type="publication_sent",
            agent_id=self.agent.aid.name,
            data={
                "publication_number": self.publication_count,
                "subscribers_count": len(self.subscribers),
                "value": message.content
            }
        )
        
        super().notify(message)


class Time(TimedBehaviour):
    """
    Timed behaviour that generates random numbers every second.
    """
    
    def __init__(self, agent, notify_callback):
        super().__init__(agent, 1)
        self.notify_callback = notify_callback
        self.generation_count = 0

    def on_time(self):
        super().on_time()
        self.generation_count += 1
        
        # Generate a random number.
        random_value = random.random()
        
        # Build the publication message.
        message = ACLMessage(ACLMessage.INFORM)
        message.set_protocol(ACLMessage.FIPA_SUBSCRIBE_PROTOCOL)
        message.set_content(str(random_value))
        
        # Notify all subscribers.
        self.notify_callback(message)
        
        logger.log_event(
            event_type="value_generated",
            agent_id=self.agent.aid.name,
            data={
                "generation_count": self.generation_count,
                "value": random_value
            }
        )


class AgentSubscriber(Agent):
    """Subscriber agent that receives publications."""
    
    def __init__(self, aid, publisher_aid):
        super().__init__(aid=aid, debug=False)
        self.publisher_aid = publisher_aid
        self.session_id = get_shared_session_id()
        
        # Log agent creation.
        logger.log_agent(
            agent_id=self.aid.name,
            session_id=self.session_id,
            name=self.aid.name,
            state="Created"
        )
        
        logger.log_event(
            event_type="subscriber_created",
            agent_id=self.aid.name,
            data={"publisher": publisher_aid.name}
        )
        
        # Schedule the subscription start.
        self.call_later(8.0, self.launch_subscriber_protocol)

    def on_start(self):
        """Register on AMS startup."""
        super().on_start()
        
        logger.log_agent(
            agent_id=self.aid.name,
            session_id=self.session_id,
            name=self.aid.name,
            state="Active"
        )

    def launch_subscriber_protocol(self):
        """Start the subscription protocol."""
        # Build the SUBSCRIBE message.
        msg = ACLMessage(ACLMessage.SUBSCRIBE)
        msg.set_protocol(ACLMessage.FIPA_SUBSCRIBE_PROTOCOL)
        msg.set_content('Subscription request')
        msg.add_receiver(self.publisher_aid)
        
        # Start the protocol behaviour.
        self.protocol = SubscriberProtocol(self, msg)
        self.behaviours.append(self.protocol)
        self.protocol.on_start()
        
        logger.log_event(
            event_type="subscribe_request_sent",
            agent_id=self.aid.name,
            data={"to": self.publisher_aid.name}
        )


class AgentPublisher(Agent):
    """Publisher agent that generates and publishes random numbers."""
    
    def __init__(self, aid):
        super().__init__(aid=aid, debug=False)
        self.session_id = get_shared_session_id()
        
        # Log agent creation.
        logger.log_agent(
            agent_id=self.aid.name,
            session_id=self.session_id,
            name=self.aid.name,
            state="Created"
        )
        
        # Publisher protocol.
        self.protocol = PublisherProtocol(self)
        
        # Timed behaviour that generates values.
        self.timed = Time(self, self.protocol.notify)
        
        self.behaviours.append(self.protocol)
        self.behaviours.append(self.timed)
        
        logger.log_event(
            event_type="publisher_created",
            agent_id=self.aid.name,
            data={}
        )

    def on_start(self):
        """Register on AMS startup."""
        super().on_start()
        
        logger.log_agent(
            agent_id=self.aid.name,
            session_id=self.session_id,
            name=self.aid.name,
            state="Active"
        )


if __name__ == '__main__':
    if len(argv) < 2:
        print("Usage: python agent_example_5_updated.py <base_port>")
        print("Example: python agent_example_5_updated.py 20000")
        exit(1)

    agents = list()
    
    # AMS configuration.
    ams_config = {'name': 'localhost', 'port': 8000}
    
    # Single session shared with the integrated runtime.
    session_id = get_shared_session_id()
    
    logger.log_session(
        session_id=session_id,
        name=f"Subscribe_Session_{session_id}",
        state="Started"
    )
    
    # Base port.
    base_port = int(argv[1])
    k = 10000  # Offset used for subscriber ports.
    
    # Create the publisher on the base port.
    publisher_name = f'publisher_{base_port}@localhost:{base_port}'
    publisher_aid = AID(name=publisher_name)
    publisher = AgentPublisher(publisher_aid)
    publisher.update_ams(ams_config)
    agents.append(publisher)
    
    # Create subscriber 1 on base port + k.
    sub1_name = f'subscriber_1_{base_port + k}@localhost:{base_port + k}'
    subscriber1 = AgentSubscriber(AID(name=sub1_name), publisher_aid)
    subscriber1.update_ams(ams_config)
    agents.append(subscriber1)
    
    # Create subscriber 2 on base port - k.
    sub2_name = f'subscriber_2_{base_port - k}@localhost:{base_port - k}'
    subscriber2 = AgentSubscriber(AID(name=sub2_name), publisher_aid)
    subscriber2.update_ams(ams_config)
    agents.append(subscriber2)
    
    logger.log_event(
        event_type="test_started",
        data={
            "example": "agent_example_5",
            "num_agents": len(agents),
            "base_port": base_port,
            "publisher": publisher_name,
            "subscribers": [sub1_name, sub2_name]
        }
    )
    
    start_loop(agents)
