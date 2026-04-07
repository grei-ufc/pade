#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FIPA-ContractNet protocol example - Python 3.12.11 version with CSV logging
Adapted by Douglas Barros on March 4, 2026

This example demonstrates the FIPA-ContractNet protocol (auction):
- AgentInitiator: sends a CFP and chooses the best proposal
- AgentParticipant: replies with proposals (available power)
- The winner is the one with the highest power
"""

from pade.misc.utility import display_message, start_loop
from pade.core.agent import Agent
from pade.acl.aid import AID
from pade.acl.messages import ACLMessage
from pade.behaviours.protocols import FipaContractNetProtocol
from pade.misc.data_logger import get_shared_session_id, logger
from sys import argv
from random import uniform

class CompContNet1(FipaContractNetProtocol):
    """
    Initiator-side behaviour in the ContractNet protocol.
    Sends the CFP, collects proposals, selects the best one, and replies.
    """
    
    def __init__(self, agent, message):
        # Sintaxe moderna de super()
        super().__init__(agent=agent, message=message, is_initiator=True)
        self.cfp = message
        self.proposals_received = []
        
        # Log the protocol start.
        logger.log_event(
            event_type="contractnet_started",
            agent_id=self.agent.aid.name,
            data={
                "num_participants": len(message.receivers),
                "required_power": message.content
            }
        )

    def handle_all_proposes(self, proposes):
        """
        Analyze all received proposals and select the best one
        (highest available power).
        """
        super().handle_all_proposes(proposes)

        best_proposer = None
        higher_power = 0.0
        other_proposers = list()
        
        display_message(self.agent.aid.name, 'Analyzing proposals...')
        
        # Log how many proposals were received.
        logger.log_event(
            event_type="proposals_analysis",
            agent_id=self.agent.aid.name,
            data={"num_proposals": len(proposes)}
        )

        i = 1
        for message in proposes:
            try:
                power = float(message.content)
                display_message(self.agent.aid.name,
                                'Analyzing proposal {i}'.format(i=i))
                display_message(self.agent.aid.name,
                                'Power Offered: {pot}'.format(pot=power))
                
                # Log each individual proposal.
                logger.log_event(
                    event_type="proposal_analyzed",
                    agent_id=self.agent.aid.name,
                    data={
                        "proposal_number": i,
                        "sender": message.sender.name,
                        "power": power
                    }
                )
                
                if power > higher_power:
                    if best_proposer is not None:
                        other_proposers.append(best_proposer)
                    higher_power = power
                    best_proposer = message.sender
                else:
                    other_proposers.append(message.sender)
                i += 1
            except ValueError:
                display_message(self.agent.aid.name, 'Invalid proposal received')

        display_message(self.agent.aid.name,
                        'The best proposal was: {pot} VA'.format(
                            pot=higher_power))
        
        logger.log_event(
            event_type="best_proposal_selected",
            agent_id=self.agent.aid.name,
            data={
                "best_proposer": best_proposer.name if best_proposer else None,
                "best_power": higher_power
            }
        )

        # Send REJECT_PROPOSAL to the losing participants.
        if other_proposers:
            display_message(self.agent.aid.name,
                            'Sending REJECT_PROPOSAL answers...')
            answer = ACLMessage(ACLMessage.REJECT_PROPOSAL)
            answer.set_protocol(ACLMessage.FIPA_CONTRACT_NET_PROTOCOL)
            answer.set_content('Proposal rejected')
            for agent in other_proposers:
                answer.add_receiver(agent)
            self.agent.send(answer)
            
            logger.log_event(
                event_type="reject_proposals_sent",
                agent_id=self.agent.aid.name,
                data={"rejected_count": len(other_proposers)}
            )

        # Send ACCEPT_PROPOSAL to the winner.
        if best_proposer is not None:
            display_message(self.agent.aid.name,
                            'Sending ACCEPT_PROPOSAL answer...')
            answer = ACLMessage(ACLMessage.ACCEPT_PROPOSAL)
            answer.set_protocol(ACLMessage.FIPA_CONTRACT_NET_PROTOCOL)
            answer.set_content('OK')
            answer.add_receiver(best_proposer)
            self.agent.send(answer)
            
            logger.log_event(
                event_type="accept_proposal_sent",
                agent_id=self.agent.aid.name,
                data={"winner": best_proposer.name, "power": higher_power}
            )

    def handle_inform(self, message):
        """Handle the winner confirmation."""
        super().handle_inform(message)
        display_message(self.agent.aid.name, 'INFORM message received')
        
        logger.log_event(
            event_type="inform_received",
            agent_id=self.agent.aid.name,
            data={
                "from": message.sender.name,
                "content": message.content
            }
        )

    def handle_refuse(self, message):
        """Handle a participant refusal."""
        super().handle_refuse(message)
        display_message(self.agent.aid.name, 'REFUSE message received')
        
        logger.log_event(
            event_type="refuse_received",
            agent_id=self.agent.aid.name,
            data={"from": message.sender.name}
        )

    def handle_propose(self, message):
        """Handle a participant proposal."""
        super().handle_propose(message)
        display_message(self.agent.aid.name, 'PROPOSE message received')
        
        logger.log_event(
            event_type="proposal_received",
            agent_id=self.agent.aid.name,
            data={
                "from": message.sender.name,
                "power": message.content
            }
        )


class CompContNet2(FipaContractNetProtocol):
    """
    Participant-side behaviour in the ContractNet protocol.
    Receives the CFP, sends a proposal, and waits for the result.
    """
    
    def __init__(self, agent):
        super().__init__(agent=agent, message=None, is_initiator=False)

    def handle_cfp(self, message):
        """Handle the call for proposal and prepare a reply."""
        self.agent.call_later(1.0, self._handle_cfp, message)

    def _handle_cfp(self, message):
        super().handle_cfp(message)
        self.message = message

        display_message(self.agent.aid.name, 'CFP message received')
        
        logger.log_event(
            event_type="cfp_received",
            agent_id=self.agent.aid.name,
            data={
                "from": message.sender.name,
                "required_power": message.content,
                "available_power": self.agent.pot_disp
            }
        )

        # Send the proposal.
        answer = self.message.create_reply()
        answer.set_performative(ACLMessage.PROPOSE)
        answer.set_content(str(self.agent.pot_disp))
        self.agent.send(answer)
        
        logger.log_event(
            event_type="proposal_sent",
            agent_id=self.agent.aid.name,
            data={
                "to": message.sender.name,
                "power": self.agent.pot_disp
            }
        )

    def handle_reject_propose(self, message):
        """Handle rejection (not the winner)."""
        super().handle_reject_propose(message)
        display_message(self.agent.aid.name,
                        'REJECT_PROPOSAL message received')
        
        logger.log_event(
            event_type="reject_received",
            agent_id=self.agent.aid.name,
            data={"from": message.sender.name}
        )

    def handle_accept_propose(self, message):
        """Handle acceptance (the winner was selected)."""
        super().handle_accept_propose(message)
        display_message(self.agent.aid.name,
                        'ACCEPT_PROPOSE message received')

        logger.log_event(
            event_type="accept_received",
            agent_id=self.agent.aid.name,
            data={"from": message.sender.name}
        )

        # Confirm the result with an INFORM reply.
        answer = message.create_reply()
        answer.set_performative(ACLMessage.INFORM)
        answer.set_content('OK')
        self.agent.send(answer)

        logger.log_event(
            event_type="inform_sent",
            agent_id=self.agent.aid.name,
            data={"to": message.sender.name}
        )


class AgentInitiator(Agent):
    """Initiator agent for the ContractNet protocol."""
    
    def __init__(self, aid, participants):
        super().__init__(aid=aid, debug=False)
        self.participants = participants
        
        # Log agent creation.
        logger.log_agent(
            agent_id=self.aid.name,
            session_id=get_shared_session_id(),
            name=self.aid.name,
            state="Created"
        )

        # Create the CFP message.
        self.message = ACLMessage(ACLMessage.CFP)
        self.message.set_protocol(ACLMessage.FIPA_CONTRACT_NET_PROTOCOL)
        self.message.set_content('60.0')  # Required power.

        for participant in participants:
            self.message.add_receiver(AID(name=participant))

        # Schedule protocol start.
        self.call_later(8.0, self.launch_contract_net_protocol)
        
        logger.log_event(
            event_type="initiator_created",
            agent_id=self.aid.name,
            data={
                "participants": participants,
                "required_power": 60.0
            }
        )

    def on_start(self):
        """Register the agent in the AMS."""
        super().on_start()
        
        logger.log_agent(
            agent_id=self.aid.name,
            session_id=get_shared_session_id(),
            name=self.aid.name,
            state="Active"
        )

    def launch_contract_net_protocol(self):
        """Start the ContractNet protocol."""
        comp = CompContNet1(self, self.message)
        self.behaviours.append(comp)
        comp.on_start()


class AgentParticipant(Agent):
    """Participant agent for the ContractNet protocol."""
    
    def __init__(self, aid, pot_disp):
        super().__init__(aid=aid, debug=False)
        self.pot_disp = pot_disp  # Available power (between 100 and 500 VA).

        comp = CompContNet2(self)
        self.behaviours.append(comp)
        
        # Log agent creation.
        logger.log_agent(
            agent_id=self.aid.name,
            session_id=get_shared_session_id(),
            name=self.aid.name,
            state="Created"
        )
        
        logger.log_event(
            event_type="participant_created",
            agent_id=self.aid.name,
            data={"available_power": pot_disp}
        )

    def on_start(self):
        """Register the agent in the AMS."""
        super().on_start()
        
        logger.log_agent(
            agent_id=self.aid.name,
            session_id=get_shared_session_id(),
            name=self.aid.name,
            state="Active"
        )


if __name__ == "__main__":
    if len(argv) < 2:
        print("Usage: python agent_example_4_updated.py <base_port>")
        print("Example: python agent_example_4_updated.py 20000")
        exit(1)

    agents = list()
    
    # AMS configuration.
    ams_config = {'name': 'localhost', 'port': 8000}

    # Shared session.
    session_id = get_shared_session_id()
    
    logger.log_session(
        session_id=session_id,
        name=f"ContractNet_Session_{session_id}",
        state="Started"
    )
    
    # Base port.
    base_port = int(argv[1])

    # Participant list.
    participants = []
    k = 10000  # Port offset for participant agents.

    # Participant 1 (base port - 10000).
    port_part1 = base_port - k
    agent_name_part1 = f'participant_1_{port_part1}@localhost:{port_part1}'
    pot_disp1 = uniform(100.0, 500.0)
    agente_part1 = AgentParticipant(AID(name=agent_name_part1), pot_disp1)
    agente_part1.update_ams(ams_config)
    agents.append(agente_part1)
    participants.append(agent_name_part1)

    # Participant 2 (base port + 10000).
    port_part2 = base_port + k
    agent_name_part2 = f'participant_2_{port_part2}@localhost:{port_part2}'
    pot_disp2 = uniform(100.0, 500.0)
    agente_part2 = AgentParticipant(AID(name=agent_name_part2), pot_disp2)
    agente_part2.update_ams(ams_config)
    agents.append(agente_part2)
    participants.append(agent_name_part2)

    # Initiator (base port).
    agent_name_init = f'initiator_{base_port}@localhost:{base_port}'
    agente_init = AgentInitiator(AID(name=agent_name_init), participants)
    agente_init.update_ams(ams_config)
    agents.append(agente_init)
    
    logger.log_event(
        event_type="test_started",
        data={
            "example": "agent_example_4",
            "num_agents": len(agents),
            "base_port": base_port,
            "participants": participants,
            "required_power": 60.0
        }
    )
    
    start_loop(agents)
