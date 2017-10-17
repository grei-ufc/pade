Instalação
==========

Instalar o PADE em seu computador, ou dispositivo embarcado é bem simples, basta que ele esteja conectado à internet!

Instalação via PIP
------------------

Para instalar o PADE via PIP basta digitar em um terminal:

.. code-block:: console

    $ pip install pade


Pronto! O Pade está instalado!

.. warning::
    Atenção! O PADE é oficalmente testado no ambiente Ubuntu 14.04 LTS. Sendo necessário a instalação dos pacotes python-twisted-qt4reactor e pyside

Instalação via GitHub
---------------------

Se você quiser ter acesso ao fonte do PADE e instala-lo a partir do fonte, basta digitar as seguintes linhas no terminal:

.. code-block:: console

    $ git clone https://github.com/lucassm/Pade
    $ cd Pade
    $ python setup.py install 

Pronto o PADE está pronto para ser utilizado, faça um teste no interpretador Python digitando:

::

    from pade.misc.utility import display_message

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
 

Ativando a interface gráfica
----------------------------
 
Para que a interface gráfica do PADE funcione é necessário que o pacote PySide, um binding do Qt, esteja instalado. Como não existem binários do PySide disponíveis para Linux e o procedimento de compilação é bastante demorado, é necessário fazer o seguinte procedimento:

1. Instale o PySide via linha de comando:

.. code-block:: console

	$ sudo apt-get install python-pyside

2. Copie a pasta com a instalação do PySide da pasta site-packages, onde fica a instalação padrão do Python em seu sistema operacional, e então coloque dentro da pasta onde ficam instalados os pacotes padrões do ambiente virtual, no nosso caso: venv/lib/python2.7/site-packages.

Pronto a instalação do PySide no ambiente virtual está concluída, mas outro procedimento que deve ser realizado é a instalação do reactor que interage com o loop de eventos do PySide, para isso, digite:

.. code-block:: console

	$ sudo apt-get install python-qt4reactor

