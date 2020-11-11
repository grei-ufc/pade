"""
Mosaik interface for the example simulator.

It more complex than it needs to be to be more flexible and show off various
features of the mosaik API.

"""
import logging

import mosaik_api

import generic_python_simulator

logger = logging.getLogger('example_sim')


example_sim_meta = {
    'models': {
        'A': {
            'public': True,
            'params': ['init_val'],
            'attrs': ['val_in', 'val_out', 'dummy_out'],
        },
        'B': {
            'public': True,
            'params': ['init_val'],
            'attrs': ['val_in', 'val_out', 'dummy_in'],
        }
    },
    'extra_methods': [
        'example_method',
    ],
}


class ExampleSim(mosaik_api.Simulator):
    def __init__(self):
        super(ExampleSim, self).__init__(example_sim_meta)
        self.step_size = None
        self.simulators = []
        self.value = None  # May be set in example_method()

    def init(self, sid, step_size=1):
        self.sid = sid
        self.step_size = step_size
        return self.meta

    def create(self, num, model, init_val):
        sim_id = len(self.simulators)
        sim = generic_python_simulator.Simulator(model, num, init_val)
        self.simulators.append(sim)
        return [{'eid': '{}.{}'.format(sim_id, eid), 'type': model, 'rel': []}
                for eid, inst in enumerate(sim.instances)]

    def step(self, time, inputs):
        if inputs:
            print(inputs)

        for sid, sim in enumerate(self.simulators):
            sim_inputs = [None for i in sim.instances]
            for i, _ in enumerate(sim_inputs):
                eid = '{}.{}'.format(sid, i)
                if eid in inputs:
                    sim_inputs[i] = sum(inputs[eid]['val_in'].values())

            for i in range(self.step_size):
                sim.step(sim_inputs)

        return time + self.step_size

    def get_data(self, outputs):
        data = {}
        for eid, attrs in outputs.items():
            sid, idx = map(int, eid.split('.'))
            data[eid] = {}
            for attr in attrs:
                if attr != 'val_out':
                    continue
                data[eid][attr] = self.simulators[sid].results[idx]
        return data

    def example_method(self, value):
        self.value = value
        return value


def main():
    return mosaik_api.start_simulation(ExampleSim())
