# Changelog - agent_example_6

## Current goal
- Extend the Subscribe example to two publishers and four subscribers.
- Keep the `call_in_thread()` behavior aligned with the legacy version.

## Verified state in the new PADE
- The main file is `agent_example_6_updated.py`.
- The recommended command is `pade start-runtime --port 24000 agent_example_6_updated.py`.
- The example uses the shared runtime session.
- The terminal shows two `I will sleep now! a` lines and two `I wake up now! b` lines, matching the legacy behavior.

## Consolidated migration changes
- The old changelog in this folder accumulated history from previous examples and no longer matched the real code.
- Each subscriber now creates its own `SUBSCRIBE` message, fixing the old bug where only half of the subscriptions became active.
- `call_in_thread(my_time, 'a', 'b')` remains non-blocking.
- The current flow correctly records two independent publish/subscribe networks.

## Expected logs
- `messages.csv`: `4 subscribe`, `4 agree`, and many `inform` messages.
- `agents.csv`: the sniffer, two publishers, and four subscribers.
- `events.csv`: test start, execution of the two threads, subscription reception, accepted subscriptions, and publications delivered to the correct subscriber pairs.

## Note
- This example is a direct extension of `agent_example_5`, but with two publisher/subscriber topologies running in parallel.
