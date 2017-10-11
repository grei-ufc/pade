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

from twisted.internet import reactor

from pade.web.flask_server import run_server, db
from pade.web.flask_server import Session, Agent, User

from pade.core.new_ams import AMS

import multiprocessing
import uuid
import datetime
import json
import subprocess


class FlaskServerProcess(multiprocessing.Process):
    """
        Esta classe implementa a thread que executa
        o servidor web com o aplicativo Flask
    """
    def __init__(self):
        multiprocessing.Process.__init__(self)

    def run(self):
        run_server()


class PSession(object):

    agents = list()
    users = list()
    user_login = dict()

    def __init__(self, name=None, ams=None):
        if name is not None:
            self.name = name
        else:
            self.name = str(uuid.uuid1())[:13]

        if ams is not None:
            self.ams = ams
        else:
            self.ams = {'name': 'localhost', 'port': 8000}

    def add_agent(self, agent):
        agent.ams = self.ams
        self.agents.append(agent)

    def add_all_agents(self, agents):
        for agent in agents:
            agent.ams = self.ams
        self.agents = self.agents + agents

    def register_user(self, username, email, password):
        self.users.append(
            {'username': username, 'email': email, 'password': password})

    def log_user_in_session(self, username, email, password):
        self.user_login['username'] = username
        self.user_login['email'] = email
        self.user_login['password'] = password


def verifica_ip(ip):
    output = subprocess.check_output('ifconfig', shell=True)
    interfaces = output.split('\n\n')
    for interface in interfaces:
        if str(ip + ' ') in interface:
            interface_name = interface.split(' ')[0]
            break
    else:
        return (False, None)
    return (True, interface_name)


def start_loop(session_, debug=False):
    """
        Lança o loop do twisted integrado com o loop do Qt se a opção GUI for
        verdadeira, se não lança o loop do Twisted
    """

    # pesquisa no banco de dados se existe uma sessao com este nome
    session = Session.query.filter_by(name=session_.name).first()

    # caso nao exista uma sessao com este nome
    if session is None:

        # instancia a classe que lança o processo
        # com o servidor web com o aplicativo Flask
        p1 = FlaskServerProcess()
        p1.daemon = True

        p1.start()

        # limpa o banco de dados e cria novos registros
        db.drop_all()
        db.create_all()

        # registra uma nova sessão no banco de dados
        s = Session(name=session_.name,
                    date=datetime.datetime.now(),
                    state='Ativo')
        db.session.add(s)
        db.session.commit()

        # instancia o agente AMS e chama o metodo listenTCP
        # do Twisted para lancar o agente
        ams_agent = AMS(host=session_.ams['name'],
                        port=session_.ams['port'],
                        session=s)
        reactor.listenTCP(ams_agent.aid.port, ams_agent.agentInstance)

        # registra os usuarios, se houverem, no banco de dados
        if len(session_.users) != 0:
            users_db = list()
            for user in session_.users:
                u = User(username=user['username'],
                         email=user['email'],
                         password=user['password'],
                         session_id=s.id)
                users_db.append(u)

            db.session.add_all(users_db)
            db.session.commit()

    # caso exista uma sessao com este nome
    else:
        s = session
        # caso seja uma sessao ativa
        if s.state == 'Ativo':
            users = s.users
            # percorre os usuarios cadastrados no banco de dados
            for user in users:
                if user.username == session_.user_login['username']:
                    if user.verify_password(session_.user_login['password']):
                        break
                    else:
                        raise UserWarning('The password is wrong!')
            else:
                raise UserWarning('The username is wrong!')
        # caso nao seja uma sessao ativa
        else:
            raise UserWarning('This session name has been used before, please, choose another!')

    i = 1
    for agent in session_.agents:
        reactor.callLater(i, listen_agent, agent)
        i += 0.2

    # lança o loop do Twisted
    reactor.run()


def listen_agent(agent):
    # Conecta o agente ao AMS
    agent.on_start()
    # Conecta o agente à porta que será utilizada para comunicação
    reactor.listenTCP(agent.aid.port, agent.agentInstance)
