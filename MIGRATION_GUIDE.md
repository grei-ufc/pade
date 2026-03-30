# PADE migration guide for the Python 3.12 codebase

This document summarizes what was actually verified in the current `NOVO/pade` codebase during the migration to Python 3.12. The goal is not to preserve every historical implementation detail, but to describe how the architecture works today, which patterns are now standard across the examples, and which specialized cases still keep a few differences.

## Scope

- Analysed codebase: `NOVO/pade`
- Package version observed in `setup.py`: `2.2.6`
- Recommended execution flow: `pade start-runtime --port <port> <file.py>`
- Telemetry persistence: CSV (`sessions.csv`, `agents.csv`, `messages.csv`, `events.csv`)

## Executive summary

- The main PADE workflow no longer depends on Flask or SQLite.
- The day-to-day command is `pade start-runtime`, which orchestrates AMS, Sniffer, and the agent scripts.
- The runtime creates a shared session through the `PADE_SESSION_ID` environment variable.
- The most recent examples were migrated to use `get_shared_session_id()` and full AIDs such as `agent@localhost:port`.
- `messages.csv` is written by the Sniffer, not by `agent.py`.
- `agent.py` records events such as `message_sent` and `message_received` in `events.csv`.

## Important corrections relative to earlier versions of this guide

- `messages.csv` is not written directly inside `react()` or `send()` in `pade/core/agent.py`. The canonical writer of `messages.csv` is `pade/core/sniffer.py`.
- The current CLI command is `start-runtime`, with a hyphen. The underscore form does not match the user-facing command name.
- The standard workflow is now the integrated runtime. Manual AMS-first startup flows only remain in specific or historical scenarios.
- `messages.csv` and `events.csv` do not include a `session_id` column. Run correlation depends on log cleanup, timestamps, or joint reading with `sessions.csv` and `agents.csv`.

## File-by-file changes that were confirmed

## `setup.py`

- The package version is `2.2.6`.
- `package_data` includes only `*.png`.
- Observed dependencies include `twisted>=22.10.0`, `requests>=2.31.0`, `click>=8.1.0`, `terminaltables>=3.1.0`, `pandas>=2.0.0`, `matplotlib>=3.7.0`, and `numpy>=1.24.0`.
- Python classifiers cover `3.7` through `3.12`.

Practical reading:
- The current package is centered on a lightweight runtime and CSV telemetry.
- The legacy web stack is no longer part of the default installation and usage path.

## `pade/cli/pade_cmd.py`

- The main command is `pade start-runtime`.
- The CLI calls `init_data_logger(config)` before launching the processes.
- `init_data_logger(config)` creates the initial `Session_<id>` record, logs `runtime_started` into `events.csv`, and exports `PADE_SESSION_ID`.
- The CLI starts AMS and Sniffer as subprocesses and then launches the agent scripts, passing the base port as an argument.
- Current utility commands: `show-logs`, `export-logs`, and `version`.

Practical reading:
- `start-runtime` is the modern equivalent of the integrated workflow users expected from the legacy PADE.
- The internal architecture remains decoupled, but the user experience is centralized again.

## `pade/misc/data_logger.py`

- The module defines `get_shared_session_id(default=None)`.
- If `PADE_SESSION_ID` exists, it becomes the dominant runtime session id.
- Four CSV files are maintained:
  - `sessions.csv`
  - `agents.csv`
  - `messages.csv`
  - `events.csv`
- `agents.csv` uses an upsert keyed by `(agent_id, session_id)`, which prevents duplicate rows for the same agent in the same run.
- `messages.csv` stores ACL metadata and the `content` converted to string form.
- `events.csv` stores general runtime and example events.

Practical reading:
- To align an example with the integrated runtime, the recommended pattern is to call `get_shared_session_id()` when the example logs its session.

## `pade/core/new_ams.py`

- The current AMS uses the shared runtime session.
- The AMS itself records `AMS_Session_<id>` in `sessions.csv`.
- The AMS records agents into `agents.csv`.
- Agent table propagation remains an essential part of the platform behavior.
- The current flow does not initialize a relational database or start a web interface.

Practical reading:
- The AMS is now primarily a routing and coordination service, not a component coupled to SQLite or Flask.

## `pade/core/agent.py`

