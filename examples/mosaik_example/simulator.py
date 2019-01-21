"""
The example simulator contains two models:

- Model A produces continuously increasing integers.
- Model B consumes a value and yields the last value consumed.

"""

def model_a(i):
    while True:
        yield i
        i += 1


def model_b(val):
    while True:
        new_val = yield val
        if new_val is not None:
            val = new_val


class Simulator(object):
    models = {
        'A': model_a,
        'B': model_b,
    }

    def __init__(self, model, num_inst, init_val):
        self.model = model
        self.instances = []
        self.results = []

        for i in range(num_inst):
            inst = Simulator.models[model](init_val)
            self.results.append(next(inst))  # Initialize generator
            self.instances.append(inst)

    def step(self, inputs):
        self.results = [inst.send(input)
                        for inst, input in zip(self.instances, inputs)]
