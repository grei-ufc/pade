#!coding=utf-8
# Hello world in PADE!
#
# Criado por Lucas S Melo em 21 de julho de 2015 - Fortaleza, Ceará - Brasil


from pade.misc.utility import display_message, start_loop
from pade.core.agent import Agent
from pade.acl.aid import AID
from pade.drivers.mosaik_driver import MosaikCon
from sys import argv

MOSAIK_MODELS = {
    'api_version': '2.2',
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
        super(MosaikSim, self).__init__(MOSAIK_MODELS, agent)
        self.entities = list()

    def create(self, num, model, init_val, medium_val):
        entities_info = list()
        for i in range(num):
            self.entities.append(init_val)
            display_message(self.agent.aid.localname, str(init_val))
            display_message(self.agent.aid.localname, str(medium_val))
            entities_info.append(
                {'eid': self.sim_id + '.' + str(i), 'type': model, 'rel': []})
        return entities_info

    def step(self, time, inputs):
        if time % 501 == 0 and time != 0:
            display_message(self.agent.aid.localname, 'step: {:4d}'.format(time))
            #display_message(self.agent.aid.localname, str(inputs))
        if time % 1001 == 0 and time != 0:
            yield self.get_progress()
        if time % 2001 == 0 and time != 0:
            data = {'ExampleSim-0.0.0': ['val_out']}
            yield self.get_data_async(data)
        return time + self.time_step

    def handle_get_data(self, data):
        display_message(self.agent.aid.localname, str(data))

    def handle_set_data(self):
        display_message(self.agent.aid.localname, 'sucess in set_data process')

    def handle_get_progress(self, progress):
        display_message(self.agent.aid.localname, 'progress: {:2.2f}%'.format(progress))

    def get_data(self, outputs):
        response = dict()
        for model, list_values in outputs.items():
            response[model] = dict()
            for value in list_values:
                response[model][value] = 1.0
        return response


class AgenteHelloWorld(Agent):
    def __init__(self, aid):
        super(AgenteHelloWorld, self).__init__(aid=aid, debug=False)
        self.mosaik_sim = MosaikSim(self)
        display_message(self.aid.localname, 'Hello World!')


if __name__ == '__main__':

    agents_per_process = 3
    c = 0
    agents = list()
    for i in range(agents_per_process):
        port = int(argv[1]) + c
        agent_name = 'agent_example_{}@localhost:{}'.format(port, port)
        agente_hello = AgenteHelloWorld(AID(name=agent_name))
        agents.append(agente_hello)
        c += 500

    start_loop(agents)
