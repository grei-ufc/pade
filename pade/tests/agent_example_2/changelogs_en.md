# Changelog - agent_example_2

## Current goal
- Demonstrate timed behavior in the new PADE.
- Keep a simple canonical example and an optional variant that produces ACL traffic for log inspection.

## Verified state in the new PADE
- The main example is `agent_example_2_updated.py`.
- The didactic variant is `agent_example_2_with_messages.py`.
- The recommended command remains `pade start-runtime --port 24000 <file>.py`.
- The main example prints periodic timed activity but does not need to generate application ACL traffic.

## Consolidated migration changes
- The main example was kept faithful to its original purpose: timing and terminal output.
- The message-enabled variant was added to make `messages.csv` and `events.csv` easier to study.
- The current logs in this folder come from the message-enabled variant, not from the pure canonical example.
- The variant emits a periodic `INFORM` every third timer tick.

## Expected logs
- `agent_example_2_updated.py`: `messages.csv` may stay empty, or only show infrastructure traces outside the application conversation.
- `agent_example_2_with_messages.py`: `messages.csv` stores `inform` rows with content like `Timed hello #<n>`.
- `events.csv`: in both cases it should record test startup and timed-agent activity.

## Note
- This folder intentionally contains two complementary goals: one example faithful to the legacy intent and one variant focused on ACL telemetry.
