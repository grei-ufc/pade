#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Integração PADE + IEC 61850
Migrado para Python 3.12.11 - Projeto GREI/UFC
"""

from pade.misc.utility import display_message, start_loop
from pade.core.agent import Agent
from pade.acl.messages import ACLMessage
from pade.acl.aid import AID
from pade.behaviours.protocols import FipaRequestProtocol, TimedBehaviour
from pade.misc.data_logger import logger

import sys
# CORREÇÃO AQUI: Importa com o prefixo 'py' e cria um apelido 'iec61850'
import pyiec61850 as iec61850
from sys import argv
from datetime import datetime

# --- ROTINA DE CONTROLE DO HARDWARE ---

def testClient(agent_name):
    tcpPort = 8102
    con = iec61850.IedConnection_create()
    error = iec61850.IedConnection_connect(con, "localhost", tcpPort)
    
    if (error == iec61850.IED_ERROR_OK):
        display_message(agent_name, "🔌 Conectado ao IED físico/simulado!")
        
        # Leitura de Valor Atual (Sensor)
        theVal_SV = "testmodelSENSORS/TTMP1.TmpSv.instMag.f"
        theValType_MX = iec61850.IEC61850_FC_MX
        
        temperatureValue = iec61850.IedConnection_readFloatValue(con, theVal_SV, theValType_MX)
        display_message(agent_name, f"📊 Leitura Inicial do Sensor: {temperatureValue[0]}")
        
        # Escrita de Setpoint (Controle)
        theVal_SP = "testmodelSENSORS/TTMP1.TmpSp.setMag.f"
        theValType_SP = iec61850.IEC61850_FC_SP
        
        newValue = temperatureValue[0] + 10.0
        display_message(agent_name, f"⚙️ Enviando comando de Setpoint: {newValue}")
        
        err = iec61850.IedConnection_writeFloatValue(con, theVal_SP, theValType_SP, newValue)
        
        if err == 0:
            temperatureSetpoint = iec61850.IedConnection_readFloatValue(con, theVal_SP, theValType_SP)
            display_message(agent_name, f"✅ Setpoint atualizado com sucesso no IED para: {temperatureSetpoint[0]}")
        else:
            display_message(agent_name, f"⚠️ Erro ao escrever no IED: Código {err}")
            
        iec61850.IedConnection_close(con)
    else:
        display_message(agent_name, "❌ Falha ao conectar no IED.")
        
    iec61850.IedConnection_destroy(con)

# --- COMPORTAMENTOS ---

class CompRequest(FipaRequestProtocol):
    def __init__(self, agent):
        super().__init__(agent=agent, message=None, is_initiator=False)

    def handle_request(self, message):
        super().handle_request(message)
        display_message(self.agent.aid.localname, '📥 Ordem de controle recebida. Acionando IED...')
        testClient(self.agent.aid.localname)

        reply = message.create_reply()
        reply.set_performative(ACLMessage.INFORM)
        reply.set_content("Manobra Concluída")
        self.agent.send(reply)

class CompRequest2(FipaRequestProtocol):
    def __init__(self, agent, message):
        super().__init__(agent=agent, message=message, is_initiator=True)

    def handle_inform(self, message):
        display_message(self.agent.aid.localname, f"📦 Relatório de Execução: {message.content}")

class ComportTemporal(TimedBehaviour):
    def __init__(self, agent, time, message):
        super().__init__(agent, time)
        self.message = message

    def on_time(self):
        super().on_time()
        display_message(self.agent.aid.localname, "⏱️ Disparo temporal! Enviando solicitação de manobra.")
        self.agent.send(self.message)

# --- AGENTES ---

class IEC61850Agent(Agent):
    def __init__(self, aid):
        super().__init__(aid=aid, debug=False)

    def on_start(self):
        super().on_start()
        self.behaviours.append(CompRequest(self))

class RequestAgent(Agent):
    def __init__(self, aid, target_agent_name):
        super().__init__(aid=aid)

        message = ACLMessage(ACLMessage.REQUEST)
        message.set_protocol(ACLMessage.FIPA_REQUEST_PROTOCOL)
        message.add_receiver(AID(name=target_agent_name))
        message.set_content('executar_manobra')

        self.comport_request = CompRequest2(self, message)
        self.comport_temp = ComportTemporal(self, 10.0, message)

    def on_start(self):
        super().on_start()
        self.behaviours.append(self.comport_request)
        self.behaviours.append(self.comport_temp)

# --- EXECUÇÃO ---

if __name__ == '__main__':
    ams_config = {'name': 'localhost', 'port': 8000}
    session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    logger.log_session(session_id=session_id, name="IEC61850_Integration", state="Started")
    
    base_port = int(argv[1]) if len(argv) > 1 else 20000

    agents_per_process = 2
    c = 0
    agents = list()
    
    for i in range(agents_per_process):
        port = base_port + c
        iec_agent_name = f'iec61850_agent_{port}@localhost:{port}'
        iec_agent = IEC61850Agent(AID(name=iec_agent_name))
        iec_agent.update_ams(ams_config)
        agents.append(iec_agent)
        
        req_agent_name = f'request_agent_{port - 10000}@localhost:{port - 10000}'
        req_agent = RequestAgent(AID(name=req_agent_name), iec_agent_name)
        req_agent.update_ams(ams_config)
        agents.append(req_agent)

        c += 500

    display_message('Sistema', "🎬 Iniciando Integração Multiagente + IEC 61850...")
    start_loop(agents)