# PADE / Mosaik Driver Integration

This folder contains the files needed to run a scenario example of PADE and Mosaik Co-Simulation integration, fully updated to support **Mosaik API 3.0+** and **Python 3.12** (GREI/UFC).

The files presented are:

| **File Name** | **Description** |
|----------------------------------------|---------------------------------------------------------------------------------|
| `agent_example_1_mosaik_updated.py`    | A PADE agent equipped with the Mosaik driver to act as a co-simulation node.    |
| `simulator.py`                         | The core logic of a generic Python simulator.                                   |
| `example_sim.py`                       | The Python simulator interface wrapper (compliant with Mosaik API 3.0 metadata).|
| `first.py`                             | The Mosaik scenario orchestrator (builds the world and connects simulators).    |

## 🚀 How to start the co-simulation

To prevent TCP port conflicts and ensure proper FIPA-ACL tracking, the services must be started in separate terminal sessions.

**Step 1: Start the PADE core services**
Open two terminal windows and run the AMS and the Sniffer:
```bash
# Terminal 1 (AMS)
python -m pade.core.new_ams localhost 8000

# Terminal 2 (Sniffer - Optional but recommended)
python -m pade.core.sniffer 8001