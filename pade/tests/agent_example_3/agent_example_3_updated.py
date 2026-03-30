#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Exemplo de Requisição FIPA-Request - Versão Python 3.12.11 com logging CSV
Adaptado por Douglas Barros em 04 de março de 2026
"""

from pade.misc.utility import display_message, start_loop
from pade.core.agent import Agent
from pade.acl.messages import ACLMessage
from pade.acl.aid import AID
from pade.behaviours.protocols import FipaRequestProtocol, TimedBehaviour, FipaSubscribeProtocol
from pade.misc.data_logger import get_shared_session_id, logger
from datetime import datetime
from sys import argv
from pickle import loads

class CompRequest(FipaRequestProtocol):
    """FIPA Request Behaviour do TimeAgent (servidor)."""
    
    def __init__(self, agent):
        super().__init__(agent=agent, message=None, is_initiator=False)

    def handle_request(self, message):
        """Processa requisição recebida e responde com a hora atual."""
        super().handle_request(message)
        display_message(self.agent.aid.localname, '✅ Requisição de hora recebida')
        
        logger.log_event(
            event_type="request_received",
            agent_id=self.agent.aid.name,
            data={"from": message.sender.name}
        )
        
        now = datetime.now()
        reply = message.create_reply()
        reply.set_performative(ACLMessage.INFORM)
        current_time = now.strftime('%d/%m/%Y - %H:%M:%S')
        reply.set_content(current_time)
        
        self.agent.send(reply)
        display_message(self.agent.aid.localname, f'📤 Resposta enviada: {current_time}')
        
        logger.log_event(
            event_type="response_sent",
            agent_id=self.agent.aid.name,
            data={"to": message.sender.name, "time": current_time}
        )


class TableMonitorBehaviour(FipaSubscribeProtocol):
    """Comportamento para monitorar atualizações da tabela de agentes."""
    
    def __init__(self, agent):
        super().__init__(agent, message=None, is_initiator=False)
        self.target_agent = None
    
    def set_target(self, target_name):
        """Define qual agente estamos procurando."""
        self.target_agent = target_name
    
    def handle_inform(self, message):
        """Recebe atualização da tabela de agentes."""
        try:
            table = loads(message.content)
            display_message(self.agent.aid.name, f'📋 Tabela atualizada com {len(table)} agentes')
            
            # Verifica se o agente alvo está na tabela
            if self.target_agent and self.target_agent in table:
                display_message(self.agent.aid.name, f'✅ Agente {self.target_agent} ENCONTRADO na tabela!')
                
                # Agenda o início das requisições
                self.agent.call_later(1.0, self.agent.start_requests)
        except Exception as e:
            display_message(self.agent.aid.name, f'❌ Erro ao processar tabela: {e}')


class CompRequest2(FipaRequestProtocol):
    """FIPA Request Behaviour do ClockAgent (cliente)."""
    
    def __init__(self, agent, message):
        super().__init__(agent=agent, message=message, is_initiator=True)

    def handle_inform(self, message):
        """Processa a resposta recebida do TimeAgent."""
        display_message(self.agent.aid.localname, f'🎯 Hora recebida: {message.content}')
        
        logger.log_event(
            event_type="inform_received",
            agent_id=self.agent.aid.name,
            data={
                "from": message.sender.name,
                "time": message.content
            }
        )


class ComportTemporal(TimedBehaviour):
    """Comportamento temporizado do ClockAgent para enviar requisições periódicas."""
    
    def __init__(self, agent, time, message):
        super().__init__(agent, time)
        self.message = message
        self.request_count = 0
        self.enabled = False

    def enable(self):
        """Ativa o envio de requisições."""
        self.enabled = True
        display_message(self.agent.aid.name, '▶️ Requisições ativadas!')

    def on_time(self):
        """Método chamado a cada intervalo de tempo."""
        super().on_time()
        
        if not self.enabled:
            return
        
        self.request_count += 1
        
        target_name = self.message.receivers[0].name if self.message.receivers else None
        
        if target_name and target_name in self.agent.agentInstance.table:
            display_message(self.agent.aid.localname, f'📤 Enviando requisição #{self.request_count} para {target_name}')
            
            logger.log_event(
                event_type="request_sent",
                agent_id=self.agent.aid.name,
                data={
                    "request_count": self.request_count,
                    "to": target_name
                }
            )
            
            self.agent.send(self.message)
        else:
            display_message(self.agent.aid.localname, f'⏳ Destino {target_name} não disponível (requisição #{self.request_count} adiada)')


class TimeAgent(Agent):
    """Agente servidor que fornece a hora atual."""
    
    def __init__(self, aid):
        super().__init__(aid=aid, debug=False)

        self.comport_request = CompRequest(self)
        self.behaviours.append(self.comport_request)
        
        logger.log_agent(
            agent_id=self.aid.name,
            session_id=get_shared_session_id(),
            name=self.aid.name,
            state="Created"
        )
    
    def on_start(self):
        super().on_start()
        display_message(self.aid.name, '⏰ TimeAgent pronto - aguardando requisições...')
        
        logger.log_agent(
            agent_id=self.aid.name,
            session_id=get_shared_session_id(),
            name=self.aid.name,
            state="Active"
        )
        
        logger.log_event(
            event_type="agent_started",
            agent_id=self.aid.name,
            data={"port": self.aid.port, "role": "server"}
        )


class ClockAgent(Agent):
    """Agente cliente que requisita a hora periodicamente."""
    
    def __init__(self, aid, time_agent_name):
        super().__init__(aid=aid, debug=False)
        self.time_agent_name = time_agent_name
        self.requests_enabled = False

        # Mensagem que requisita hora do TimeAgent
        self.message = ACLMessage(ACLMessage.REQUEST)
        self.message.set_protocol(ACLMessage.FIPA_REQUEST_PROTOCOL)
        self.message.add_receiver(AID(name=time_agent_name))
        self.message.set_content('time')

        # Comportamentos
        self.comport_request = CompRequest2(self, self.message)
        self.comport_temp = ComportTemporal(self, 8.0, self.message)
        self.table_monitor = TableMonitorBehaviour(self)
        self.table_monitor.set_target(time_agent_name)

        self.behaviours.append(self.comport_request)
        self.behaviours.append(self.comport_temp)
        self.system_behaviours.append(self.table_monitor)
        
        logger.log_agent(
            agent_id=self.aid.name,
            session_id=get_shared_session_id(),
            name=self.aid.name,
            state="Created"
        )
    
    def on_start(self):
        super().on_start()
        display_message(self.aid.name, f'🕐 ClockAgent iniciado - aguardando tabela de agentes...')
        
        logger.log_agent(
            agent_id=self.aid.name,
            session_id=get_shared_session_id(),
            name=self.aid.name,
            state="Active"
        )
        
        logger.log_event(
            event_type="agent_started",
            agent_id=self.aid.name,
            data={"port": self.aid.port, "role": "client", "target": self.time_agent_name}
        )
    
    def start_requests(self):
        """Ativa o envio de requisições."""
        if not self.requests_enabled:
            self.requests_enabled = True
            self.comport_temp.enable()
            display_message(self.aid.name, f'🚀 Iniciando requisições periódicas para {self.time_agent_name}')


if __name__ == '__main__':
    if len(argv) < 2:
        print("Uso: python agent_example_3_updated.py <porta_base>")
        print("Exemplo: python agent_example_3_updated.py 20000")
        exit(1)

    agents = list()
    ams_config = {'name': 'localhost', 'port': 8000}
    session_id = get_shared_session_id()
    
    logger.log_session(
        session_id=session_id,
        name=f"FIPARequest_Session_{session_id}",
        state="Started"
    )
    
    base_port = int(argv[1])
    
    # TimeAgent
    time_port = base_port
    time_agent_name = f'agent_time_{time_port}@localhost:{time_port}'
    time_agent = TimeAgent(AID(name=time_agent_name))
    time_agent.update_ams(ams_config)
    agents.append(time_agent)
    display_message('Sistema', f'⏰ TimeAgent criado: {time_agent_name}')
    
    # ClockAgent
    clock_port = base_port + 1
    clock_agent_name = f'agent_clock_{clock_port}@localhost:{clock_port}'
    clock_agent = ClockAgent(AID(name=clock_agent_name), time_agent_name)
    clock_agent.update_ams(ams_config)
    agents.append(clock_agent)
    display_message('Sistema', f'🕐 ClockAgent criado: {clock_agent_name}')

    display_message('Sistema', f'🚀 Iniciando {len(agents)} agentes...')
    display_message('Sistema', f'📡 ClockAgent aguardando tabela para iniciar requisições')
    
    logger.log_event(
        event_type="test_started",
        data={
            "example": "agent_example_3",
            "num_agents": len(agents),
            "time_port": time_port,
            "clock_port": clock_port,
            "interval": 8.0
        }
    )
    
    start_loop(agents)
