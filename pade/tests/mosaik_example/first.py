#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import mosaik

# Bridge configuration: Mosaik runs `example_sim` as an internal process
# and connects via TCP to PADE listening on port 20000.
sim_config = {
    'ExampleSim': {'python': 'example_sim:ExampleSim'},
    'PadeSim': {'connect': 'localhost:20000'}
}

def create_scenario(world):
    print("🌍 Building the co-simulation scenario...")
    
    # Start the simulators.
    exsim1 = world.start('ExampleSim')
    exsim2 = world.start('ExampleSim')
    exsim3 = world.start('PadeSim')

    # Create the model entities.
    a = [exsim1.A(init_val=0) for i in range(3)]
    b = exsim2.B.create(2, init_val=0)
    d = exsim3.D.create(2, init_val=0, medium_val=1)

    # Connect generator A to both B and PADE model D.
    for i, j, k in zip(a, b, d):
        # Send A output to B input.
        world.connect(i, j, 'val_out', 'val_in')
        
        # Send A output to the PADE agent input.
        # Mosaik 3 uses different arguments for asynchronous requests.
        world.connect(i, k, 'val_out', 'val_in', async_requests=True)

if __name__ == '__main__':
    print("🎬 Starting the Mosaik orchestrator...")
    world = mosaik.World(sim_config)
    create_scenario(world)
    
    # Run the simulation until time step 10,000.
    world.run(until=10000)
    print("✅ Co-simulation finished!")
