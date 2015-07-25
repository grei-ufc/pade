Python Agent DEvelopment framework (PADE)
==============

![Logo padrão do projeto PADE] (https://raw.githubusercontent.com/lucassm/Pade/master/pade/images/pade_logo.png)

PADE é um framework para desenvolvimento, execução e gerenciamento de sistemas multiagentes em ambientes de computação distribuída. PADE é escrito 100% em Python e utiliza as bibliotecas do projeto Twisted para implementar a comunicação entre os nós da rede.
PADE é software livre, licenciado sob os termos da licença MIT, desenvolvido no ambito da Universidade Federal do Ceará pelo Grupo de Redes Elétricas Inteligentes (GREI) que pertence ao departamento de Engenharia Elétrica.
Qualquer um que queira contribuir com o projeto é convidado a baixar, executar, testar e enviar feedback a respeito das impressões tiradas da plataforma.

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

