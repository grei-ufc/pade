#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Timed Hello World in PADE with peer messaging.

This variant preserves the legacy timed behaviour example while adding
periodic ACL message exchange so that messages.csv receives application data.
"""

from sys import argv

from pade.acl.aid import AID
from pade.acl.messages import ACLMessage
from pade.behaviours.protocols import TimedBehaviour
from pade.core.agent import Agent
from pade.misc.data_logger import get_shared_session_id, logger
from pade.misc.utility import display_message, format_message_content, start_loop


class TimedHelloWithMessages(TimedBehaviour):
    """Execute a periodic action and occasionally send a message to a peer."""

    def __init__(self, agent, interval):
        super().__init__(agent, interval)
        self.execution_count = 0

    def on_time(self):
        super().on_time()
        self.execution_count += 1

        display_message(self.agent.aid.localname, "Hello World!")
        logger.log_event(
            event_type="timed_behaviour_execution",
            agent_id=self.agent.aid.name,
            data={
                "execution_count": self.execution_count,
                "interval": self.time,
            },
        )

        # Send a peer message every 3 executions to populate messages.csv
        # without overwhelming the terminal output.
        if self.execution_count % 3 == 0:
            message = ACLMessage(ACLMessage.INFORM)
            message.add_receiver(self.agent.peer_aid)
            message.set_ontology("timed_hello_ontology")
            message.set_content(
                f"Timed hello #{self.execution_count} from {self.agent.aid.localname}"
            )
            self.agent.send(message)


class TimedHelloAgent(Agent):
    """Timed agent that also exchanges peer messages."""

    def __init__(self, aid, peer_aid, session_id):
        super().__init__(aid=aid, debug=False)
        self.peer_aid = peer_aid
        self.session_id = session_id

        self.behaviours.append(TimedHelloWithMessages(self, 1.0))

        logger.log_agent(
            agent_id=self.aid.name,
            session_id=self.session_id,
            name=self.aid.name,
            state="Created",
        )

    def on_start(self):
        super().on_start()
        display_message(self.aid.name, "Agente registrado no AMS - Iniciando comportamentos temporizados...")

        logger.log_agent(
            agent_id=self.aid.name,
            session_id=self.session_id,
            name=self.aid.name,
            state="Active",
        )
        logger.log_event(
            event_type="agent_started",
            agent_id=self.aid.name,
            data={"port": self.aid.port, "peer": self.peer_aid.name},
        )

    def react(self, message):
        super().react(message)

        if "ams@" in getattr(message.sender, "name", ""):
            return

        display_message(
            self.aid.localname,
            f"Mensagem recebida de {message.sender.localname}: {format_message_content(message.content)}",
        )


if __name__ == "__main__":
    if len(argv) < 2:
        print("Uso: python agent_example_2_with_messages.py <porta_base>")
        print("Exemplo: python agent_example_2_with_messages.py 20000")
        exit(1)

    base_port = int(argv[1])
    session_id = get_shared_session_id()
    ams_config = {"name": "localhost", "port": 8000}

    logger.log_session(
        session_id=session_id,
        name=f"TimedHelloWithMessages_Session_{session_id}",
        state="Started",
    )

    first_port = base_port
    second_port = base_port + 1000

    first_aid = AID(name=f"agent_timed_{first_port}@localhost:{first_port}")
    second_aid = AID(name=f"agent_timed_{second_port}@localhost:{second_port}")

    first_agent = TimedHelloAgent(first_aid, second_aid, session_id)
    second_agent = TimedHelloAgent(second_aid, first_aid, session_id)

    first_agent.update_ams(ams_config)
    second_agent.update_ams(ams_config)

    agents = [first_agent, second_agent]

    display_message("Sistema", f"Agente {first_aid.name} criado")
    display_message("Sistema", f"Agente {second_aid.name} criado")
    display_message(
        "Sistema",
        "Iniciando 2 agentes com comportamentos temporizados e troca de mensagens...",
    )

    logger.log_event(
        event_type="test_started",
        data={
            "example": "agent_example_2_with_messages",
            "num_agents": len(agents),
            "base_port": argv[1],
            "behaviour_interval": 1.0,
            "message_interval": 3,
        },
    )

    start_loop(agents)
