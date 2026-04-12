# Changelog - script_4

## Current goal
- Simulate an energy recomposition workflow using FIPA Contract Net.
- Record power proposals with readable payloads and deterministic ports.

## Verified state in the new PADE
- The main file is `script_4_updated.py`.
- The recommended command is `pade start-runtime --port 24000 script_4_updated.py`.
- The initiator sends a `CFP` to two participants, compares the power proposals, accepts the best one, and receives a final confirmation `INFORM`.
- The current flow is consistent across the terminal, `messages.csv`, and `events.csv`.

## Consolidated migration changes
- Message content was migrated from `pickle` to JSON.
- The example session now uses `get_shared_session_id()`.
- Agent AIDs are now derived from the runtime base port.
- The previous changelog in this folder was replaced because it still documented binary payloads and behavior that has already been fixed.

## Expected logs
- `messages.csv`: `2 cfp`, `2 propose`, `1 reject-proposal`, `1 accept-proposal`, and `1 inform`.
- `content` should remain readable in JSON, for example `{"type": "recomposition_order", "qty": 100.0}` and `{"value": 200.0}`.
- `agents.csv`: the sniffer, two participants, and one initiator.

## Note
- This example now follows the same technical pattern as `script_2` and `script_3`: shared session, readable logs, and stable AIDs.
