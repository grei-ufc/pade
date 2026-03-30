.. Pade documentation master file

Python Agent DEvelopment framework
==================================

Sistemas Multiagentes em Python 3.12+
-------------------------------------

O PADE é um framework para desenvolvimento, execução e gerenciamento de sistemas multiagentes em ambientes de computação distribuída.

PADE é escrito 100% em Python e utiliza as bibliotecas do projeto `Twisted <http://twistedmatrix.com/>`_ para implementar a comunicação assíncrona entre os nós da rede.

O PADE é software livre, licenciado sob os termos da licença MIT, desenvolvido pelo Grupo de Redes Elétricas Inteligentes (GREI) do Departamento de Engenharia Elétrica da Universidade Federal do Ceará. 

Qualquer um que queira contribuir com o projeto é convidado a baixar, executar, testar e enviar feedback a respeito das impressões tiradas da plataforma.

PADE é simples!
~~~~~~~~~~~~~~~

O desenvolvimento e a execução de agentes no PADE moderno (Python 3.12+) foram simplificados. Os agentes agora são instanciados diretamente via código Python, sem a necessidade de comandos CLI complexos.

::

    # agent_example_1.py
    # A simple hello agent in PADE!

    from pade.misc.utility import display_message, start_loop
    from pade.core.agent import Agent
    from pade.acl.aid import AID
    from pade.misc.data_logger import logger
    from sys import argv
    from datetime import datetime

    class AgenteHelloWorld(Agent):
        def __init__(self, aid):
            super().__init__(aid=aid)
            
        def on_start(self):
            super().on_start()
            display_message(self.aid.localname, 'Hello World!')

    if __name__ == '__main__':
        # 1. Configuracao do AMS
        ams_config = {'name': 'localhost', 'port': 8000}
        
        # 2. Inicializacao do Log (CSV)
        session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        logger.log_session(session_id=session_id, name="Hello_World", state="Started")

        agents_per_process = 3
        c = 0
        agents = list()
        
        # 3. Porta Base
        base_port = int(argv[1]) if len(argv) > 1 else 20000
        
        for i in range(agents_per_process):
            port = base_port + c
            agent_name = f'agent_hello_{port}@localhost:{port}'
            
            agente_hello = AgenteHelloWorld(AID(name=agent_name))
            agente_hello.update_ams(ams_config)
            
            agents.append(agente_hello)
            c += 1000
        
        # 4. Iniciar Loop do Twisted
        start_loop(agents)

Se você quiser saber o passo a passo de como rodar este exemplo (iniciando o AMS e o Sniffer em terminais separados), siga a documentação aqui: :ref:`hello-world-page`. 

É fácil de instalar!
~~~~~~~~~~~~~~~~~~~~

Para instalar a versão estável do PADE via PyPI, execute: 

.. code-block:: console

    $ pip install pade

Para desenvolvedores e pesquisadores (recomendado), instale a versão mais recente clonando o repositório do GREI:

.. code-block:: console

    $ git clone https://github.com/grei-ufc/pade
    $ cd pade
    $ python setup.py install

Veja mais detalhes aqui: :ref:`installation-page`.

Principais Funcionalidades
~~~~~~~~~~~~~~~~~~~~~~~~~~

O PADE foi desenvolvido tendo em vista os rígidos requisitos de sistemas de automação e co-simulação de redes elétricas (ex: Mosaik). O framework oferece:

**Orientação a Objetos**
  Abstração total para construção de agentes e de seus comportamentos;

**Mensagens FIPA-ACL**
  Módulo avançado para construção, envio e tratamento de mensagens no padrão internacional FIPA-ACL;

**Protocolos FIPA Nativos**
  Classes prontas para os protocolos Request, Contract-Net e Subscribe;

**Logging em CSV de Alta Performance**
  Substituição completa de bancos de dados legados por um sistema de I/O otimizado. O PADE registra sessões, agentes, eventos e todas as mensagens trafegadas diretamente em arquivos `.csv` (prontos para leitura com Pandas);

**Envio de Objetos Binários (Pickle)**
  Suporte robusto para encapsulamento e envio de dados complexos (como matrizes Numpy e dataframes) no corpo das mensagens;

**Co-Simulação Assíncrona**
  Gerenciadores assíncronos que permitem integração sem deadlocks com orquestradores de tempo discreto.


Guia do Usuário
---------------

.. toctree::
   :maxdepth: 2

   user/instalacao
   user/pade-cli
   user/hello-world
   user/agentes-temporais
   user/enviando-mensagens
   user/recebendo-mensagens
   user/um-momento
   user/enviando-objetos
   user/selecao-de-mensagens
   user/interface-grafica
   user/protocolos
   user/desenvolvedores