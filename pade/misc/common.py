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
from pade.core.sniffer import SnifferFactory

from pade.web.flask_server import app, db
from pade.web.flask_server import Session, Agent

import optparse
import multiprocessing
import uuid
import datetime

AMS = {'name': 'localhost', 'port': 8000}


class FlaskServerProcess(multiprocessing.Process):
    """
        Esta classe implementa a thread que executa
        o servidor web com o aplicativo Flask
    """
    def __init__(self, app):
        multiprocessing.Process.__init__(self)
        self.app = app

    def run(self):
        self.app.run(host='0.0.0.0', port=5000, debug=None)


# =========================================================================
# Metodos Utilitarios
# =========================================================================

def set_ams(name, port, debug=False):
    """
        Metodo utilizado na inicialização do laço de execução do AMS
    """
    global AMS

    AMS = {'name': name, 'port': port}

    amsFactory = AgentManagementFactory(port, debug)
    twisted.internet.reactor.listenTCP(port, amsFactory)

def start_loop(agents):
    """
        Lança o loop do twisted integrado com o loop do Qt se a opção GUI for
        verdadeira, se não lança o loop do Twisted
    """
    global AMS

    # instancia um AID para o agente Sniffer
    # aid = AID('Sniffer_Agent')
    # instancia um objeto Factory para o agente Sniffer
    # snifferFactory = SnifferFactory(aid, AMS)
    # lança o agente como servidor na porta gerada pelo objeto AID
    # twisted.internet.reactor.listenTCP(aid.port, snifferFactory)

    # instancia a classe que lança o processo
    # com o servidor web com o aplicativo Flask
    p1 = FlaskServerProcess(app)
    p1.daemon = True

    p1.start()

    db.drop_all()
    db.create_all()

    s = Session(name=str(uuid.uuid1())[:13], date=datetime.datetime.now(), state = 'Ativo')
    db.session.add(s)
    db.session.commit()

    i = 1
    agents_db = list()
    for agent in agents:
        twisted.internet.reactor.callLater(i, listen_agent, agent)
        a = Agent(name=agent.aid.localname, session_id=s.id, date=datetime.datetime.now(), state = 'Ativo')
        agents_db.append(a)
        i += 0.2
    db.session.add_all(agents_db)
    db.session.commit()

    # lança o loop do Twisted
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

if __name__ == '__main__':
    main()
