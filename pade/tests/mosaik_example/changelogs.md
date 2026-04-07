# Changelog - mosaik_example

## Current goal
- Integrate a PADE agent with Mosaik and record co-simulation data as FIPA-ACL messages.
- Make simulator outputs visible in `messages.csv`.

## Verified state in the new PADE
- The main file is `agent_example_1_mosaik_updated.py`.
- The agent wraps Mosaik data in self-addressed `INFORM` messages using ontology `mosaik_data`.
- The payload is serialized as JSON before being sent through the PADE network.
- The logs currently stored in this folder show successive `val_out` readings with values `2001`, `4002`, `6003`, and `8004`.

## Consolidated migration changes
- The integration was adapted to the Mosaik 3.0 API.
- Data registration no longer depends on a relational database and now uses the PADE CSV telemetry pipeline.
- Payloads stored in `messages.csv` became readable and filterable by ontology.
- This example still creates its own session with `datetime.now()`, so it is not yet as tightly aligned with the integrated runtime pattern as the newer basic examples.

## Expected logs
- `sessions.csv`: sessions named `Mosaik_FIPA_Logging`.
- `messages.csv`: `inform` messages with ontology `mosaik_data` and JSON payloads.
- Each message represents one simulator data snapshot.

## Note
- The main goal here is not a conversation between different agents, but auditing simulator outputs inside PADE's ACL format.
