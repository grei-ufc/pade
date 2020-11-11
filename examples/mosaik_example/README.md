# PADE/Mosaik Driver

This folder contains the files needed to run a scenario example of PADE/Mosaik integration.

The files presented are:

| **File Name**                                | **Description**                                                 |
|----------------------------------------------|-----------------------------------------------------------------|
| pade_mosaik_agent_example_1.py               | a simple PADE agent with the Mosaik driver enabled              |
| generic_python_simulator.py                  | a simple python simulator                                       |
| generic_python_simulator_mosaik_interface.py | the python simulator interface with Mosaik                      |
| mosaik_scenario_def.py                       | scenario description and initialization of Mosaik co-simulation |

## Start the co-simulation

First open a terminal window and type:

```
pade start-runtime --num 1 --port 20000 pade_mosaik_agent_example_1.py
```

After agents initialization, open another terminal session and type:

```
python mosaik_scenario_def.py
```

If the co-simulation setup is correct you will see messages like this:

<img src="https://raw.githubusercontent.com/grei-ufc/pade/master/examples/mosaik_example/screencast.png" width="800">
