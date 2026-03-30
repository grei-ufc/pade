#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import mosaik

# Configuração de ponte: O Mosaik vai rodar o 'example_sim' como processo interno 
# e vai se conectar via TCP no PADE que estará escutando na 20000
sim_config = {
    'ExampleSim': {'python': 'example_sim:ExampleSim'},
    'PadeSim': {'connect': 'localhost:20000'}
}

def create_scenario(world):
    print("🌍 Construindo o cenário de Co-simulação...")
    
    # Inicia os simuladores
    exsim1 = world.start('ExampleSim')
    exsim2 = world.start('ExampleSim')
    exsim3 = world.start('PadeSim')

    # Cria entidades (Modelos)
    a = [exsim1.A(init_val=0) for i in range(3)]
    b = exsim2.B.create(2, init_val=0)
    d = exsim3.D.create(2, init_val=0, medium_val=1)

    # Conecta o Gerador de números A -> PADE D e B
    for i, j, k in zip(a, b, d):
        # Envia a saída de A para a entrada de B
        world.connect(i, j, 'val_out', 'val_in')
        
        # Envia a saída de A para a entrada do Agente PADE
        # O Mosaik 3 usa argumentos diferentes para requisições assíncronas
        world.connect(i, k, 'val_out', 'val_in', async_requests=True)

if __name__ == '__main__':
    print("🎬 Iniciando orquestrador Mosaik...")
    world = mosaik.World(sim_config)
    create_scenario(world)
    
    # Roda a simulação até o tempo (step) 10.000
    world.run(until=10000)
    print("✅ Co-simulação finalizada!")