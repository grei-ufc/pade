.. _pade-cli-page:

Linha de comando do PADE
========================

A CLI do PADE foi simplificada para refletir a arquitetura atual do
framework: sem Flask, sem SQLite e com execução integrada baseada em
AMS, Sniffer e logs CSV.

Estrutura geral
---------------

O formato geral é:

::

    pade [comando] [opções]

Comandos disponíveis
--------------------

Os comandos disponíveis atualmente são:

* ``start-runtime``: inicia AMS, Sniffer e um ou mais scripts de agentes
  em um único fluxo;
* ``start-runtime-detailed``: inicia o mesmo fluxo integrado, mas com
  rastros técnicos detalhados de AMS e Sniffer no terminal;
* ``show-logs``: mostra um resumo dos CSVs encontrados na pasta
  ``logs/``;
* ``export-logs``: exporta os logs atuais para ``logs/exports/`` nos
  formatos ``csv``, ``json`` ou ``txt``;
* ``version``: exibe a versão instalada do PADE;
* ``clean-logs``: remove a pasta ``logs/`` e seus arquivos exportados,
  mediante confirmação.

Comando ``start-runtime``
-------------------------

Esse é o comando principal da experiência atual do PADE:

.. code-block:: console

    $ pade start-runtime --port 20000 pade/tests/agent_example_1/agent_example_1_updated.py

Ao executá-lo, o PADE:

* cria a sessão raiz de logs;
* inicia o AMS;
* inicia o Sniffer;
* executa o script de agentes informado com a porta base escolhida.

As opções mais úteis são:

* ``--port``: define a porta base entregue ao script de agentes;
* ``--num``: executa o mesmo script múltiplas vezes, incrementando a
  porta base;
* ``--username`` e ``--password``: credenciais solicitadas pelo runtime
  por compatibilidade com o fluxo legado;
* ``--detailed``: reativa no terminal os rastros detalhados de AMS e
  Sniffer, sem alterar os CSVs gerados;
* ``--pade_ams`` / ``--no_pade_ams``: liga ou desliga a inicialização do
  AMS pelo CLI;
* ``--pade_sniffer`` / ``--no_pade_sniffer``: liga ou desliga a
  inicialização do Sniffer;
* ``--config_file``: permite iniciar o runtime a partir de um arquivo de
  configuração JSON.

Exemplos:

.. code-block:: console

    $ pade start-runtime --port 24000 pade/tests/agent_example_5/agent_example_5_updated.py

.. code-block:: console

    $ pade start-runtime --num 2 --port 20000 meu_script.py

.. code-block:: console

    $ pade start-runtime --no_pade_sniffer --port 20000 meu_script.py

.. code-block:: console

    $ pade start-runtime --detailed --port 20000 pade/tests/mosaik_example/agent_example_1_mosaik_updated.py

O mesmo modo detalhado tambem pode ser chamado pelo alias dedicado:

.. code-block:: console

    $ pade start-runtime-detailed --port 20000 pade/tests/mosaik_example/agent_example_1_mosaik_updated.py

Arquivo atual, pasta atual e caminhos
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

O README legado usava ``hello-agent.py`` apenas como nome ilustrativo.
Esse arquivo nao existe no repositório atual. No PADE novo, a pasta
``pade/tests/hello_world`` traz duas alternativas concretas:

* ``hello_world_minimal.py``: so imprime no terminal;
* ``hello_world.py``: troca uma mensagem ACL real e preenche
  ``messages.csv``.

Se voce quiser comecar pelo caso mais curto, use:

.. code-block:: console

    $ pade start-runtime --port 20000 pade/tests/hello_world/hello_world_minimal.py

Se voce quiser o mesmo exemplo com logging de mensagens, use:

.. code-block:: console

    $ pade start-runtime --port 20000 pade/tests/hello_world/hello_world.py

Esse ``hello_world.py`` cria dois agentes por processo: um destinatario
na porta base e um remetente em ``base_port + 1000``. O remetente envia
uma mensagem ACL real para o destinatario, de forma que ``messages.csv``
e preenchido automaticamente quando o Sniffer esta ativo.

Se voce ja estiver dentro da pasta onde o script esta salvo, pode usar
apenas o nome do arquivo:

.. code-block:: console

    $ cd pade/tests/hello_world
    $ pade start-runtime --port 20000 hello_world_minimal.py

ou, para a variante com logging:

.. code-block:: console

    $ pade start-runtime --port 20000 hello_world.py

Se voce estiver fora da pasta do script, passe um caminho relativo ou
absoluto.

Entendendo ``--num`` e ``--port``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Ao executar:

