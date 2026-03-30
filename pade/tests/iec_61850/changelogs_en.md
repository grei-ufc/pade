# Changelog - iec_61850

## Current goal
- Demonstrate an integration between PADE agents and an IEC 61850 IED.
- Trigger periodic control requests and record the response using the FIPA Request pattern.

## Verified state in the new PADE
- The main file is `agent_example_iec_61850_1_updated.py`.
- Two `RequestAgent` instances send periodic `REQUEST` messages to two `IEC61850Agent` instances.
- Each IEC 61850 agent attempts to execute the read/write routine on the IED and replies with an `INFORM`.
- The current logs in this folder show the `request -> inform` cycle repeating roughly every 10 seconds.

## Consolidated migration changes
- The integration was ported to Python 3.12 with the `pyiec61850` library.
- CSV logging replaced the legacy relational database storage.
- The example documents that the response may appear as `[Dados binarios codificados como string]` when the original data is not textual.
- This script still creates its own session with `datetime.now()` and is not yet fully aligned with the more recent `get_shared_session_id()` pattern.

## Expected logs
- `sessions.csv`: a session named `IEC61850_Integration`.
- `messages.csv`: repeated `request` and `inform` rows using the `fipa-request protocol`.
- `agents.csv`: two IEC 61850 agents, two requesting agents, and the sniffer when the execution is complete.

## Note
- This example depends on an available IEC 61850 environment. The migration work here focused on flow compatibility and auditability, not on removing that external dependency.
