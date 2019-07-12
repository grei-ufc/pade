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

PADE its a framework for developing, executing and mannaging multi-agent systems in distributed computing enviroments. PADE code is 100% Python and has its core in Twisted, a python package for implementing distributed applications.

PADE is also free software and licenced in terms of MIT licence. First it was developed in Federal University of Ceará (Brazil) by Electric Smart Grids Group (GREI) in Electric Engineering Department (DEE). Now everyone that has interest in developing PADE is welcome to download, install, test, use and send us feedback.

## Documentation

PADE is well documented. You can access the documentation here: [PADE documentation](https://pade.readthedocs.io/en/latest/)

## Dependencies

PADE is developed in [Python 3.7](https://www.python.org/) and has a [Twisted](https://twistedmatrix.com/trac/) core.

## Install

#### Via Python Package Index (PyPI):
```bash
$ pip install pade
```

#### Via Github:
```bash
$ git clone https://github.com/greiufc/pade
$ cd pade
$ python setup.py install
```

See the complete process in this video: [HOW TO install PADE](https://asciinema.org/a/ELHfOxZnMUjZyLa8bITJ0AQnP)

## Docker

Build container
```bash
$ docker-compose up -d
````

List containers
```bash
$ docker ps

CONTAINER ID        IMAGE
8d7cb00972c9        pade_pade
```

Get inside container
```bash
$ docker exec -it <CONTAINER_ID> bash
```




## Example

Hello world in PADE:

```python
from pade.misc.utility import display_message, start_loop
from pade.core.agent import Agent
from pade.acl.aid import AID
from sys import argv

class AgenteHelloWorld(Agent):
    def __init__(self, aid):
        super(AgenteHelloWorld, self).__init__(aid=aid)
        display_message(self.aid.localname, 'Hello World!')


if __name__ == '__main__':

    agents_per_process = 3
    c = 0
    agents = list()
    for i in range(agents_per_process):
        port = int(argv[1]) + c
        agent_name = 'agente_hello_{}@localhost:{}'.format(port, port)
        agente_hello = AgenteHelloWorld(AID(name=agent_name))
        agents.append(agente_hello)
        c += 1000
    
    start_loop(agents)
```

## Changes in this new version

Some changes has been added in this new version, but don't worry about that if you are using pade in your simulations, it's very easy adjust this version in old versions.

The main and bigger change in Pade is in how you launch your agents. Now when you install Pade via pip command or via setup.py install you install too a pade terminal command line (cli) that launch your pade applications.

As example, if you put the hello world example code in a file with the name hello-agent.py and you want to launch this agent just one time, you could type in your command line interface:

```shell
$ pade start-runtime hello-agent.py 
```

If you want to launch this agent 3 times, than you type:

```shell
$ pade start-runtime --num 3 hello-agent.py 
```

If you wanto to launch the 3 agents in ports 20000, 20001 and 20002, than you just type:

```shell
$ pade start-runtime --num 3 --port 20000 hello-agent.py 
```

Here we have to explain some points in how Pade executes the agents.

When you type the commands `--num 3` and `--port 20000` you tell to Pade command line tool to execute the content of file hello-agent.py 3 times. Each time, the file content will be executed in a new process and the attribute port will be passed as argument in this process with a unit incremment in each time. For example, in the case `--num 3` and `--port 2000`, the arguments passed for agents are 2000, 2001 and 2002.

This arguments should  be accessed in the code with `sys.argv[1]`. So you can execute how many agents as you want per process. In the hello-agent.py example there is a for loop that will repeat many times as defined in agents_per_process variable. That will define the number of agents in each process. In the example, since the `--num` parameter is 3 and the agents_per_process variable is 3 the pade will start 9 agents in ports: 20000, 21000, 22000, 20001, 210001, 22001, 20002, 210002 and 22002.

The command line will support mode than one agent file too, for example if you have the agents in mode than one file you could start then with a command like this:

```shell
$ pade start-runtime --num 3 --port 20000 hello-agent_1.py hello-agent_2.py
```

In this case the first agent receive in the `sys.argv[1]` the value 20000 and the second, the value 20001, and so on.

There is another way to launch the Pade agents. Is with a config file in the json format. Here it's a example of config file:

```json
{ 
    "agent_files": [
        "agent_example_1.py",
        "agent_example_3.py"
    ],
    "port": 20000,
    "num": 2,
    "pade_ams": {
        "launch": true,
        "host": "localhost",
        "port": 8000
    },
    "pade_web": {
        "active": true,
        "host": "localhost",
        "port": 5000
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

To launch then, just type the command line:

```shell
pade start-runtime --config_file pade_config.json
```

If you need to execute simulations with a high number of agents that send and receive messages, something like 500 agents sending 5 messages per second, is recommended that you launch your pade session with a option `--no_pade_sniffer` because the register of this messages in database will overhead your pade execution. Than, the example could be:

```shell
$ pade start-runtime --num 3 --port 20000  --no_pade_sniffer hello-agent_1.py hello-agent_2.py
```

Another useful commands in Pade CLI are:

```shell
$ pade create-pade-db
```

```shell
$ pade drop-pade-db
```

```shell
$ pade start-web-interface
```

To show a complete list of pade comands in the CLI, just type `pade` in terminal command line.

To show the agents in action, show the video in this link: [pade agents start example]()
