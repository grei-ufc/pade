# Changelog - script_3

## Current goal
- Demonstrate a minimal FIPA Request flow in the form `REQUEST -> AGREE -> INFORM`.
- Keep the example simple and fully observable through the CSV logs.

## Verified state in the new PADE
- The main file is `script_3_updated.py`.
- The recommended command is `pade start-runtime --port 24000 script_3_updated.py`.
- The participant receives a `REQUEST`, replies with `AGREE`, and then completes the interaction with `INFORM`.
- The equivalent legacy file is syntactically broken, so the migrated version is the valid executable reference.

## Consolidated migration changes
- The script now uses `get_shared_session_id()`.
- Agent AIDs are deterministic from the runtime base port.
- The `REQUEST` receiver now uses the participant's full name, avoiding inconsistencies in `events.csv`.
- Text, comments, and terminal messages are now in English to standardize the new material.

## Expected logs
- `messages.csv`: exactly `1 request`, `1 agree`, and `1 inform`.
- `agents.csv`: the sniffer, one participant, and one initiator.
- `events.csv`: `message_sent`, `message_received`, and `message_stored` for the three protocol steps.

## Note
- This is a one-shot conversation example. The runtime stays alive, but the application protocol finishes after the third message.
