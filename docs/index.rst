.. Pade documentation master file, created by
   sphinx-quickstart on Sat Sep 12 19:30:28 2015.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Python Agent DEvelopment framework
==================================

Sistemas Multiagentes para Python!
----------------------------------

PADE é um framework para desenvolvimento, execução e gerenciamento de sistemas multiagentes em ambientes de computação distribuída.

PADE é escrito 100% em Python e utiliza as bibliotecas do projeto `Twisted <http://twistedmatrix.com/>`_ para implementar a comunicação entre os nós da rede.

PADE é software livre, licenciado sob os termos da licença MIT, desenvolvido no ambito da Universidade Federal do Ceará pelo Grupo de Redes Elétricas Inteligentes (GREI) que pertence ao departamento de Engenharia Elétrica.

Qualquer um que queira contribuir com o projeto é convidado a baixar, executar, testar e enviar feedback a respeito das impressões tiradas da plataforma. 

PADE é simples!
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

Funcionalidades
~~~~~~~~~~~~~~~

O PADE foi desenvolvido tendo em vista os requisitos para sistema de automação. PADE oferece os seguintes recursos em sua biblioteca para desenvolvimento de sistemas multiagentes:


**Orientação a Objetos**
  Abstração para construção de agentes e seus comportamentos utilizando conceitos de orientação a objetos;

**Ambiente de execução**
  Módulo para inicialização do ambiente de execução de agentes, inteiramente em código Python;

**Mensagens no padrão FIPA-ACL**
  Módulo para construção e tratamento de mensagens no padrão FIPA-ACL;

**Filtragem de Mensagens**
  Módulo para filtragem de mensagens;

**Protocolos FIPA**
  Módulo para a implementação dos protocolos definidos pela FIPA;

**Comportamentos Cíclicos e Temporais**
  Módulo para implementação de comportamentos cíclicos e temporais;

**Banco de Dados**
  Módulo para interação com banco de dados;

**Envio de Objetos Serializados**
  Possibilidade de envio de objetos serializados como conteúdo das mensagens FIPA-ACL.


Além dessas funcionalidades, o PADE é de fácil instalação e configuração, multiplataforma, podendo ser instalado e utilizado em hardwares embarcados que executam sistema operacional Linux, como Raspberry Pi e BeagleBone Black, bem como sistema operacional Windows.



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