- The file records send and receive events in `events.csv`.
- The current code emits events such as `message_sent` and `message_received`.
- The file does not write `messages.csv` directly.
- Using full AIDs helps keep routing and logs stable.

Practical reading:
- When `events.csv` looks correct but `messages.csv` looks odd, the first place to inspect is the Sniffer and the message payload, not the `Agent` logger path.

## `pade/core/sniffer.py`

- This is the canonical writer of `messages.csv`.
- The Sniffer intercepts messages, buffers them by sender, and writes the result to CSV.
- The `receivers` field is canonicalized into a stable string representation.
- The Sniffer also records `message_stored` in `events.csv`.

Practical reading:
- When the application payload is text or JSON, `messages.csv` tends to stay readable.
- When the application payload is binary or `pickle`-serialized, the CSV may still show opaque string representations. That is why the migrated examples now prefer JSON whenever log readability matters.

## `pade/behaviours/protocols.py`

- `TimedBehaviour` is recurring by design in the new PADE.
- Its `on_time()` method reschedules itself with `reactor.callLater(self.time, self.on_time)`.

Practical reading:
- If the goal is to execute something only once after a delay, the recommended pattern is `call_later(...)`.
- If the goal is a periodic behavior, `TimedBehaviour` is still the correct tool.

This point was especially important to fix:
- `test_agent`, which should not loop
- periodic examples such as `agent_example_2`, `agent_example_3`, and `iec_61850`, which should keep looping

## `pade/misc/common.py`

- `PadeSession` still exists as a compatibility layer.
- It logs sessions and events through the CSV logger.
- Even so, the main user-facing path remains the integrated CLI, not manual session assembly.

Practical reading:
- `PadeSession` can still be useful in specific scenarios, but it is not the execution style that the main documentation should promote.

## `pade/drivers/mosaik_driver.py`

- Current driver usage was indirectly confirmed through the `mosaik_example`.
- The migrated example declares Mosaik API `3.0` metadata and emits JSON payloads into ACL telemetry.

Practical reading:
- The Mosaik case is more specialized than the basic protocol examples.
- The most important validation in this review round was that simulator outputs can be reflected into `messages.csv` as readable ACL messages.

## Migration patterns that proved correct in the examples

The most stable examples in the new PADE converged on the same practices:

- Run with `pade start-runtime --port ...`
- Use `get_shared_session_id()` inside the example
- Build full AIDs, for example `agent@localhost:24000`
- Use JSON when human-readable `messages.csv` matters
- Filter system messages in `react()` when the example is primarily educational
- Use `call_later(...)` instead of `TimedBehaviour` for one-shot sends

## Current state of the migrated examples

Examples already aligned with the new standard:

- `agent_example_1`
- `agent_example_2`
- `agent_example_3`
- `agent_example_4`
- `agent_example_5`
- `agent_example_6`
- `script_2`
- `script_3`
- `script_4`
- `script_5`
- `test_agent`
- `test_pingpong`

More specialized cases with some residual style differences:

- `mosaik_example`
- `iec_61850`

In those two cases, the code still creates a local session with `datetime.now()` instead of fully following the `get_shared_session_id()` pattern used by the newer basic examples.

## Limits and precautions when interpreting the logs

- The `logs/` directory accumulates runs unless it is cleaned manually.
- `messages.csv` may be written a few seconds after the terminal output appears, because the Sniffer buffers messages before persisting them.
- `CONNECTION`, `Agent successfully identified.`, and AMS table messages may appear in the terminal, but they do not always belong to the main ACL conversation of the example.
- For clean comparisons between runs, the safest workflow is to clear or archive `logs/` before executing the example again.

## Conclusion

The Python 3.12 migration produced a PADE that is lighter, more auditable, and more predictable for educational examples. The core of the new architecture is:

- integrated CLI from the user's perspective
- internally decoupled AMS and Sniffer
- CSV telemetry as the observability layer
- shared runtime session as the main run correlation anchor

Whenever a new example is migrated, the safest path is to repeat the pattern that already proved robust in the updated examples:

1. `pade start-runtime --port ...`
2. `get_shared_session_id()`
3. full AIDs
4. readable payloads
5. validation across `sessions.csv`, `agents.csv`, `messages.csv`, and `events.csv`
