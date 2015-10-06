Python Agent DEvelopment framework (PADE)
==============

[![Join the chat at https://gitter.im/lucassm/Pade](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/lucassm/Pade?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)

![Logo padrão do projeto PADE] (https://raw.githubusercontent.com/lucassm/Pade/master/pade/images/pade_logo.png)

PADE é um framework para desenvolvimento, execução e gerenciamento de sistemas multiagentes em ambientes de computação distribuída. PADE é escrito 100% em Python e utiliza as bibliotecas do projeto Twisted para implementar a comunicação entre os nós da rede.
PADE é software livre, licenciado sob os termos da licença MIT, desenvolvido no ambito da Universidade Federal do Ceará pelo Grupo de Redes Elétricas Inteligentes (GREI) que pertence ao departamento de Engenharia Elétrica.
Qualquer um que queira contribuir com o projeto é convidado a baixar, executar, testar e enviar feedback a respeito das impressões tiradas da plataforma.

Dependências
-----

PADE é desenvolvido com [Python 2.7](https://www.python.org/) no topo do framework [Twisted](https://twistedmatrix.com/trac/) que é sua principal dependência.

Instalação
------

Para baixar e instalar o PADE, basta abrir uma seção do terminal de comandos Linux e digitar os seguintes comandos:

	$ git clone https://github.com/lucassm/PADE
	$ cd PADE
	$ sudo python setup.py install

Pronto! Você já está pronto para utilizar o PADE!

Exemplo
------

Um simples agente desenvolvido com as bibliotecas do PADE:

```python
from pade.misc.utility import display_message
from pade.misc.common import set_ams, start_loop
from pade.core.agent import Agent
from pade.acl.aid import AID


class AgenteHelloWorld(Agent):
    def __init__(self, aid):
        super(AgenteHelloWorld, self).__init__(aid=aid, debug=False)
        display_message(self.aid.localname, 'Hello World!')

if __name__ == '__main__':

    set_ams('localhost', 8000, debug=False)

    agents = list()

    agente_hello = AgenteHelloWorld(AID(name='agente_hello'))
    agente_hello.ams = {'name': 'localhost', 'port': 8000}
    agents.append(agente_hello)

    start_loop(agents, gui=True)
```

Funcionalidades
------

Pade possui as seguintes funcionalidades:

* Bibliotecas para desenvolver agentes que se comunicam no Padrão FIPA-ACL;
* Fácil de utilizar e com versatilizade do Python;
* Ambiente de execução distribuído testado em hardware embarcados como Raspberry Pi e BeagleBone Black;
* Desenvolvido inteiramente em Python! isso mesmo feito por quem ama Python para quem ama programar em Python;
* Interface gráfica para monitoramento de agentes;
* Projeto em pleno desenvolvimento;
* É software livre.


Interface de Desenvolvimento
-------

![Interface do Python](https://raw.githubusercontent.com/lucassm/Pade/master/pade/images/interface.png)

