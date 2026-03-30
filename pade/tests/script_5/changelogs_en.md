# Changelog - script_5

## Current goal
- Demonstrate the smallest possible ACL exchange between two agents.
- Clearly separate application messages from internal infrastructure messages.

## Verified state in the new PADE
- The main file is `script_5_updated.py`.
- The recommended command is `pade start-runtime --port 24000 script_5_updated.py`.
- Bob sends a single `INFORM` to Alice with the content `Hello Alice!`.
- The runtime may stay open showing connection checks, but that does not mean the application conversation is repeating.

## Consolidated migration changes
- The script now uses `get_shared_session_id()` and deterministic AIDs.
- The terminal output was filtered to ignore `Agent successfully identified.`, `CONNECTION`, and AMS table messages.
- The current behavior is aligned with the historical purpose of the example: one single ACL greeting.
- The previous changelog was corrected to make it clear that having only one line in `messages.csv` is expected.

## Expected logs
- `messages.csv`: exactly `1 inform`, with content `Hello Alice!`.
- `agents.csv`: the sniffer, Alice, and Bob.
- `events.csv`: one application exchange, plus runtime infrastructure events.

## Note
- The `CONNECTION` messages seen in the terminal do not appear in `messages.csv` because they are not part of the application's ACL conversation.
