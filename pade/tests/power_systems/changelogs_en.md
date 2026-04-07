# Changelogs

## Power Systems Example Migration

### Preserved objective

The new version preserves the same purpose as the legacy PADE example:

- a requester agent periodically sends a `REQUEST`
- a power-flow agent recomputes the IEEE-13 feeder state
- the voltage at node `675` is returned through an `INFORM`

### Main migration updates

- Added a local `mygrid` package to replace the missing external dependency.
- Implemented a simplified three-phase backward/forward sweep solver tailored to the radial IEEE-13 topology used by this example.
- Preserved the original IEEE-13 feeder structure from the legacy version.
- Translated the remaining Portuguese strings in the example to English.
- Integrated the example with the CSV-based session and agent logging flow used by the new PADE runtime.
- Added a guard requiring a base port of at least `10000`.
- Replaced the binary `pickle` payload with a JSON voltage payload so `messages.csv` remains human-readable.

### Validation status

The example now:

- imports correctly
- executes the local power-flow calculation
- runs inside `pade start-runtime`
- exchanges `REQUEST` and `INFORM` messages correctly
- records readable voltage data in `messages.csv`
