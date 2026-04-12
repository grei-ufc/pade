# Changelog - agent_example_5

## Current goal
- Demonstrate the FIPA Subscribe protocol with one publisher and two subscribers.
- Validate the intentional delay before subscription and the continuous publication flow.

## Verified state in the new PADE
- The main file is `agent_example_5_updated.py`.
- The recommended command is `pade start-runtime --port 24000 agent_example_5_updated.py`.
- The example uses the shared runtime session.
- Subscribers wait a few seconds before sending `SUBSCRIBE`, so the first publications may happen with no active subscribers yet.

## Consolidated migration changes
- The old changelog accumulated history from other examples and outdated information.
- The current example correctly records `subscribe`, `agree`, and `inform` in CSV.
- The expected behavior is now described from the real script flow.
- The documentation was corrected to make it clear that `messages.csv` is not empty in this example.

## Expected logs
- `messages.csv`: `2 subscribe`, `2 agree`, and multiple `inform` messages.
- `agents.csv`: the sniffer, one publisher, and two subscribers.
- `events.csv`: test start, initial publications with zero subscribers, subscription requests, accepted subscriptions, and continuous publication reception.

## Note
- Seeing some publications before `SUBSCRIBE` is accepted is normal here, because that delay is part of the didactic design of the example.
