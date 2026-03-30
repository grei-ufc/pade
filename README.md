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

PADE is currently maintained for **Python 3.12+** and has a [Twisted](https://twistedmatrix.com/trac/) core.

## Install

#### Via Python Package Index (PyPI):
```bash
$ pip install pade
```

#### Via Github (Latest Version):
```bash
$git clone [https://github.com/grei-ufc/pade$](https://github.com/grei-ufc/pade$) cd pade
$ python setup.py install
```

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

Here is a simple example of defining and launching a PADE agent directly from a Python script. This example also demonstrates how to send a basic FIPA-ACL message to trigger the CSV Logging system.

```python
from pade.misc.utility import display_message, start_loop
from pade.core.agent import Agent
from pade.acl.aid import AID
from pade.acl.messages import ACLMessage
from pade.misc.data_logger import logger
from sys import argv
from datetime import datetime

class AgenteHelloWorld(Agent):
    def __init__(self, aid):
        super().__init__(aid=aid)
        
    def on_start(self):
        super().on_start()
        display_message(self.aid.localname, 'Hello World!')
        
        # Send a message to itself to trigger the PADE Sniffer and populate messages.csv
        mensagem = ACLMessage(ACLMessage.INFORM)
        mensagem.set_sender(self.aid)
        mensagem.add_receiver(self.aid)
        mensagem.set_content('Hello World Message!')
        self.send(mensagem)

if __name__ == '__main__':
    # Define the AMS configuration
    ams_config = {'name': 'localhost', 'port': 8000}
    
    # Initialize the session logger (CSV)
    session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    logger.log_session(session_id=session_id, name="HelloWorld_Test", state="Started")

    # Start 1 agent
    agents_per_process = 1
    c = 0
    agents = list()
    
    # Define the base port via argument or use a default
    base_port = int(argv[1]) if len(argv) > 1 else 20000
    
    for i in range(agents_per_process):
        port = base_port + c
        agent_name = f'agente_hello_{port}@localhost:{port}'
        
        agente_hello = AgenteHelloWorld(AID(name=agent_name))
        agente_hello.update_ams(ams_config)
        agents.append(agente_hello)
        c += 1000
    
    start_loop(agents)
```

## 🚀 Changes in the New Version (Python 3.12.11)

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

**Recommended workflow**
Run the entire environment with a single command:
```bash
$ pade start-runtime --port 20000 pade/tests/hello_world/hello_world.py
```

This command orchestrates:
* the AMS on port `8000`;
* the Sniffer on port `8001` when enabled;
* the agent script informed on the command line.

**Advanced workflow**
If you need to debug a specific component in isolation, you can still run the services manually:
```bash
$ python -m pade.core.new_ams test test@test.com 123 8000
$ python -m pade.core.sniffer 8001
$ python hello-agent.py 20000
```
This mode remains useful for low-level troubleshooting and performance analysis.

### 3. Co-Simulation with Mosaik API 3.0+
The `mosaik_driver` module has been completely refactored to support the modern **Mosaik API 3.0** and the strict bytes I/O rules of Python 3.12. PADE agents can now perform seamless asynchronous data fetching (`get_data_async`) and progress tracking during complex power system co-simulations without deadlocks. Check the `tests/mosaik_example` directory for a complete integration example.

### CLI Tools Updated
Commands like `pade create-pade-db`, `pade drop-pade-db`, and `pade start-web-interface` have been removed. The current CLI keeps the integrated `start-runtime` workflow and adds CSV-oriented inspection tools:

* To start AMS, Sniffer, and your agents in a single command:
  ```bash
  $ pade start-runtime --port 20000 pade/tests/hello_world/hello_world.py
  ```

* To view a summary of the current logs:
  ```bash
  $ pade show-logs
  ```
* To export the logs to `logs/exports/` in JSON, CSV, or TXT format:
  ```bash
  $ pade export-logs csv
  ```
