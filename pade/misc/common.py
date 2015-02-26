#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Framework para Desenvolvimento de Agentes Inteligentes KajuPy

# Copyright (C) 2014  Lucas Silveira Melo

# Este arquivo é parte do programa KajuPy
#
# KajuPy é um software livre; você pode redistribuí-lo e/ou 
# modificá-lo dentro dos termos da Licença Pública Geral GNU como 
# publicada pela Fundação do Software Livre (FSF); na versão 3 da 
# Licença, ou (na sua opinião) qualquer versão.
#
# Este programa é distribuído na esperança de que possa ser  útil, 
# mas SEM NENHUMA GARANTIA; sem uma garantia implícita de ADEQUAÇÃO a qualquer
# MERCADO ou APLICAÇÃO EM PARTICULAR. Veja a
# Licença Pública Geral GNU para maiores detalhes.
#
# Você deve ter recebido uma cópia da Licença Pública Geral GNU
# junto com este programa, se não, escreva para a Fundação do Software
# Livre(FSF) Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

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
from pade.core.sniffer import SnifferFactory
from pade.core.ams import AgentManagementFactory
from pade.gui.interface import ControlAgentsGui
import optparse

#=========================================================================
# Metodos Utilitarios
#=========================================================================

AMS = {'name': 'localhost', 'port': 8000}

def set_ams(name, port, debug=False):
    """
        Metodo utilizado na inicialização do laço de execução do AMS 
    """
    global AMS

    AMS = {'name': name, 'port': port}

    amsFactory = AgentManagementFactory(port, debug)
    twisted.internet.reactor.listenTCP(port, amsFactory)

    twisted.internet.reactor.callLater(
        5, amsFactory.protocol.connection_test_send)

def start_loop(agents, gui=False):
    """
        Lança o loop do twisted integrado com o loop do Qt se a opção GUI for
        verdadeira, se não lança o loop do Twisted
    """
    global AMS

    if gui:
        controlAgentsGui = ControlAgentsGui()
        controlAgentsGui.show()

        # instancia um AID para o agente Sniffer
        aid = AID('Sniffer_Agent')
        # instancia um objeto Factory para o agente Sniffer
        snifferFactory = SnifferFactory(aid, AMS, controlAgentsGui.ui)
        # lança o agente como servidor na porta gerada pelo objeto AID
        twisted.internet.reactor.listenTCP(aid.port, snifferFactory)

    i = 0
    for agent in agents:
        i += 1
        twisted.internet.reactor.callLater(i, listen_agent, agent)

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
