#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Integração PADE + Mosaik Co-Simulation
Módulo com Registro Nativo FIPA-ACL no Sniffer - GREI/UFC
"""

import json
from pade.misc.utility import display_message, start_loop
from pade.core.agent import Agent
from pade.acl.aid import AID
from pade.acl.messages import ACLMessage
from pade.drivers.mosaik_driver import MosaikCon
from pade.misc.data_logger import logger
from sys import argv
from datetime import datetime

MOSAIK_MODELS = {
    'api_version': '3.0',
    'type': 'time-based',
    'models': {
        'D': {
            'public': True,
            'params': ['init_val', 'medium_val'],
            'attrs': ['val_in', 'val_out'],
        },
    },
}

class MosaikSim(MosaikCon):

    def __init__(self, agent):
        super().__init__(MOSAIK_MODELS, agent)
        self.entities = list()

    def create(self, num, model, init_val, medium_val):
        entities_info = list()
        for i in range(num):
            self.entities.append(init_val)
            display_message(self.agent.aid.localname, f"Entity D: init={init_val}, med={medium_val}")
            entities_info.append({
                'eid': f"{self.sim_id}.{str(i)}", 
                'type': model, 
                'rel': []
            })
        return entities_info

    def step(self, time, inputs, max_advance=0):
        if time % 501 == 0 and time != 0:
            display_message(self.agent.aid.localname, f'step: {time:4d}')
        
        if time % 1001 == 0 and time != 0:
            yield self.get_progress()
            
        if time % 2001 == 0 and time != 0:
            data = {'ExampleSim-0.0.0': ['val_out']}
            yield self.get_data_async(data)
            
        return time + self.time_step

    def handle_get_data(self, data):
        display_message(self.agent.aid.localname, f"Handle Data: {str(data)}")
        # Em vez de apenas imprimir, manda o agente registrar no PADE!
        self.agent.registrar_dados_mosaik(data)

    def handle_set_data(self):
        display_message(self.agent.aid.localname, 'Success in set_data process')

    def handle_get_progress(self, progress):
        display_message(self.agent.aid.localname, f'progress: {progress:2.2f}%')

    def get_data(self, outputs):
        response = dict()
        for model, list_values in outputs.items():
            response[model] = dict()
            for value in list_values:
                response[model][value] = 1.0
        return response

class AgenteHelloWorld(Agent):
    def __init__(self, aid):
        super().__init__(aid=aid, debug=False)
        self.mosaik_sim = MosaikSim(self)

    def on_start(self):
        super().on_start()
        display_message(self.aid.localname, '🌐 Agente Mosaik Online - GREI/UFC')

    def registrar_dados_mosaik(self, dados_mosaik):
        """
        Empacota os dados do simulador em uma mensagem FIPA-ACL 
        para que o Sniffer do PADE possa gravar no messages.csv
        """
        mensagem = ACLMessage(ACLMessage.INFORM)
        mensagem.set_sender(self.aid)
        mensagem.add_receiver(self.aid) # Envia para si mesmo
        mensagem.set_ontology('mosaik_data') # Facilita a filtragem depois
        
        # Converte o dicionário do Mosaik para String JSON
        mensagem.set_content(json.dumps(dados_mosaik))
        
        # Dispara na rede do PADE
        self.send(mensagem)

if __name__ == '__main__':
    ams_config = {'name': 'localhost', 'port': 8000}
    session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    logger.log_session(session_id=session_id, name="Mosaik_FIPA_Logging", state="Started")

    agents_per_process = 1 
    c = 0
    agents = list()
    for i in range(agents_per_process):
        port = int(argv[1]) if len(argv) > 1 else 20000
        port += c
        agent_name = f'agent_example_{port}@localhost:{port}'
        agente_hello = AgenteHelloWorld(AID(name=agent_name))
        agente_hello.update_ams(ams_config)
        agents.append(agente_hello)
        c += 500

    start_loop(agents)