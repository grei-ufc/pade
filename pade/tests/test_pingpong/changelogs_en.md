# Changelog - test_pingpong

## Current goal
- Demonstrate a simple `PING` and `PONG` conversation in the new PADE.
- Support both integrated `start-runtime` execution and manual two-terminal execution.

## Verified state in the new PADE
- The main file is `test_pingpong.py`.
- Integrated mode works with `pade start-runtime --port 24000 test_pingpong.py`.
- Manual mode remains available through:
  - `python test_pingpong.py pong 37001`
  - `python test_pingpong.py ping 37000 37001`
- In integrated mode, the runtime creates `pong_24000@localhost:24000` and `ping_24001@localhost:24001`.

## Consolidated migration changes
- The script was adapted to accept the new PADE integrated mode, which passes only the base port as an argument.
- The integrated path now uses `get_shared_session_id()`.
- Both agents run with `debug=False`.
- The first `PING` is sent after 5 seconds and the next ones are scheduled every 30 seconds.

## Expected logs
- `agents.csv`: the sniffer, `pong_24000`, and `ping_24001` in integrated mode with base port 24000.
- `messages.csv`: at least one `PING` and one `PONG` sharing the same `conversation_id`, for example `ping_conversation_1`.
- `events.csv`: `message_sent`, `message_received`, `message_stored`, plus runtime connection verification events.

## Note
- If the run is stopped right after the first exchange, `messages.csv` will show only one `PING`/`PONG` pair, which is expected.
