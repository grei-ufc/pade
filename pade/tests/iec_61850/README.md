# PADE / IEC 61850 Integration

This folder contains the IEC 61850 integration example adapted to the new PADE runtime.

The legacy objective is preserved: one PADE agent receives periodic FIPA Request messages, accesses an IEC 61850 IED server, performs a read/write cycle, and replies with an `INFORM`.

## Files

| File | Description |
|------|-------------|
| `agent_example_iec_61850_1_updated.py` | Main PADE-side IEC 61850 integration example. |
| `server_iec61850.py` | Simple IEC 61850 server used as the IED endpoint. |
| `changelogs.md` | Portuguese migration notes for this example. |
| `changelogs_en.md` | English migration notes for this example. |

## Required dependency

This example depends on the optional Python package `pyiec61850`, which is not part of the PADE core installation.

Install it in the same virtual environment used by PADE before running the example:

```bash
python -m pip install pyiec61850==1.5.2a1
```

## Recommended execution flow

Open two terminal sessions.

### Terminal 1: start the IEC 61850 server

From this folder:

```bash
python server_iec61850.py
```

The server listens on TCP port `8102`.

### Terminal 2: start the PADE side

From this folder:

```bash
pade start-runtime --port 20000 agent_example_iec_61850_1_updated.py
```

If you want the same execution with detailed AMS and Sniffer traces in the terminal, use:

```bash
pade start-runtime --detailed --port 20000 agent_example_iec_61850_1_updated.py
```

If you prefer to launch it from the repository root, you can also run:

```bash
pade start-runtime --port 20000 pade/tests/iec_61850/agent_example_iec_61850_1_updated.py
```

## Important note about the base port

This example preserves the legacy port layout, where the requesting agents are created with `port - 10000`.

Because of that, the recommended base port is `20000` or any other value greater than or equal to `10000`.

## Expected behaviour

If the setup is correct:

- the IEC 61850 server starts on port `8102`
- two `RequestAgent` instances periodically send `REQUEST` messages
- two `IEC61850Agent` instances connect to the IED server and execute the control routine
- the requesting agents receive `INFORM` replies with the execution status

## Expected logs

When the Sniffer is active, the most relevant files are:

- `sessions.csv`: root runtime session plus the `IEC61850_Integration` session
- `agents.csv`: two IEC 61850 agents, two requesting agents, and the sniffer
- `messages.csv`: repeated `request` and `inform` messages using the FIPA Request protocol
- `events.csv`: runtime, delivery, and message storage events

## Relation to the legacy example

Compared with the legacy PADE example:

- the core interaction pattern remains the same
- the IEC 61850 import was updated from `iec61850` to `pyiec61850`
- the example now aligns its session with the integrated runtime through `get_shared_session_id()`
- the recommended execution flow uses the integrated `pade start-runtime` command
