
.. _installation-page:

Instalação
==========

Instalar o PADE em seu computador, ou dispositivo embarcado é bem simples, basta que ele esteja conectado à internet!

Instalação via PIP
------------------

Para instalar o PADE via PIP basta digitar em um terminal:

.. code-block:: console

    $ pip install pade


Pronto! O Pade está instalado!

Instalação via GitHub
---------------------

Se você quiser ter acesso ao fonte do PADE e instala-lo a partir do repositório oficial, basta digitar os seguintes comandos no terminal:

.. code-block:: console

    $ git clone https://github.com/grei-ufc/pade
    $ cd pade
    $ python setup.py install

Pronto o PADE está pronto para ser utilizado, faça um teste entrando na pasta de exemplos e digitando na linha de comandos:

::

    pade start_runtime --port 20000 agent_example_1.py

Instalando o PADE em um ambiente virtual
----------------------------------------

Quando se trabalha com módulos Python é importante saber criar e manipular ambientes virtuais para gerenciar as dependências do projeto de uma maneira mais organizada. Aqui iremos mostrar como criar um ambiente virtual python, ativá-lo e utilizar o pip para instalar o PADE. Para uma visão mais detalhada sobre ambientes virtuais Python, acesse: `Python Guide <http://docs.python-guide.org/en/latest/dev/virtualenvs/>`_.

Primeiro você irá precisar ter o pacote virtualenv instalado em seu PC, instale-o digitando o comando:

.. code-block:: console

	$ pip install virtualenv

Após instalado o virtualenv é hora de criar um ambiente virtual, por meio do seguinte comando:

.. code-block:: console
	
	$ cd my_project_folder 
	$ virtualenv venv

Para ativar o ambiente virtual criado, digite o comando:

.. code-block:: console
	
	$ source venv/bin/activate

Agora basta instalar o pade, por meio do pip:

.. code-block:: console

	$ pip install pade

.. note:: Você pode utilizar também a excelente distribuição python para computação científica Anaconda. Veja como aqui: `AnacondaInc <https://www.anaconda.com/distribution/>`_.