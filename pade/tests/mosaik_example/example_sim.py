"""
Mosaik interface for the example simulator.
Migrated to API 3.0+ with None-value filtering (GREI/UFC).
"""
import logging
import mosaik_api_v3 as mosaik_api
import simulator

logger = logging.getLogger('example_sim')

example_sim_meta = {
    'api_version': '3.0',
    'type': 'time-based',
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
        },
    },
    'extra_methods': [
        'example_method',
    ],
}

class ExampleSim(mosaik_api.Simulator):
    def __init__(self):
        super().__init__(example_sim_meta)
        self.step_size = None
        self.simulators = []
        self.value = None

    def init(self, sid, time_resolution=1.0, step_size=1, **kwargs):
        self.sid = sid
        self.step_size = step_size
        return self.meta

    def create(self, num, model, init_val):
        sim_id = len(self.simulators)
        sim = simulator.Simulator(model, num, init_val)
        self.simulators.append(sim)
        return [{'eid': '%s.%s' % (sim_id, eid), 'type': model, 'rel': []}
                for eid, inst in enumerate(sim.instances)]

    def step(self, time, inputs, max_advance=0):
        for sid, sim in enumerate(self.simulators):
            sim_inputs = [None for i in sim.instances]
            for i, _ in enumerate(sim_inputs):
                eid = '%s.%s' % (sid, i)
                if eid in inputs:
                    # --- Fix: filter out None values before summing inputs. ---
                    val_list = [v for v in inputs[eid]['val_in'].values() if v is not None]
                    sim_inputs[i] = sum(val_list) if val_list else 0
                    # ----------------------------------------------------------

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
