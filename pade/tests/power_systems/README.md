# Power Systems Example

This example keeps the original goal of the legacy PADE `power_systems` demo: a supervisory agent periodically requests a three-phase power-flow calculation, and a calculation agent returns the updated voltage profile for node `675`.

## What changed in the new PADE version

- The example now ships with a local `mygrid` package inside this folder.
- The bundled `mygrid` implementation is focused on the IEEE-13 topology used by this test.
- The voltage reply is now serialized as JSON so the data remains readable in `messages.csv`.
- The example uses the integrated PADE runtime and CSV logging instead of the old database-backed flow.

## Files

- `agent_example_power_system_1_updated.py`: PADE agents and request/reply logic
- `ieee_13_bus_system.py`: IEEE-13 feeder topology used by the example
- `mygrid/`: local grid models, phasor utilities and the simplified backward/forward sweep solver

## How to run

From this directory:

```bash
source ~/python-envs/pade-novo-3.12/bin/activate
cd /home/fdouglas/Documentos/FACULDADE/GREI/PADE/NOVO/pade/pade/tests/power_systems
pade start-runtime --port 20000 agent_example_power_system_1_updated.py
```

Detailed terminal mode:

```bash
pade start-runtime --detailed --port 20000 agent_example_power_system_1_updated.py
```

## Notes

- Use a base port greater than or equal to `10000`, because the requester agents are created with `base_port - 10000`.
- The example creates two calculation agents and two requester agents in the same process.
- `messages.csv` stores the `REQUEST` messages plus the JSON voltage payload returned by each `INFORM`.

## Expected output

- Terminal:
  - the requester agents periodically trigger new readings
  - the power-flow agents recalculate the feeder state
  - the updated voltage at node `675` is printed phase-by-phase
- Logs:
  - `sessions.csv`: runtime and example session
  - `agents.csv`: sniffer, power-flow agents and requester agents
  - `messages.csv`: `REQUEST` and `INFORM` entries
  - `events.csv`: message delivery lifecycle plus connection verification
