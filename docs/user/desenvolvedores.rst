Estrutura construtiva do PADE
=============================

Este guia tem o objetivo de apoiar quem deseja entender e evoluir o
PADE internamente. A base conceitual do framework continua sendo a
mesma do legado, mas a versão atual foi reorganizada para Python 3.12+,
com execução integrada via CLI, telemetria em CSV e sem dependência de
Flask ou SQLite.

Visão geral da arquitetura
--------------------------

O PADE continua tendo o Twisted como motor assíncrono principal. Isso
significa que o framework é orientado a eventos e trabalha de forma
natural com conexões TCP, agendamento temporal e protocolos de
conversação FIPA.

Na versão atual:

* o AMS e o Sniffer continuam sendo serviços independentes
  internamente;
* o comando ``pade start-runtime`` voltou a ser o fluxo recomendado,
  orquestrando AMS, Sniffer e scripts de agentes em um único comando;
* o armazenamento de dados passou a ser feito em CSV, dentro da pasta
  ``logs/`` do diretório de trabalho;
* a sessão compartilhada do runtime é propagada para os agentes por meio
  da variável de ambiente ``PADE_SESSION_ID``, acessível com
  ``get_shared_session_id()``.

Pacote ``core``
---------------

A essência do framework está no pacote ``pade.core``. Os módulos mais
importantes são:

* ``agent.py``: define a classe ``Agent`` e a infraestrutura básica de
  envio, recepção, registro no AMS e gerenciamento de comportamentos;
* ``new_ams.py``: implementa o AMS (Agent Management System), ou seja, o
  agente responsável por manter a tabela de agentes ativos e publicá-la
  para a plataforma;
* ``peer.py``: contém o protocolo básico de rede utilizado pelo PADE,
  trabalhando com transporte em bytes e integração com o Twisted;
* ``sniffer.py``: implementa o agente Sniffer, responsável por observar
  o tráfego FIPA-ACL e gravar ``messages.csv``.

Módulo ``agent.py``
~~~~~~~~~~~~~~~~~~~

A classe ``Agent`` é o ponto de entrada para praticamente todo
desenvolvimento no PADE. Ao estender essa classe, você passa a contar
com:

* identificação junto ao AMS;
* envio de mensagens ACL com ``send()``;
* agendamento não bloqueante com ``call_later()``;
* execução de tarefas bloqueantes fora do reactor com
  ``call_in_thread()`` via ``pade.misc.utility``;
* associação de comportamentos em ``behaviours`` e
  ``system_behaviours``;
* ganchos de ciclo de vida como ``on_start()`` e ``react()``.

Em termos práticos, o ciclo de vida de um agente costuma seguir este
fluxo:

1. o script instancia o agente com um ``AID``;
2. o agente recebe a configuração do AMS por ``update_ams()``;
3. o runtime chama ``start_loop(agents)``;
4. o agente se identifica no AMS e passa a receber a tabela de agentes;
5. os comportamentos associados passam a tratar mensagens, protocolos e
   eventos temporais.

Módulo ``new_ams.py``
~~~~~~~~~~~~~~~~~~~~~

O AMS é o núcleo de gerenciamento da plataforma. Na implementação atual
ele:

* recebe a identificação dos agentes;
* mantém a tabela de agentes ativos;
* publica atualizações dessa tabela usando a lógica de
  editor-assinante;
* executa verificações periódicas de conectividade;
* registra eventos da infraestrutura em ``events.csv``.

Embora o comando ``start-runtime`` peça ``username`` e ``password`` por
compatibilidade com o fluxo legado, a versão atual não depende mais de
autenticação via banco de dados ou interface web.

Módulos ``peer.py`` e ``sniffer.py``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

O módulo ``peer.py`` implementa o protocolo de transporte base do PADE,
fazendo a ponte entre a infraestrutura Twisted e os objetos ACL do
framework.

O módulo ``sniffer.py`` hospeda o agente Sniffer. Ele é especialmente
importante porque:

