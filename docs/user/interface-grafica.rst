Interface Gráfica
=================

**Atenção:** a antiga interface web do PADE, baseada em Flask e SQLite,
foi removida da arquitetura atual.

O que mudou
-----------

Na versão moderna do framework:

* não existe mais painel web embutido;
* não é mais necessário criar ou manter um banco SQLite;
* a observabilidade passou a ser feita com logs CSV e com o Sniffer.

Como analisar seus dados agora?
-------------------------------

Ao executar o PADE com o Sniffer ativo, o framework cria a pasta
``logs/`` com arquivos estruturados:

* ``sessions.csv``;
* ``agents.csv``;
* ``messages.csv``;
* ``events.csv``.

Além disso, a CLI oferece dois comandos úteis:

.. code-block:: console

    $ pade show-logs

.. code-block:: console

    $ pade export-logs json

Ferramentas recomendadas
------------------------

Os arquivos CSV podem ser consumidos diretamente por:

* Pandas;
* Matplotlib;
* Excel;
* Power BI;
* qualquer pipeline de análise baseada em CSV ou JSON.

Na prática, a combinação entre ``messages.csv`` e ``events.csv`` cobre o
que antes era feito pela interface gráfica legado, com a vantagem de
ser mais simples de automatizar e escalar em experimentos maiores.
