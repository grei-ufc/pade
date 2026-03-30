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
