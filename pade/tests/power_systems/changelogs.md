# Changelogs

## Power Systems Example Migration

### Goal preserved

The new version keeps the same objective as the legacy PADE example:

- a requester agent periodically sends a `REQUEST`
- a power-flow agent recalculates the IEEE-13 feeder state
- the voltage at node `675` is returned in an `INFORM`

### Main migration changes

- Added a local `mygrid` package to replace the missing external dependency.
- Implemented a simplified three-phase backward/forward sweep solver tailored to the radial IEEE-13 example.
- Kept the original IEEE-13 feeder structure from the legacy example.
- Translated the remaining Portuguese strings in the example to English.
- Updated the PADE integration to log sessions and agents through the new CSV logger.
- Added a guard requiring a base port of at least `10000`.
- Replaced the binary `pickle` payload with a JSON voltage payload so `messages.csv` remains readable.

### Validation status

The example now:

- imports successfully
- executes the local power-flow calculation
- runs inside `pade start-runtime`
- exchanges `REQUEST` and `INFORM` messages correctly
- records readable voltage data in `messages.csv`
