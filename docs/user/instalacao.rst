.. _installation-page:

Instalação
==========

Instalar o PADE é simples. A versão atual do projeto é mantida para
Python 3.12 ou superior.

Instalação via PyPI
-------------------

Para instalar o PADE a partir do PyPI:

.. code-block:: console

    $ python -m pip install pade-agents

Pronto: o comando ``pade`` já estará disponível no ambiente. No PyPI, a
distribuição publicada se chama ``pade-agents``, mas o pacote Python e o
CLI permanecem ``pade``.

Instalação a partir do repositório
----------------------------------

Se você quiser trabalhar com o código-fonte, documentação e exemplos
adaptados, clone o repositório oficial:

.. code-block:: console

    $ git clone https://github.com/grei-ufc/pade
    $ cd pade
    $ uv sync

Essa forma é a mais indicada para desenvolvimento e revisão dos
exemplos em ``pade/tests/``.

Teste rápido após a instalação
------------------------------

O teste mais simples consiste em executar o Hello World mínimo, que
apenas imprime no terminal:

.. code-block:: console

    $ uv run pade start-runtime --port 20000 pade/tests/hello_world/hello_world_minimal.py

Se o ambiente estiver correto, o runtime abrirá AMS, Sniffer e os
agentes do exemplo, além de criar a pasta ``logs/`` no diretório atual.
Nesse caso, você verá ``sessions.csv``, ``agents.csv`` e ``events.csv``
logo na primeira execução.

Se você quiser um teste igualmente simples, mas que também valide o
Sniffer e preencha ``messages.csv``, use a variante com logging:

.. code-block:: console

    $ uv run pade start-runtime --port 20000 pade/tests/hello_world/hello_world.py

Observe que você não precisa obrigatoriamente usar ``cd`` até a pasta do
script. Se estiver na raiz do repositório, pode passar o caminho
relativo completo. Se já estiver dentro da pasta do script, pode usar só
o nome do arquivo.

Usando ambiente virtual
-----------------------

Em Python 3.12+, o caminho mais simples é usar ``uv`` para criar e manter
o ambiente virtual automaticamente:

.. code-block:: console

    $ uv sync

Se você quiser ativar o ambiente criado pelo ``uv`` manualmente:

.. code-block:: console

    # Linux / macOS
    $ source .venv/bin/activate

.. code-block:: console

    # Windows
    > .venv\Scripts\activate

Depois disso, você pode usar o comando ``pade`` diretamente no shell ativado
ou continuar pelo fluxo do ``uv``:

.. code-block:: console

    $ uv run pade version

Observações importantes
-----------------------

Na versão atual:

* não é necessário criar banco de dados antes de executar o framework;
* os dados de simulação são gravados automaticamente em CSV;
* o fluxo recomendado voltou a ser o integrado, usando
  ``pade start-runtime``.
