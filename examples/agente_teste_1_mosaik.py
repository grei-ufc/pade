#!coding=utf-8
# Hello world in PADE!
#
# Criado por Lucas S Melo em 21 de julho de 2015 - Fortaleza, Ceará - Brasil

from pade.misc.utility import display_message
from pade.misc.common import PadeSession
from pade.core.agent import Agent
from pade.acl.aid import AID
from pade.drivers.mosaik_driver import MosaikCon

from time import sleep

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
            print(init_val)
            print(medium_val)
            entities_info.append(
                {'eid': self.sim_id + '.' + str(i), 'type': model, 'rel': []})
        return entities_info

    def step(self, time, inputs):
        print(time)
        #print(inputs)
        if time % 1001 == 0 and time != 0:
            self.get_progress()
        if time % 2001 == 0 and time != 0:
            data = {'ExampleSim-0.0.0': ['val_out']}
            self.get_data_async(data)
        return time + self.time_step

    def handle_get_data(self, data):
        print(data)

    def handle_set_data(self):
        print('sucess in set_data process')

    def handle_get_progress(self, progress):
        print('------------')
        print(progress)

    def get_data(self, outputs):
        response = dict()
        for model, list_values in outputs.items():
            response[model] = dict()
            for value in list_values:
                response[model][value] = 1.0
        return response


class AgenteHelloWorld(Agent):
    def __init__(self, aid):
        super(AgenteHelloWorld, self).__init__(aid=aid, debug=True)
        self.mosaik_sim = MosaikSim(self)
        display_message(self.aid.localname, 'Hello World!')


def config_agents():

    agents = list()

    agente_hello = AgenteHelloWorld(AID(name='agente_hello@localhost:1234'))
    agents.append(agente_hello)

    s = PadeSession()
    s.add_all_agents(agents)
    s.register_user(username='lucassm', email='lucas@gmail.com', password='12345')

    return s

if __name__ == '__main__':

    s = config_agents()
    s.start_loop()