* monitora o tráfego ACL da plataforma;
* grava ``messages.csv`` com ``message_id``, ``conversation_id``,
  performative, protocolo, remetente, destinatários e conteúdo;
* complementa os logs feitos por agentes e pelo runtime.

Pacote ``misc``
---------------

O pacote ``pade.misc`` concentra utilidades de uso geral. Os módulos
mais relevantes para a documentação atual são:

* ``utility.py``: contém ``display_message()``, ``call_later()``,
  ``call_in_thread()`` e ``start_loop()``;
* ``data_logger.py``: contém o logger CSV do framework e a função
  ``get_shared_session_id()``;
* ``common.py``: mantém classes de sessão e compatibilidade com fluxos
  mais avançados, embora os exemplos atuais usem principalmente
  ``start_loop(agents)``.

Logging em CSV
--------------

O antigo fluxo baseado em SQLite foi removido. Em seu lugar, o PADE
gera arquivos CSV diretamente na pasta ``logs/``:

* ``sessions.csv``: sessões iniciadas pelo runtime e pelos exemplos;
* ``agents.csv``: estado dos agentes por sessão;
* ``messages.csv``: histórico das mensagens FIPA-ACL observadas;
* ``events.csv``: eventos auxiliares de infraestrutura e debug.

Ao executar um script com ``pade start-runtime``, o CLI cria uma sessão
raiz e propaga o identificador para o processo dos agentes. Por isso,
nos exemplos atuais, o padrão recomendado é:

::

    from pade.misc.data_logger import get_shared_session_id, logger

    session_id = get_shared_session_id()
    logger.log_session(
        session_id=session_id,
        name=f"MinhaSessao_{session_id}",
        state="Started"
    )

Esse padrão evita que cada script gere um ``session_id`` próprio e
desalinhado do runtime.

Fluxo recomendado de execução
-----------------------------

O modo recomendado hoje é o integrado:

.. code-block:: console

    $ pade start-runtime --port 20000 meu_script.py

Esse comando:

* inicia o AMS;
* inicia o Sniffer;
* cria a sessão raiz de logs;
* executa o script informado com a porta base escolhida.

Se você precisar depurar um componente isoladamente, ainda é possível
usar o fluxo manual:

.. code-block:: console

    $ python -m pade.core.new_ams user user@pade.com 12345 8000

.. code-block:: console

    $ python -m pade.core.sniffer 8001

.. code-block:: console

    $ python meu_script.py 20000

Esqueleto de um novo agente
---------------------------

O padrão mínimo para um script compatível com a versão atual pode ser
resumido assim:

::

    from pade.misc.utility import display_message, start_loop
    from pade.misc.data_logger import get_shared_session_id, logger
    from pade.core.agent import Agent
    from pade.acl.aid import AID
    from sys import argv


    class MeuAgente(Agent):
        def __init__(self, aid, session_id):
            super().__init__(aid=aid, debug=False)
            self.session_id = session_id

        def on_start(self):
            super().on_start()
            display_message(self.aid.localname, 'Agente iniciado!')
            logger.log_agent(
                agent_id=self.aid.name,
                session_id=self.session_id,
                name=self.aid.name,
                state='Active'
            )


    if __name__ == '__main__':
        ams_config = {'name': 'localhost', 'port': 8000}
        session_id = get_shared_session_id()

        logger.log_session(
            session_id=session_id,
            name=f"Exemplo_{session_id}",
            state='Started'
        )

        port = int(argv[1]) if len(argv) > 1 else 20000
        agente = MeuAgente(AID(name=f'meu_agente@localhost:{port}'), session_id)
        agente.update_ams(ams_config)

        start_loop([agente])

Esse esqueleto é o ponto de partida mais fiel ao PADE atual. A partir
dele, basta adicionar comportamentos temporais, filtros ou protocolos
FIPA conforme o tipo de interação desejado.
