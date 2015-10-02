Instalação
==========

Instalar o PADE em seu computador, ou dispositivo embarcado é bem simples, basta que ele esteja conectado à internet!

Instalação via PIP
------------------

Para instalar o PADE via PIP basta digitar em um terminal:

::

    $ pip install pade


Pronto! O Pade está instalado!

Instalação via GitHub
---------------------

Se você quiser ter acesso ao fonte do PADE e instala-lo a partir do fonte, basta digitar as seguintes linhas no terminal:

::

    $ git clone https://github.com/lucassm/Pade
    $ cd Pade
    $ python setup.py install 

Pronto o PADE está pronto para ser utilizado, faça um teste no IPython digitando:

::

    from pade.misc.utility import display_message
