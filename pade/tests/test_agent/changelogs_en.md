# Changelog - test_agent

## Current goal
- Validate a simple exchange between two test agents.
- Stay as close as possible to the intent of the legacy example without introducing unintended repetition.

## Verified state in the new PADE
- The main file is `test_agent_updated.py`.
- The recommended command is `pade start-runtime --port 24000 test_agent_updated.py`.
- The initiator sends a single `Hello Agent!` message after a short delay.
- The participant replies exactly once with `Hello to you too, Agent!`.
- The runtime stays alive afterwards, but the ACL conversation itself does not loop.

## Consolidated migration changes
- The recurring `TimedBehaviour` send was removed because it did not match the intended behavior of the legacy example.
- The script now uses `call_later(3.0, ...)` for a one-shot trigger.
- The session now uses `get_shared_session_id()` and deterministic AIDs.
- The terminal now ignores noisy infrastructure messages so the application exchange remains visible.

## Expected logs
- `messages.csv`: exactly `2 inform` rows, one outbound greeting and one reply.
- `agents.csv`: the sniffer, the initiator, and the participant.
- `events.csv`: a single `message_sent -> message_received -> message_stored` exchange for each side of the conversation.

## Note
- The runtime does not need to terminate automatically. What matters here is that the application protocol happens once, as intended in the legacy design.
