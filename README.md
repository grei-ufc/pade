# Python Agent DEvelopment framework (PADE)

[![](https://img.shields.io/pypi/v/pade.svg)](https://pypi.python.org/pypi/pade/)
[![](https://img.shields.io/pypi/pyversions/pade.svg)](https://pypi.python.org/pypi/pade/)
[![](https://img.shields.io/readthedocs/pade.svg)](https://pade.readthedocs.io/en/latest/)
[![](https://img.shields.io/github/issues/grei-ufc/pade.svg)](https://github.com/grei-ufc/pade/issues)
[![](https://img.shields.io/github/issues-pr/grei-ufc/pade.svg)](https://github.com/grei-ufc/pade/pulls)
[![](https://img.shields.io/pypi/l/pade.svg)](https://opensource.org/licenses/MIT)

<br>

<p align="center">
    <img src="https://raw.githubusercontent.com/lucassm/Pade/master/pade/images/pade_logo.png" alt="PADE" width="200">
</p>

PADE is a framework for developing, executing, and managing multi-agent systems in distributed computing environments. PADE code is 100% Python and has its core in Twisted, a Python package for implementing distributed applications.

PADE is free software licensed under the MIT license. It was originally developed at the **Federal University of Ceará (Brazil) by the Intelligent Electrical Grids Group (GREI) in the Electrical Engineering Department (DEE)**.

The researchers at the **Laboratory of Applied Artificial Intelligence (LAAI) of the Federal University of Pará (UFPA)** have contributed significantly to the PADE project. We register here our acknowledgments.

Everyone interested in developing PADE is welcome to download, install, test, use, and send us feedback.

## Scientific Paper

There is a scientific paper presenting PADE as a scientific tool for multi-agent system simulation, with a focus on electric power systems simulation. If you are interested, here is the link to access it:

[Python‐based multi‐agent platform for application on power grids](https://doi.org/10.1002/2050-7038.12012)

If you use PADE in your research work, please cite PADE as:

>Melo, LS, Sampaio, RF, Leão, RPS, Barroso, GC, Bezerra, JR. Python‐based multi‐agent platform for application on power grids. Int Trans Electr Energ Syst. 2019; 29:e12012. https://doi.org/10.1002/2050-7038.12012


## Documentation

PADE is well documented. You can access the documentation here: [PADE documentation](https://pade.readthedocs.io/en/latest/)

## Dependencies

PADE is currently maintained for [Python 3.12+**](https://www.python.org/) and has a [Twisted](https://twistedmatrix.com/trac/) core.

## Install

#### Via Python Package Index (PyPI):
```bash
$ pip install pade
```

#### Via Github (Latest Version):
```bash
$ git clone https://github.com/grei-ufc/pade.git
$ cd pade
$ uv sync
$ uv run pade version
```

For the current installation workflow, prefer the repository documentation in `docs/user/instalacao.rst`, which reflects the Python 3.12 codebase.

## Docker

Build container:
```bash
$ docker-compose up -d
```

List containers:
```bash
$ docker ps

CONTAINER ID        IMAGE
8d7cb00972c9        pade_pade
```

Get inside container:
```bash
$ docker exec -it <CONTAINER_ID> bash
```


## Example: Hello World in PADE

The new PADE now ships two Hello World levels in the same folder:

* `pade/tests/hello_world/hello_world_minimal.py`: the shortest version, focused on terminal output;
* `pade/tests/hello_world/hello_world.py`: a slightly richer version that also produces real ACL traffic for `messages.csv`.

If you only want the simplest possible first contact, start with the minimal version:

```python
from sys import argv

from pade.acl.aid import AID
from pade.core.agent import Agent
from pade.misc.utility import display_message, start_loop


class HelloWorldAgent(Agent):
    def __init__(self, aid):
        super().__init__(aid=aid, debug=False)

    def on_start(self):
        super().on_start()
        display_message(self.aid.localname, 'Hello World!')

if __name__ == '__main__':
    ams_config = {'name': 'localhost', 'port': 8000}
    base_port = int(argv[1]) if len(argv) > 1 else 20000

    agent = HelloWorldAgent(
        AID(name=f'hello_agent_{base_port}@localhost:{base_port}')
    )
    agent.update_ams(ams_config)

    start_loop([agent])
```

This version is intentionally small: it only prints to the terminal. If you run it through `pade start-runtime`, the runtime still creates `sessions.csv`, `agents.csv`, and `events.csv`, but `messages.csv` stays empty because no ACL message is exchanged.

If you also want to demonstrate real message logging, use the companion script `pade/tests/hello_world/hello_world.py`. That version starts a receiver and a sender in the same process, and the sender emits one `INFORM` message a few seconds after startup. This is the recommended Hello World when you want to validate the Sniffer and `messages.csv`.

## Changes in the New Version (Python 3.12.11)

The latest version of PADE introduces major structural changes to modernize the framework, improve performance, and remove obsolete dependencies.

### 1. New CSV Logging System (No more SQLite)
In previous versions, PADE required the initialization of an SQLite database (`pade create-pade-db`) before running any simulation. This dependency has been **entirely removed**.

PADE now features a lightweight, high-performance **CSV Logging System**. When you run an agent session, PADE automatically creates a `logs/` directory in your current workspace and generates the following structured files:
* `sessions.csv`: Records the start and end of your simulation sessions.
* `agents.csv`: Registers all agents initialized in the environment.
* `messages.csv`: Logs all FIPA-ACL messages exchanged between agents (if the Sniffer is active).
* `events.csv`: Tracks system and agent-level events.

This new approach ensures data persistence without external database services and allows for easy data analysis using standard tools like Pandas or Excel.

### 2. Integrated Execution with `start-runtime`
PADE 2.2.6 keeps the modernized AMS and Sniffer as independent services internally, but the recommended user experience is integrated again through `pade start-runtime`. This preserves the original workflow of the legacy PADE while maintaining the lightweight CSV-based architecture.

Here it is important to explain how `start-runtime` executes the agent scripts.

The adapted examples and tests shipped with the new PADE are located in:

```bash
pade/tests/
```

For example, the bundled Hello World scripts are:

```bash
pade/tests/hello_world/hello_world_minimal.py
pade/tests/hello_world/hello_world.py
```

Use `hello_world_minimal.py` when you want the shortest possible terminal-only example. Use `hello_world.py` when you want the same folder to also demonstrate real ACL traffic and `messages.csv`.

The logging-oriented `hello_world.py` creates two agents per launched process:

* a receiver bound to the base port;
* a sender bound to `base_port + 1000`.

The sender emits one real `INFORM` message to the receiver a few seconds after startup. That keeps the example small while ensuring that `messages.csv` is populated when the Sniffer is active.

So, if you are in the repository root, you can execute it directly by passing its relative path:

```bash
$ pade start-runtime --port 20000 pade/tests/hello_world/hello_world_minimal.py
```

If you copy that same file to your current working directory, or if you create your own script in the current directory, you may execute it with the simple form used in the legacy README:

```bash
$ pade start-runtime hello_world_minimal.py
```

The same rule applies to any other PADE script: use only the filename when the file is in your current directory, or pass a relative or absolute path when it is stored elsewhere.

If you want the bundled Hello World that also fills `messages.csv`, execute:

```bash
$ pade start-runtime --port 20000 pade/tests/hello_world/hello_world.py
```

If you want to launch this same script 3 times, then you can type:

```bash
$ pade start-runtime --num 3 hello_world_minimal.py
```

With the minimal Hello World, that means 3 independent processes and 3 agents in total, because each process creates exactly 1 agent.

If you want to launch the 3 processes with base ports `20000`, `20001`, and `20002`, then you can type:

```bash
$ pade start-runtime --num 3 --port 20000 hello_world_minimal.py
```

When you use `--num 3` and `--port 20000`, the PADE command line tool executes the content of `hello_world_minimal.py` 3 times in 3 independent processes. Each process receives one positional argument in `sys.argv[1]`, and this value is incremented by one at every launch. In this case, the script receives `20000`, `20001`, and `20002`.

This argument should normally be accessed in the code through `sys.argv[1]`, for example:

```python
base_port = int(sys.argv[1]) if len(sys.argv) > 1 else 20000
```

So you can execute as many agents as you want per process. If your script contains a loop controlled by a variable such as `agents_per_process`, then the total number of agents will be:

```text
total_agents = num * agents_per_process
```

For example, if `--num` is `3` and the script itself creates `3` agents per process with a spacing of `1000`, PADE will start 9 agents overall. A possible distribution would be:

* process `20000`: agents on `20000`, `21000`, `22000`
* process `20001`: agents on `20001`, `21001`, `22001`
* process `20002`: agents on `20002`, `21002`, `22002`

The command line also supports more than one agent file. For example:

```bash
$ pade start-runtime --num 3 --port 20000 hello_world_1.py hello_world_2.py
```

In the current PADE CLI, the port is incremented after every launched process. Therefore:

* `hello_world_1.py` receives `20000`, `20001`, and `20002`
* `hello_world_2.py` receives `20003`, `20004`, and `20005`

If you are already inside the example directory, you may also use only the filename:

```bash
$ cd pade/tests/hello_world
$ pade start-runtime --port 20000 hello_world_minimal.py
```

In this specific minimal example, the first process started with `--port 20000` creates:

* `hello_agent_20000@localhost:20000`

If you switch to the logging-oriented variant instead:

```bash
$ cd pade/tests/hello_world
$ pade start-runtime --port 20000 hello_world.py
```

the first process creates:

* `hello_receiver_20000@localhost:20000`
* `hello_sender_21000@localhost:21000`

There is another way to launch PADE agents: with a configuration file in JSON format. A valid example for the new PADE is:

```json
{
  "agent_files": [
    "pade/tests/agent_example_1/agent_example_1_updated.py",
    "pade/tests/agent_example_3/agent_example_3_updated.py"
  ],
  "port": 20000,
  "num": 2,
  "pade_ams": {
    "launch": true,
    "host": "localhost",
    "port": 8000
  },
  "pade_sniffer": {
    "active": true,
    "host": "localhost",
    "port": 8001
  },
  "session": {
    "username": "pade_user",
    "email": "pade_user@pade.com",
    "password": "12345"
  }
}
```

To launch it, type:

```bash
$ pade start-runtime --config_file pade_config.json
```

The old `pade_web` block should not be used anymore, because the embedded Flask interface was removed from the new PADE architecture.

If you need to execute simulations with a high number of agents that send and receive messages, such as hundreds of agents exchanging messages at high frequency, it may be useful to disable the Sniffer:

```bash
$ pade start-runtime --num 3 --port 20000 --no_pade_sniffer hello_world_1.py hello_world_2.py
```

Even though the new PADE no longer uses SQLite, the Sniffer still intercepts traffic and writes telemetry to disk, which can add overhead in very large runs.

If you want to keep the integrated workflow but temporarily restore the detailed AMS/Sniffer traces in the terminal, use ``--detailed``:

```bash
$ pade start-runtime --detailed --port 20000 pade/tests/mosaik_example/agent_example_1_mosaik_updated.py
```

This mode is useful for infrastructure debugging and keeps the same CSV logging behaviour. The detailed mode is also available through the dedicated alias:

```bash
$ pade start-runtime-detailed --port 20000 pade/tests/mosaik_example/agent_example_1_mosaik_updated.py
```

This command orchestrates:
* the AMS on port `8000`;
* the Sniffer on port `8001` when enabled;
* the agent script or scripts informed on the command line.

**Advanced workflow**
If you need to debug a specific component in isolation, you can still run the services manually:
```bash
$ python -m pade.core.new_ams test test@test.com 123 8000
$ python -m pade.core.sniffer 8001
$ python pade/tests/hello_world/hello_world_minimal.py 20000
```

If you also want to validate the Sniffer and `messages.csv`, switch only the script:

```bash
$ python pade/tests/hello_world/hello_world.py 20000
```
This mode remains useful for low-level troubleshooting and performance analysis.

### 3. Co-Simulation with Mosaik API 3.0+
The `mosaik_driver` module has been completely refactored to support the modern **Mosaik API 3.0** and the strict bytes I/O rules of Python 3.12. PADE agents can now perform seamless asynchronous data fetching (`get_data_async`) and progress tracking during complex power system co-simulations without deadlocks. Check the `tests/mosaik_example` directory for a complete integration example.

### 4. Power Systems Example (IEEE-13)
The `tests/power_systems` directory now ships a local `mygrid` implementation tailored to the migrated IEEE-13 feeder example. The scenario preserves the legacy objective: supervisory agents periodically request a new power-flow calculation, and calculation agents respond with the updated three-phase voltage profile of node `675`. The returned voltage payload is now logged as readable JSON in `messages.csv`.

### CLI Tools Updated
Commands like `pade create-pade-db`, `pade drop-pade-db`, and `pade start-web-interface` have been removed. The current CLI keeps the integrated `start-runtime` workflow and adds CSV-oriented inspection tools:

* To view a summary of the current logs:
  ```bash
  $ pade show-logs
  ```
* To export the logs to `logs/exports/` in JSON, CSV, or TXT format:
  ```bash
  $ pade export-logs csv
  ```
