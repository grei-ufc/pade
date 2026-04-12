# Changelog - agent_example_3

## Current goal
- Demonstrate the FIPA Request protocol with a clock agent and a time agent.
- Ensure that the conversation starts only after the AMS table has been propagated.

## Verified state in the new PADE
- The main file is `agent_example_3_updated.py`.
- The recommended command is `pade start-runtime --port 24000 agent_example_3_updated.py`.
- The example uses the shared runtime session.
- The `ClockAgent` waits for the AMS table through a monitor behavior before starting its `REQUEST` cycle.

## Consolidated migration changes
- The old instructions based on a separate AMS and manual startup are obsolete.
- The current flow uses the integrated PADE runtime.
- Synchronization with the AMS table was made explicit to avoid sending messages too early.
- The final behavior is cyclic: a `REQUEST` from the clock agent and an `INFORM` carrying the returned time.

## Expected logs
- `agents.csv`: the sniffer, `clock_agent`, and `time_agent`.
- `messages.csv`: alternating `request` and `inform` rows.
- `events.csv`: test start, agent startup, `request_sent`, `request_received`, `response_sent`, and `inform_received`.

## Note
- This example is intentionally periodic. The goal here is not a one-shot exchange, but a controlled repetition of the Request protocol.
