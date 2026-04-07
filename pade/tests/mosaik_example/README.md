# PADE / Mosaik Driver Integration

This folder contains the files required to run a PADE + Mosaik co-simulation example, updated for **Mosaik API 3.0+** and **Python 3.12**.

The legacy goal is preserved: Mosaik starts a scenario, connects to a PADE-driven simulation node, and exchanges values during the co-simulation. The main change in the new PADE is that simulator outputs are also wrapped as FIPA-ACL `INFORM` messages with ontology `mosaik_data`, making them visible in `messages.csv`.

## Files

| File | Description |
|------|-------------|
| `agent_example_1_mosaik_updated.py` | PADE agent with the Mosaik driver enabled, acting as the PADE-side co-simulation node. |
| `simulator.py` | Core logic of the generic Python simulator used by Mosaik. |
| `example_sim.py` | Mosaik API 3.0 wrapper around the generic Python simulator. |
| `first.py` | Mosaik scenario orchestrator that creates the world and connects the simulators. |
| `changelogs.md` | Migration notes and expected logging behaviour. |
| `changelogs_en.md` | English changelog copy for the same example. |

## What changed relative to the legacy example

- The Mosaik integration was updated from API 2.2 to API 3.0.
- The simulator wrapper now filters `None` values before summing asynchronous inputs.
- The PADE-side agent records simulator snapshots as JSON payloads in ACL messages.
- The example currently starts one PADE process instead of three agent processes by default.

These changes alter implementation details, but the example still serves the same main purpose: demonstrating PADE/Mosaik co-simulation and value exchange.

## Recommended execution flow

Before running the example, make sure the Mosaik packages are installed in the same virtual environment used by PADE:

```bash
python -m pip install mosaik mosaik-api-v3
```

The legacy `mosaik-api` package should not be used here. It is deprecated and may fail in modern Python 3.12 environments.

Open two terminal sessions.

### Terminal 1: start the PADE side

From this folder:

```bash
pade start-runtime --port 20000 agent_example_1_mosaik_updated.py
```

If you want the same execution with detailed AMS/Sniffer traces in the terminal, use:

```bash
pade start-runtime --detailed --port 20000 agent_example_1_mosaik_updated.py
```

If you prefer to launch it from the repository root, you can also run:

```bash
pade start-runtime --port 20000 pade/tests/mosaik_example/agent_example_1_mosaik_updated.py
```

Or, in detailed mode from the repository root:

```bash
pade start-runtime --detailed --port 20000 pade/tests/mosaik_example/agent_example_1_mosaik_updated.py
```

This starts the integrated runtime, including:

- AMS on port `8000`
- Sniffer on port `8001`
- the PADE-side Mosaik agent on port `20000`

### Terminal 2: start the Mosaik orchestrator

From this folder:

```bash
python first.py
```

`first.py` starts two internal `ExampleSim` instances and connects `PadeSim` to `localhost:20000`, which is why the PADE agent must already be running before the scenario starts.

## Expected behaviour

If the setup is correct:

- the PADE terminal shows the Mosaik agent starting and receiving simulator data
- the Mosaik terminal shows the scenario being built and the co-simulation running until step `10000`
- `messages.csv` stores JSON payloads such as:

```json
{"ExampleSim-0.0.0": {"val_out": 2001}}
```

- the message ontology is `mosaik_data`, which makes filtering easier in later analysis

## Logging notes

This example extends the legacy behaviour. In the old PADE version, simulator data was mainly printed to the terminal. In the new version, the same data is additionally registered in the PADE telemetry pipeline.

The most relevant files are:

- `sessions.csv`: session start records
- `messages.csv`: `inform` messages containing simulator snapshots
- `events.csv`: lower-level runtime and sending events

The logs currently stored in this folder show successive `val_out` readings of `2001`, `4002`, `6003`, and `8004`.

## Manual debugging flow

The integrated `start-runtime` command is the recommended entry point. If you need to debug services separately, you can still launch them manually in different terminals:

```bash
python -m pade.core.new_ams pade_user pade_user@pade.com 12345 8000
python -m pade.core.sniffer 8001
python agent_example_1_mosaik_updated.py 20000
```

Then run:

```bash
python first.py
```

## Current limitation

This example still creates its own session id with `datetime.now()`, so it is not yet as tightly aligned with the integrated runtime pattern as the newer basic examples.
