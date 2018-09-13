# Python Agent DEvelopment framework (PADE)


[![Join the chat at https://gitter.im/lucassm/Pade](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/lucassm/Pade?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)

<img src="https://raw.githubusercontent.com/lucassm/Pade/master/pade/images/pade_logo.png" alt="PADE" width="4.0in">

PADE its a framework for developing, executing and mannaging multi-agent systems in distributed computing enviroments. PADE code is 100% Python and has its core in Twisted, a python package for implementing distributed applications.

PADE is also free software and licenced in terms of MIT licence. First it was developed in Federal University of Ceará (Brazil) by Electric Smart Grids Group (GREI) in Electric Engineering Department (DEE). Now everyone that has interest in developing PADE is welcome to dowload, install, test, use and send us feedback.

## Documentation

PADE is well documented. You can access the documentation hear: [PADE documentation](https://pade-docs-en.readthedocs.io/en/latest/) 

## Dependencies

PADE is developed in [Python 3.7](https://www.python.org/) and has a [Twisted](https://twistedmatrix.com/trac/) core.

## Install

Via Python Package Index (PyPI):

    $ pip install pade

Via Github:

	$ git clone https://github.com/greiufc/pade
	$ cd pade
	$ python setup.py install

That's all!

## Example

Hello world in PADE:

```python
from pade.misc.utility import display_message
from pade.misc.common import PadeSession
from pade.core.agent import Agent
from pade.acl.aid import AID


class AgenteHelloWorld(Agent):
    def __init__(self, aid):
        super(AgenteHelloWorld, self).__init__(aid=aid, debug=True)
        display_message(self.aid.localname, 'Hello World!')


def config_agents():

    agents = list()

    agente_hello = AgenteHelloWorld(AID(name='agente_hello'))
    agents.append(agente_hello)

    s = PadeSession()
    s.add_all_agents(agents)
    s.register_user(username='pade_user', email='user@pademail.com', password='12345')

    return s

if __name__ == '__main__':

    s = config_agents()
    s.start_loop()

```

