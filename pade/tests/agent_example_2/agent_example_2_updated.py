#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hello World temporal in PADE - Versão Python 3.12.11 com logging CSV
Adaptado por Douglas Barros em 04 de março de 2026

Este exemplo demonstra o uso de TimedBehaviour para ações periódicas.
Os agentes exibem "Hello World!" a cada 1 segundo.
"""

from pade.misc.utility import display_message, start_loop
from pade.core.agent import Agent
from pade.acl.aid import AID
from pade.behaviours.protocols import TimedBehaviour
from pade.misc.data_logger import get_shared_session_id, logger
from sys import argv

class ComportTemporal(TimedBehaviour):
    """Comportamento que executa ações em intervalos regulares."""
    
    def __init__(self, agent, time):
        # Sintaxe moderna de super()
        super().__init__(agent, time)
        self.execution_count = 0

    def on_time(self):
        """Método chamado a cada intervalo de tempo definido."""
        super().on_time()
        self.execution_count += 1
        
        # Mantém a saída alinhada ao exemplo legado.
        display_message(self.agent.aid.localname, 'Hello World!')
        
        # Log da execução do comportamento
        logger.log_event(
            event_type="timed_behaviour_execution",
            agent_id=self.agent.aid.name,
            data={
                "execution_count": self.execution_count,
                "interval": self.time
            }
        )


class AgenteHelloWorld(Agent):
    """Agente que utiliza comportamento temporizado para exibir mensagens."""
    
    def __init__(self, aid, session_id):
        super().__init__(aid=aid, debug=False)
        self.session_id = session_id

        # Cria o comportamento temporizado (executa a cada 1 segundo)
        comp_temp = ComportTemporal(self, 1.0)
        self.behaviours.append(comp_temp)
        
        # Log da criação do agente
        logger.log_agent(
            agent_id=self.aid.name,
            session_id=self.session_id,
            name=self.aid.name,
            state="Created"
        )
    
    def on_start(self):
        """Método chamado quando o agente inicia e registra no AMS."""
        super().on_start()
        display_message(self.aid.name, 'Agente registrado no AMS - Iniciando comportamentos temporizados...')
        
        # Log do agente ativo
        logger.log_agent(
            agent_id=self.aid.name,
            session_id=self.session_id,
            name=self.aid.name,
            state="Active"
        )
        
        # Log do evento de inicialização
        logger.log_event(
            event_type="agent_started",
            agent_id=self.aid.name,
            data={"port": self.aid.port}
        )
    
if __name__ == '__main__':
    # Verifica se a porta base foi fornecida
    if len(argv) < 2:
        print("Uso: python agent_example_2_updated.py <porta_base>")
        print("Exemplo: python agent_example_2_updated.py 20000")
        exit(1)
    
    agents_per_process = 2
    c = 0
    agents = list()
    
    # Configuração do AMS
    ams_config = {'name': 'localhost', 'port': 8000}
    
    # Sessão única para todos os agentes
    session_id = get_shared_session_id()
    
    # Log da sessão
    logger.log_session(
        session_id=session_id,
        name=f"TimedHelloWorld_Session_{session_id}",
        state="Started"
    )
    
    for i in range(agents_per_process):
        port = int(argv[1]) + c
        agent_name = f'agent_timed_{port}@localhost:{port}'
        
        # Cria o agente
        agente_hello = AgenteHelloWorld(AID(name=agent_name), session_id)
        
        # Configura o AMS para o agente
        agente_hello.update_ams(ams_config)
        
        agents.append(agente_hello)
        display_message('Sistema', f'Agente {agent_name} criado')
        c += 1000
    
    display_message('Sistema', f'Iniciando {len(agents)} agentes com comportamentos temporizados...')
    
    # Log do início da execução
    logger.log_event(
        event_type="test_started",
        data={
            "example": "agent_example_2",
            "num_agents": len(agents),
            "base_port": argv[1],
            "behaviour_interval": 1.0
        }
    )
    
    start_loop(agents)
