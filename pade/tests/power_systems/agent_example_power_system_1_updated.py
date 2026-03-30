#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Integração PADE + IEEE 13-Bus System
Migrado para Python 3.12.11 - Projeto GREI/UFC
"""

from pade.misc.utility import display_message, start_loop
from pade.core.agent import Agent
from pade.acl.messages import ACLMessage
from pade.acl.aid import AID
from pade.behaviours.protocols import FipaRequestProtocol, TimedBehaviour
from pade.misc.data_logger import logger

import numpy as np
import pickle
from sys import argv
from datetime import datetime

# Dependências da Matriz Elétrica
from mygrid.power_flow.backward_forward_sweep_3p import calc_power_flow
from ieee_13_bus_system import grid_elements, Load_Node675
import random

# --- COMPORTAMENTOS ---

class CompRequest(FipaRequestProtocol):
    """Comportamento que recebe ordens, calcula o fluxo e retorna a tensão no Nó 675."""
    def __init__(self, agent):
        super().__init__(agent=agent, message=None, is_initiator=False)

    def handle_request(self, message):
        super().handle_request(message)
        display_message(self.agent.aid.localname, '📥 Ordem recebida. Iniciando cálculo de fluxo de carga...')
        
        try:
            # 1. Modifica a carga aleatoriamente para simular variabilidade no sistema
            pp = np.array([[485+1j*190, 68+1j*60, 290+1j*212]]) * 1e3 * random.uniform(0, 3)
            pp.shape = (3, 1)
            Load_Node675.pp = pp
            
            # 2. Executa o algoritmo Backward-Forward Sweep
            calc_power_flow(grid_elements.dist_grids['F0'])

            # 3. Serializa a Matriz NumPy (Atenção: Essencial para Python 3.12)
            voltage_array = Load_Node675.vp
            serialized_voltage = pickle.dumps(voltage_array)

            reply = message.create_reply()
            reply.set_performative(ACLMessage.INFORM)
            reply.set_content(serialized_voltage)
            self.agent.send(reply)
            
        except Exception as e:
            display_message(self.agent.aid.localname, f"❌ Erro durante o fluxo de carga: {e}")

class CompRequest2(FipaRequestProtocol):
    """Comportamento do Agente de Supervisão que recebe as tensões calculadas."""
    def __init__(self, agent, message):
        super().__init__(agent=agent, message=message, is_initiator=True)

    def handle_inform(self, message):
        try:
            # Extrai os dados do pacote serializado
            raw_content = message.content
            if isinstance(raw_content, bytes):
                vp_array = pickle.loads(raw_content)
            else:
                vp_array = raw_content
                
            display_message(self.agent.aid.localname, f"⚡ Tensão atualizada no Nó 675:\n{vp_array}")
        except Exception as e:
            display_message(self.agent.aid.localname, f"Falha na extração de dados: {e}")

class ComportTemporal(TimedBehaviour):
    """Gatilho temporal: Dispara o cálculo a cada 3 segundos."""
    def __init__(self, agent, time, message):
        super().__init__(agent, time)
        self.message = message

    def on_time(self):
        super().on_time()
        display_message(self.agent.aid.localname, "⏱️ Disparo temporal! Solicitando leitura de fluxo de carga.")
        self.agent.send(self.message)

# --- AGENTES ---

class PowerFlowAgent(Agent):
    """Agente responsável pela matemática do sistema elétrico."""
    def __init__(self, aid):
        super().__init__(aid=aid, debug=False)

    def on_start(self):
        super().on_start()
        self.behaviours.append(CompRequest(self))

class RequestVoltageAgent(Agent):
    """Agente de supervisão da rede de distribuição."""
    def __init__(self, aid, target_agent_name):
        super().__init__(aid=aid)

        message = ACLMessage(ACLMessage.REQUEST)
        message.set_protocol(ACLMessage.FIPA_REQUEST_PROTOCOL)
        message.add_receiver(AID(name=target_agent_name))
        message.set_content('Solicitar_Leitura_Nó_675')

        self.comport_request = CompRequest2(self, message)
        # Timer ajustado para 3.0s para dar fôlego ao processador no Pop!_OS
        self.comport_temp = ComportTemporal(self, 3.0, message)

    def on_start(self):
        super().on_start()
        self.behaviours.append(self.comport_request)
        self.behaviours.append(self.comport_temp)

# --- EXECUÇÃO ---

if __name__ == '__main__':
    ams_config = {'name': 'localhost', 'port': 8000}
    session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    logger.log_session(session_id=session_id, name="PowerFlow_IEEE13", state="Started")

    base_port = int(argv[1]) if len(argv) > 1 else 20000
    agents_per_process = 2
    c = 0
    agents = list()
    
    for i in range(agents_per_process):
        port = base_port + c
        
        pf_agent_name = f'power_flow_agent_{port}@localhost:{port}'
        pf_agent = PowerFlowAgent(AID(name=pf_agent_name))
        pf_agent.update_ams(ams_config)
        agents.append(pf_agent)
        
        req_agent_name = f'request_voltage_agent_{port - 10000}@localhost:{port - 10000}'
        req_agent = RequestVoltageAgent(AID(name=req_agent_name), pf_agent_name)
        req_agent.update_ams(ams_config)
        agents.append(req_agent)

        c += 500

    display_message('Sistema', "🎬 Iniciando Integração Multiagente + Fluxo de Carga (IEEE-13)...")
    start_loop(agents)