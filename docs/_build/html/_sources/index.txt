.. Pade documentation master file, created by
   sphinx-quickstart on Sat Sep 12 19:30:28 2015.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Python Agent DEvelopment framework
==================================

Sistemas Multiagentes para Python!
----------------------------------

PADE é um framework para desenvolvimento, execução e gerenciamento de sistemas multiagentes em ambientes de computação distribuída.

PADE é escrito 100% em Python e utiliza as bibliotecas do projeto Twisted para implementar a comunicação entre os nós da rede.

PADE é software livre, licenciado sob os termos da licença MIT, desenvolvido no ambito da Universidade Federal do Ceará pelo Grupo de Redes Elétricas Inteligentes (GREI) que pertence ao departamento de Engenharia Elétrica.

Qualquer um que queira contribuir com o projeto é convidado a baixar, executar, testar e enviar feedback a respeito das impressões tiradas da plataforma. 

PADE é divertido!
~~~~~~~~~~~~~~~~~

::

    # este e o arquivo start_ams.py
    from pade.misc.common import set_ams, start_loop

    if __name__ == '__main__':
        set_ams('localhost', 8000)
        start_loop(list(), gui=True)


E fácil de instalar!
~~~~~~~~~~~~~~~~~~~~

Para instalar o PADE basta executar o seguinte comando em um terminal linux: 

::

    $ pip install pade
    $ python start_ams.py

Créditos
~~~~~~~~

PADE é software livre e é desenvolvido pela equipe do grupo de redes elétricas inteligentes:

**Lucas Melo**: Ditador Benevolente Vitalício (Benevolent Dictator for Life) do PADE

**Professora Ruth Leão**: Coordenadora do Grupo de Redes Elétricas Inteligentes da UFC

**Professor Raimundo Furtado**: Coordenador do Grupo de Redes Elétricas Inteligentes da UFC

**Professor Giovanni Cordeiro**: Colaborador do projeto PADE


Guia do Usuário
----------------

.. toctree::
   :maxdepth: 2

   user/instalacao.rst
   user/hello-world
   user/meu-primeiro-agente
   user/agentes-temporais
   user/enviando-mensagens
   user/recebendo-mensagens
   user/um-momento
   user/enviando-objetos
   user/selecao-de-mensagens
   user/interface-grafica
   user/protocolos



Referência da API do PADE 
-------------------------

.. toctree::
   :maxdepth: 2

   api


