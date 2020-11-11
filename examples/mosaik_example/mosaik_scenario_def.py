import mosaik

sim_config = {
    'ExampleSim': {'python': 'generic_python_simulator_mosaik_interface:ExampleSim'},
    'PadeSim': {'connect': 'localhost:20000'}
}


def create_scenario(world):
    exsim = world.start('ExampleSim')
    padesim = world.start('PadeSim')

    exsim_entities = exsim.A.create(3, init_val=0)
    padesim_entities = padesim.D.create(2, init_val=0)

    for i, j in zip(exsim_entities, padesim_entities):
        world.connect(i, j, ('val_out', 'val_in'), async_requests=True)

world = mosaik.World(sim_config)
create_scenario(world)
world.run(until=10000)
