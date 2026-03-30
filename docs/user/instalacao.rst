.. _installation-page:

Instalação
==========

Instalar o PADE é simples. A versão atual do projeto é mantida para
Python 3.12 ou superior.

Instalação via PyPI
-------------------

Para instalar o PADE a partir do PyPI:

.. code-block:: console

    $ python -m pip install pade

Pronto: o comando ``pade`` já estará disponível no ambiente.

Instalação a partir do repositório
----------------------------------

Se você quiser trabalhar com o código-fonte, documentação e exemplos
adaptados, clone o repositório oficial:

.. code-block:: console

    $ git clone https://github.com/grei-ufc/pade
    $ cd pade
    $ python -m pip install -e .

Essa forma é a mais indicada para desenvolvimento e revisão dos
exemplos em ``pade/tests/``.

Teste rápido após a instalação
------------------------------

Um teste simples consiste em executar o primeiro exemplo adaptado:

.. code-block:: console

    $ pade start-runtime --port 20000 pade/tests/agent_example_1/agent_example_1_updated.py

Se o ambiente estiver correto, o runtime abrirá AMS, Sniffer e os
agentes do exemplo, além de criar a pasta ``logs/`` no diretório atual.

Usando ambiente virtual
-----------------------

Em Python 3.12+, o caminho mais simples é usar ``venv``:

.. code-block:: console

    $ python -m venv .venv

Ativação do ambiente virtual:

.. code-block:: console

    # Linux / macOS
    $ source .venv/bin/activate

.. code-block:: console

    # Windows
    > .venv\Scripts\activate

Depois disso, instale o PADE normalmente:

.. code-block:: console

    $ python -m pip install pade

Observações importantes
-----------------------

Na versão atual:

* não é necessário criar banco de dados antes de executar o framework;
* os dados de simulação são gravados automaticamente em CSV;
* o fluxo recomendado voltou a ser o integrado, usando
  ``pade start-runtime``.
