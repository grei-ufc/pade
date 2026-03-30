#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Exemplo de Protocolo FIPA-ContractNet - Versão Python 3.12.11 com logging CSV
Adaptado por Douglas Barros em 04 de março de 2026

Este exemplo demonstra o protocolo FIPA-ContractNet (leilão):
- AgentInitiator: envia CFP e escolhe a melhor proposta
- AgentParticipant: responde com propostas (potência disponível)
- O vencedor é aquele com maior potência
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
    Comportamento do Iniciador (Initiator) no protocolo ContractNet.
    Envia CFP, coleta propostas, seleciona a melhor e responde.
    """
    
    def __init__(self, agent, message):
        # Sintaxe moderna de super()
        super().__init__(agent=agent, message=message, is_initiator=True)
        self.cfp = message
        self.proposals_received = []
        
        # Log do início do protocolo
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
        Analisa todas as propostas recebidas e seleciona a melhor
        (maior potência disponível).
        """
        super().handle_all_proposes(proposes)

        best_proposer = None
        higher_power = 0.0
        other_proposers = list()
        
        display_message(self.agent.aid.name, 'Analyzing proposals...')
        
        # Log do número de propostas recebidas
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
                
                # Log de cada proposta
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

        # Envia REJECT_PROPOSAL para os perdedores
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

        # Envia ACCEPT_PROPOSAL para o vencedor
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
        """Recebe confirmação do vencedor."""
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
        """Recebe recusa de participante."""
        super().handle_refuse(message)
        display_message(self.agent.aid.name, 'REFUSE message received')
        
        logger.log_event(
            event_type="refuse_received",
            agent_id=self.agent.aid.name,
            data={"from": message.sender.name}
        )

    def handle_propose(self, message):
        """Recebe proposta de participante."""
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
    Comportamento do Participante (Participant) no protocolo ContractNet.
    Recebe CFP, envia proposta e aguarda resultado.
    """
    
    def __init__(self, agent):
        super().__init__(agent=agent, message=None, is_initiator=False)

    def handle_cfp(self, message):
        """Recebe chamada de proposta e prepara resposta."""
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

        # Envia proposta
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
        """Recebe rejeição (não foi o vencedor)."""
        super().handle_reject_propose(message)
        display_message(self.agent.aid.name,
                        'REJECT_PROPOSAL message received')
        
        logger.log_event(
            event_type="reject_received",
            agent_id=self.agent.aid.name,
            data={"from": message.sender.name}
        )

    def handle_accept_propose(self, message):
        """Recebe aceitação (foi o vencedor!)."""
        super().handle_accept_propose(message)
        display_message(self.agent.aid.name,
                        'ACCEPT_PROPOSE message received')

        logger.log_event(
            event_type="accept_received",
            agent_id=self.agent.aid.name,
            data={"from": message.sender.name}
        )

        # Confirma com INFORM
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
    """Agente Iniciador do protocolo ContractNet."""
    
    def __init__(self, aid, participants):
        super().__init__(aid=aid, debug=False)
        self.participants = participants
        
        # Log da criação
        logger.log_agent(
            agent_id=self.aid.name,
            session_id=get_shared_session_id(),
            name=self.aid.name,
            state="Created"
        )

        # Cria mensagem CFP
        self.message = ACLMessage(ACLMessage.CFP)
        self.message.set_protocol(ACLMessage.FIPA_CONTRACT_NET_PROTOCOL)
        self.message.set_content('60.0')  # Potência necessária

        for participant in participants:
            self.message.add_receiver(AID(name=participant))

        # Agenda início do protocolo
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
        """Registro no AMS."""
        super().on_start()
        
        logger.log_agent(
            agent_id=self.aid.name,
            session_id=get_shared_session_id(),
            name=self.aid.name,
            state="Active"
        )

    def launch_contract_net_protocol(self):
        """Inicia o protocolo ContractNet."""
        comp = CompContNet1(self, self.message)
        self.behaviours.append(comp)
        comp.on_start()


class AgentParticipant(Agent):
    """Agente Participante do protocolo ContractNet."""
    
    def __init__(self, aid, pot_disp):
        super().__init__(aid=aid, debug=False)
        self.pot_disp = pot_disp  # Potência disponível (entre 100 e 500 VA)

        comp = CompContNet2(self)
        self.behaviours.append(comp)
        
        # Log da criação
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
        """Registro no AMS."""
        super().on_start()
        
        logger.log_agent(
            agent_id=self.aid.name,
            session_id=get_shared_session_id(),
            name=self.aid.name,
            state="Active"
        )


if __name__ == "__main__":
    if len(argv) < 2:
        print("Uso: python agent_example_4_updated.py <porta_base>")
        print("Exemplo: python agent_example_4_updated.py 20000")
        exit(1)

    agents = list()
    
    # Configuração do AMS
    ams_config = {'name': 'localhost', 'port': 8000}
    
    # Sessão única
    session_id = get_shared_session_id()
    
    logger.log_session(
        session_id=session_id,
        name=f"ContractNet_Session_{session_id}",
        state="Started"
    )
    
    # Porta base
    base_port = int(argv[1])
    
    # Lista de participantes
    participants = []
    k = 10000  # Offset para portas dos participantes
    
    # Participante 1 (porta base - 10000)
    port_part1 = base_port - k
    agent_name_part1 = f'participant_1_{port_part1}@localhost:{port_part1}'
    pot_disp1 = uniform(100.0, 500.0)
    agente_part1 = AgentParticipant(AID(name=agent_name_part1), pot_disp1)
    agente_part1.update_ams(ams_config)
    agents.append(agente_part1)
    participants.append(agent_name_part1)

    # Participante 2 (porta base + 10000)
    port_part2 = base_port + k
    agent_name_part2 = f'participant_2_{port_part2}@localhost:{port_part2}'
    pot_disp2 = uniform(100.0, 500.0)
    agente_part2 = AgentParticipant(AID(name=agent_name_part2), pot_disp2)
    agente_part2.update_ams(ams_config)
    agents.append(agente_part2)
    participants.append(agent_name_part2)

    # Iniciador (porta base)
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