.. code-block:: console

    $ pade start-runtime --num 3 --port 20000 pade/tests/hello_world/hello_world_minimal.py

o CLI do PADE:

* sobe tres processos independentes para o mesmo script;
* passa um unico argumento posicional para cada processo em
  ``sys.argv[1]``;
* incrementa esse valor em uma unidade por processo.

Nesse caso, os tres processos recebem:

* ``20000``
* ``20001``
* ``20002``

No caso especifico do ``hello_world_minimal.py``, isso resulta em 3
agentes ao todo:

* processo base ``20000``: ``hello_agent_20000``;
* processo base ``20001``: ``hello_agent_20001``;
* processo base ``20002``: ``hello_agent_20002``.

Se voce trocar para o ``hello_world.py`` com logging, ai sim o mesmo
comando gera 6 agentes ao todo:

* processo base ``20000``: ``hello_receiver_20000`` e
  ``hello_sender_21000``;
* processo base ``20001``: ``hello_receiver_20001`` e
  ``hello_sender_21001``;
* processo base ``20002``: ``hello_receiver_20002`` e
  ``hello_sender_21002``.

Dentro do script, esse valor costuma ser lido assim:

.. code-block:: python

    base_port = int(sys.argv[1]) if len(sys.argv) > 1 else 20000

Se o proprio script criar mais de um agente por processo, o total final
de agentes sera:

.. code-block:: text

    total_agents = num * agents_per_process

Exemplo: se ``agents_per_process = 3`` e o script espaciar as portas em
``1000``, o processo base ``20000`` pode criar agentes em ``20000``,
``21000`` e ``22000``; o processo base ``20001`` pode criar agentes em
``20001``, ``21001`` e ``22001``; e assim por diante.

Executando mais de um arquivo
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Tambem e possivel subir mais de um script:

.. code-block:: console

    $ pade start-runtime --num 3 --port 20000 script_a.py script_b.py

No CLI atual, a porta e incrementada depois de cada processo lancado.
Portanto:

* ``script_a.py`` recebe ``20000``, ``20001`` e ``20002``;
* ``script_b.py`` recebe ``20003``, ``20004`` e ``20005``.

Usando ``--config_file``
~~~~~~~~~~~~~~~~~~~~~~~~

O runtime integrado ainda aceita um arquivo JSON de configuracao. Um
exemplo valido para o PADE novo e:

.. code-block:: json

    {
      "agent_files": [
        "pade/tests/agent_example_1/agent_example_1_updated.py",
        "pade/tests/agent_example_3/agent_example_3_updated.py"
      ],
      "port": 20000,
      "num": 1,
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

Execucao:

.. code-block:: console

    $ pade start-runtime --config_file pade_config.json

O bloco ``pade_web`` do legado nao deve mais ser usado, pois a
interface Flask foi removida da arquitetura atual.

Quando usar ``--no_pade_sniffer``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Em cargas muito altas, ``--no_pade_sniffer`` continua sendo util. O novo
PADE nao grava mais em SQLite, mas o Sniffer ainda intercepta trafego e
grava em disco, o que pode introduzir custo extra em simulacoes grandes.

Comando ``show-logs``
---------------------

Depois de uma execução, você pode inspecionar rapidamente o volume de
dados gerado:

.. code-block:: console

    $ pade show-logs

Saída típica:

.. code-block:: console

    $ pade show-logs
    === PADE Data Logs ===
    Log directory: logs
    sessions.csv: 1 entries
    events.csv: 15 entries
    messages.csv: 4 entries
    agents.csv: 2 entries

Comando ``export-logs``
-----------------------

Os logs podem ser exportados para formatos mais convenientes para
análise externa:

.. code-block:: console

    $ pade export-logs csv

.. code-block:: console

    $ pade export-logs json

.. code-block:: console

    $ pade export-logs txt

Os arquivos exportados são criados em subpastas como
``logs/exports/json/`` ou ``logs/exports/txt/``.

Comandos ``version`` e ``clean-logs``
-------------------------------------

Para verificar a versão instalada:

.. code-block:: console

    $ pade version

Para apagar todos os logs atuais:

.. code-block:: console

    $ pade clean-logs

Esse último comando pede confirmação antes de remover a pasta
``logs/``.

Comandos removidos do fluxo legado
----------------------------------

Na versão atual não fazem mais parte da CLI:

* ``create-pade-db``;
* ``drop-pade-db``;
* ``start-web-interface``.

Esses comandos deixaram de existir porque o PADE atual não depende mais
de banco de dados SQLite nem de interface web embutida.
