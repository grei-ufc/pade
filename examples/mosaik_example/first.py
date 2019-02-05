import mosaik

sim_config = {
    'ExampleSim': {'python': 'example_sim:ExampleSim'},
    'PadeSim': {'connect': 'localhost:20000'}
}


def create_scenario(world):
    exsim1 = world.start('ExampleSim')
    exsim2 = world.start('ExampleSim')
    exsim3 = world.start('PadeSim')

    a = [exsim1.A(init_val=0) for i in range(3)]
    b = exsim2.B.create(2, init_val=0)
    d = exsim3.D.create(2, init_val=0, medium_val=1)

    for i, j, k in zip(a, b, d):
        world.connect(i, j, ('val_out', 'val_in'), async_requests=True)
        #world.connect(j, k, ('val_out', 'val_in'))
        world.connect(i, k, ('val_out', 'val_in'), async_requests=True)


world = mosaik.World(sim_config)
create_scenario(world)
world.run(until=10000)