#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PADE + Mosaik co-simulation integration.
Module with native FIPA-ACL registration through the Sniffer - GREI/UFC.
"""

import json
from pade.misc.utility import display_message, start_loop
from pade.core.agent import Agent
from pade.acl.aid import AID
from pade.acl.messages import ACLMessage
from pade.drivers.mosaik_driver import MosaikCon
from pade.misc.data_logger import get_shared_session_id, logger
from sys import argv

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
        display_message(self.agent.aid.localname, f"Handle data: {str(data)}")
        # Instead of only printing, ask the agent to register the data in PADE.
        self.agent.register_mosaik_data(data)

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

class HelloWorldAgent(Agent):
    def __init__(self, aid):
        super().__init__(aid=aid, debug=False)
        self.mosaik_sim = MosaikSim(self)

    def on_start(self):
        super().on_start()
        display_message(self.aid.localname, '🌐 Mosaik agent online - GREI/UFC')

    def register_mosaik_data(self, mosaik_data):
        """
        Pack simulator data into a FIPA-ACL message so the PADE
        Sniffer can store it in `messages.csv`.
        """
        message = ACLMessage(ACLMessage.INFORM)
        message.set_sender(self.aid)
        message.add_receiver(self.aid)  # Send to the same agent for logging.
        message.set_ontology('mosaik_data')  # Makes later filtering easier.
        
        # Convert the Mosaik dictionary to a JSON string.
        message.set_content(json.dumps(mosaik_data))
        
        # Dispatch through the PADE network.
        self.send(message)

if __name__ == '__main__':
    ams_config = {'name': 'localhost', 'port': 8000}
    session_id = get_shared_session_id()
    logger.log_session(session_id=session_id, name="Mosaik_FIPA_Logging", state="Started")

    agents_per_process = 1 
    c = 0
    agents = list()
    for i in range(agents_per_process):
        port = int(argv[1]) if len(argv) > 1 else 20000
        port += c
        agent_name = f'agent_example_{port}@localhost:{port}'
        hello_agent = HelloWorldAgent(AID(name=agent_name))
        hello_agent.update_ams(ams_config)
        agents.append(hello_agent)
        c += 500

    start_loop(agents)
