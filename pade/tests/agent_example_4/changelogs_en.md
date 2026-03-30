# Changelog - agent_example_4

## Current goal
- Demonstrate the FIPA Contract Net protocol in the new PADE.
- Compare proposals from two participants and select the best response.

## Verified state in the new PADE
- The main file is `agent_example_4_updated.py`.
- The recommended command is `pade start-runtime --port 24000 agent_example_4_updated.py`.
- The example uses the shared runtime session and full AIDs in the new format.
- The initiator sends a `CFP`, receives two proposals, rejects the lower offer, accepts the best one, and receives the final `INFORM`.

## Consolidated migration changes
- The old changelog in this folder was incorrect and has been rewritten from scratch.
- The current example is aligned with the integrated runtime flow.
- The contract flow was validated with consistent `messages.csv` and `events.csv` records.
- Best-offer selection is now documented as part of the expected behavior.

## Expected logs
- `messages.csv`: `2 cfp`, `2 propose`, `1 reject-proposal`, `1 accept-proposal`, and `1 inform`.
- `agents.csv`: the sniffer, two participants, and one initiator.
- `events.csv`: agent creation, Contract Net start, proposal reception, best-offer selection, and protocol completion.

## Note
- This example is the first fully complete negotiation flow in the repository already aligned with the CSV telemetry model of the new PADE.
