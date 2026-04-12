# Changelog - script_2

## Current goal
- Demonstrate a FIPA Contract Net negotiation between one consumer and three bookstores.
- Ensure that the logs remain readable and use deterministic ports.

## Verified state in the new PADE
- The main file is `script_2_updated.py`.
- The recommended command is `pade start-runtime --port 24000 script_2_updated.py`.
- The consumer sends a `CFP`, receives three proposals, selects the best offer, rejects the others, and finishes the purchase with an `INFORM`.
- The equivalent legacy file is syntactically broken, so this migrated version is the executable reference for the example.

## Consolidated migration changes
- The negotiation payload was migrated from `pickle` to JSON to avoid hexadecimal content in `messages.csv`.
- The script now uses `get_shared_session_id()` to align the example session with the runtime session.
- Agent AIDs are deterministic from the runtime base port.
- Terminal behavior and CSV logs now describe the same negotiation.

## Expected logs
- `messages.csv`: `3 cfp`, `3 propose`, `1 accept-proposal`, `2 reject-proposal`, and `1 inform`.
- `agents.csv`: the sniffer, `Saraiva`, `Cultura`, `Nobel`, and `Consumer`.
- Message content should appear as readable JSON, not as serialized bytes.

## Note
- This example already matches the recommended new-PADE pattern: integrated runtime, shared session, stable ports, and audit-friendly textual payloads.
