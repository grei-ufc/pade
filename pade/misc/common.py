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
from pade.web.flask_server import Session, AgentModel, User

from pade.core.new_ams import AMS
from pade.core.agent import Agent
from pade.acl.aid import AID
from pade.acl.messages import ACLMessage
from pade.behaviours.protocols import FipaRequestProtocol

import multiprocessing
import uuid
import datetime
from pickle import dumps, loads

class FlaskServerProcess(multiprocessing.Process):
    """
        Esta classe implementa a thread que executa
        o servidor web com o aplicativo Flask
    """
    def __init__(self):
        multiprocessing.Process.__init__(self)

    def run(self):
        run_server()


class PadeSession(object):

    agents = list()
    users = list()
    user_login = dict()

    def __init__(self, name=None, ams=None, remote_ams=False):
        
        self.remote_ams = remote_ams

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


    def _verifica_sessao_remota(self):
        vua_aid = AID('valid_user_agent')
        vua_aid.setHost(self.agents[0].aid.host)
        valid_user_agent = ValidadeUserAgent(vua_aid,
                                             self.user_login,
                                             self.name)
        reactor.callLater(1.0, self._listen_agent, valid_user_agent)
        reactor.run()

    def _verifica_usuario_na_sessao(self, db_session):
        # caso seja uma sessao ativa
        if db_session.state == 'Ativo':
            users = db_session.users
            # percorre os usuarios cadastrados no banco de dados
            for user in users:
                if user.username == self.user_login['username']:
                    if user.verify_password(self.user_login['password']):
                        break
                    else:
                        raise UserWarning('The password is wrong!')
            else:
                raise UserWarning('The username is wrong!')
        # caso nao seja uma sessao ativa
        else:
            raise UserWarning('This session name has been used before, please, choose another!')

    def _inicializa_banco_de_dados(self):

        db.create_all()
        # pesquisa no banco de dados se existe uma sessao 
        # com este nome
        db_session = Session.query.filter_by(name=self.name).first()

        # caso nao exista uma sessao com este nome
        if db_session is None:

            # limpa o banco de dados e cria novos registros
            db.drop_all()
            db.create_all()

            # registra uma nova sessão no banco de dados
            db_session = Session(name=self.name,
                                 date=datetime.datetime.now(),
                                 state='Ativo')
            db.session.add(db_session)
            db.session.commit()

            # instancia o agente AMS e chama o metodo listenTCP
            # do Twisted para lancar o agente
            ams_agent = AMS(host=self.ams['name'],
                            port=self.ams['port'],
                            session=db_session)
            reactor.listenTCP(ams_agent.aid.port, ams_agent.agentInstance)

            # registra os usuarios, se houverem, no banco de dados
            if len(self.users) != 0:
                users_db = list()
                for user in self.users:
                    u = User(username=user['username'],
                             email=user['email'],
                             password=user['password'],
                             session_id=db_session.id)
                    users_db.append(u)

                db.session.add_all(users_db)
                db.session.commit()

        # caso exista uma sessao com este nome
        else:
            self._verifica_usuario_na_sessao(db_session)

    def start_loop(self, debug=False):
        """
            Lança o loop do twisted
        """
        if self.remote_ams:
            
            self._verifica_sessao_remota()
            
        else:

            # instancia a classe que lança o processo
            # com o servidor web com o aplicativo Flask
            p1 = FlaskServerProcess()
            p1.daemon = True

            p1.start()

            # verifica sessao no banco de dados.
            # Se nao for uma sessao existente
            # cria uma, inicializa o AMS e 
            # cadastra os usuarios da sessao.
            # Caso seja uma sessao existente
            # verifica o usuario que pretente
            # fazer login na sessao. 
            # 
            self._inicializa_banco_de_dados()

            i = 1.0
            for agent in self.agents:
                reactor.callLater(i, self._listen_agent, agent)
                i += 0.2

            # lança o loop do Twisted
            reactor.run()

    def _listen_agent(self, agent):
        # Conecta o agente ao AMS
        agent.on_start()
        # Conecta o agente à porta que será utilizada para comunicação
        reactor.listenTCP(agent.aid.port, agent.agentInstance)


class CompRegisterUser(FipaRequestProtocol):
    """Comportamento FIPA Request para
    registro de usuario"""
    def __init__(self, agent, message):
        super(CompRegisterUser, self).__init__(agent=agent,
                                               message=message,
                                               is_initiator=True)
        

    def handle_inform(self, message):
        super(CompRegisterUser, self).handle_inform(message)
        content = loads(message.content)
        if type(content) == dict:
            if content['ref'] == "REGISTER":
                user_login = content['content']
                print user_login
                if user_login:
                    reactor.stop()
                else:
                    reactor.stop()
                    raise Exception('Falha na autenticacao do usuario')
                    


class ValidadeUserAgent(Agent):

    def __init__(self, aid, user_login, session_name):
        super(ValidadeUserAgent, self).__init__(aid=aid, debug=True)
        self.user_login = user_login
        self.session_name = session_name
        message = ACLMessage(ACLMessage.REQUEST)
        message.set_protocol(ACLMessage.FIPA_REQUEST_PROTOCOL)
        content = dumps({
        'ref': 'REGISTER',
        'content': {'user_login': self.user_login, 'session_name': self.session_name}})
        message.set_content(content)
        ams_aid = AID('ams@' + self.ams['name'] + ':' + str(self.ams['port']))
        message.add_receiver(ams_aid)
        message.set_system_message(is_system_message=True)
        self.comport_register_user = CompRegisterUser(self, message)

        self.system_behaviours.append(self.comport_register_user)

    def react(self, message):
        super(ValidadeUserAgent, self).react(message)


# def verifica_ip(ip):
#     output = subprocess.check_output('ifconfig', shell=True)
#     interfaces = output.split('\n\n')
#     for interface in interfaces:
#         if str(ip + ' ') in interface:
#             interface_name = interface.split(' ')[0]
#             break
#     else:
#         return (False, None)
#     return (True, interface_name)
