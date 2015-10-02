#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Framework para Desenvolvimento de Agentes Inteligentes PADE

# The MIT License (MIT)

# Copyright (c) 2015 Lucas S Melo

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

"""
 Módulo de Utilidades
 --------------------

 Este módulo Python disponibiliza métodos de configuração
 do loop twisted onde os agentes serão executados e caso se utilize
 interface gráfica, é neste módulo que o loop Qt4 é integrado ao 
 loop Twisted, além de disponibilizar métodos para lançamento do AMS
 e Sniffer por linha de comando e para exibição de informações no 
 terminal

 @author: lucas
"""

import twisted.internet
from pade.acl.aid import AID
from pade.core.ams import AgentManagementFactory

import optparse

# =========================================================================
# Metodos Utilitarios
# =========================================================================

AMS = {'name': 'localhost', 'port': 8000}


def set_ams(name, port, debug=False):
    """
        Metodo utilizado na inicialização do laço de execução do AMS 
    """
    global AMS

    AMS = {'name': name, 'port': port}

    amsFactory = AgentManagementFactory(port, debug)
    twisted.internet.reactor.listenTCP(port, amsFactory)


def start_loop(agents, gui=False):
    """
        Lança o loop do twisted integrado com o loop do Qt se a opção GUI for
        verdadeira, se não lança o loop do Twisted
    """
    global AMS

    if gui:
        from pade.core.sniffer import SnifferFactory
        from pade.gui.interface import ControlAgentsGui

        controlAgentsGui = ControlAgentsGui()
        controlAgentsGui.show()

        # instancia um AID para o agente Sniffer
        aid = AID('Sniffer_Agent')
        # instancia um objeto Factory para o agente Sniffer
        snifferFactory = SnifferFactory(aid, AMS, controlAgentsGui.ui)
        # lança o agente como servidor na porta gerada pelo objeto AID
        twisted.internet.reactor.listenTCP(aid.port, snifferFactory)

    i = 1
    for agent in agents:
        twisted.internet.reactor.callLater(i, listen_agent, agent)
        i += 0.2

    # lança o loop do Twisted
    # twisted.internet.reactor.startRunning(init)
    twisted.internet.reactor.run()


def listen_agent(agent):
    # Conecta o agente ao AMS
    twisted.internet.reactor.connectTCP(
        agent.ams['name'], agent.ams['port'], agent.agentInstance)
    # Conecta o agente à porta que será utilizada para comunicação
    twisted.internet.reactor.listenTCP(agent.aid.port, agent.agentInstance)


def main():
    p = optparse.OptionParser()
    p.add_option('--port', '-p', default=8000)
    p.add_option('--gui', '-g', default=False)
    options, arguments = p.parse_args()

    set_ams('localhost', port=int(options.port))
    start_loop(agents=[], gui=True)

if __name__ == '__main__':
    main()
