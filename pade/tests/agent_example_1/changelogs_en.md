# Changelog - agent_example_1

## Current goal
- Demonstrate basic ring communication among three agents.
- Keep terminal-only text separate from the actual ACL payload exchanged over the network.

## Verified state in the new PADE
- The main file is `agent_example_1_updated.py`.
- The recommended command is `pade start-runtime --port 24000 agent_example_1_updated.py`.
- The example uses the shared runtime session so `sessions.csv`, `agents.csv`, `messages.csv`, and `events.csv` stay aligned.
- The current behavior is a three-agent ring that exchanges `INFORM` messages in sequence.

## Consolidated migration changes
- The old manual startup flow was replaced by the integrated runtime.
- `Hello World! (Apenas Terminal)` was kept as local console output.
- Network traffic now uses its own payload, `Hello World Message! (Via Rede)`, with ontology `hello_ontology`.
- Logging now records the real application traffic without relying on a relational database.

## Expected logs
- `agents.csv`: the sniffer plus the three example agents.
- `messages.csv`: three `inform` messages.
- `events.csv`: test start, agent startup, and the `message_sent -> message_received -> message_stored` chain.

## Note
- The `content` stored in `messages.csv` is the ACL payload sent through the network, not the string printed only to the terminal.
