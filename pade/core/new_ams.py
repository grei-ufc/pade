"""Framework for Intelligent Agents Development - PADE

The MIT License (MIT)

Copyright (c) 2019 Lucas S Melo

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""
from pade.core.agent import Agent_
from pade.acl.messages import ACLMessage
from pade.acl.aid import AID
from pade.behaviours.protocols import TimedBehaviour, FipaRequestProtocol, FipaSubscribeProtocol
from pade.misc.utility import display_message

from pade.web import flask_server
from pade.web.flask_server import db, Session, User, basedir

from pickle import dumps, loads
from datetime import datetime
import uuid
from terminaltables import AsciiTable

from alchimia import wrap_engine
from sqlalchemy import create_engine, Table, MetaData

from twisted.internet.defer import inlineCallbacks
from twisted.internet import reactor

import random
import os
import sys

# Behaviour that sends the connection verification messages.

class ComportSendConnMessages(TimedBehaviour):
    def __init__(self, agent, message, time):
        super(ComportSendConnMessages, self).__init__(agent, time)
        self.message = message

    def on_time(self):
        super(ComportSendConnMessages, self).on_time()
        self.agent.add_all(self.message)
        self.agent.send(self.message)
        if self.agent.debug:
            display_message(self.agent.aid.name, 'Checking connection...')

# Behaviour that verifies the answer time of the agents
# and decides whether to disconnect them or not.

class ComportVerifyConnTimed(TimedBehaviour):
    def __init__(self, agent, time):
        super(ComportVerifyConnTimed, self).__init__(agent, time)

    def on_time(self):
        super(ComportVerifyConnTimed, self).on_time()
        desconnect_agents = list()
        table = list([['agent', 'delta']])
        for agent_name, date in self.agent.agents_conn_time.items():
            now = datetime.now()
            delta = now - date
            table.append([agent_name, str(delta.total_seconds())])
            if delta.total_seconds() > 20.0:
                desconnect_agents.append(agent_name)
                self.agent.agentInstance.table.pop(agent_name)
                display_message(self.agent.aid.name, 'Agent {} disconnected.'.format(agent_name))    

        for agent_name in desconnect_agents:
            self.agent.agents_conn_time.pop(agent_name)

        if self.agent.debug:
            display_message(self.agent.aid.name, 'Calculating response time of the agents...')
            table = AsciiTable(table)
            print(table.table)


class CompConnectionVerify(FipaRequestProtocol):
    """FIPA Request Behaviour of the Clock agent.
    """
    def __init__(self, agent, message):
        super(CompConnectionVerify, self).__init__(agent=agent,
                                           message=message,
                                           is_initiator=True)
        

    def handle_inform(self, message):
        # if self.agent.debug:
        #     display_message(self.agent.aid.localname, message.content)
        date = datetime.now()
        self.agent.agents_conn_time[message.sender.name] = date


class PublisherBehaviour(FipaSubscribeProtocol):
    """
    FipaSubscribe behaviour of Publisher type that implements
    a publisher-subscriber communication, which has the AMS agent
    as the publisher and the agents of the plataform as subscribers.
    Two procedures are implemented in this behaviour:
        - The first one is the identification procedure, which
          verifies the availability in the database and stores it
          if positive.
        - The second one is the updating procedure, which updates the
          distributed tables that contain the adresses of the agents 
          in the pleteform. It is updated every time that an agent 
          enters or leaves the network."""

    STATE = 0

    def __init__(self, agent):
        super(PublisherBehaviour, self).__init__(agent,
                                                 message=None,
                                                 is_initiator=False)

    def handle_subscribe(self, message):

        sender = message.sender

        if sender in self.agent.agentInstance.table.values():
            display_message(self.agent.aid.name,
                            'Failure when Identifying agent ' + sender.name)

            # prepares the answer message
            reply = message.create_reply()
            reply.set_content(
                'There is already an agent with this identifier. Please, choose another one.')
            # sends the message
            self.agent.send(reply)
        else:
            # registers the agent in the database.

            insert_obj = AGENTS.insert()
            sql_act = insert_obj.values(name=sender.name,
                                        session_id=self.agent.session.id,
                                        date=datetime.now(),
                                        state='Active')

            reactor.callLater(random.uniform(0.1, 0.5), self.register_agent_in_db, sql_act)

            # registers the agent in the table of agents
            self.agent.agentInstance.table[sender.name] = sender
            # registers the agent as a subscriber in the protocol.
            self.register(message.sender)
            # registers the agent in the table of time.
            self.agent.agents_conn_time[message.sender.name] = datetime.now()

            display_message(
                self.agent.aid.name, 'Agent ' + sender.name + ' successfully identified.')

            # prepares and sends answer messages to the agent
            reply = message.create_reply()
            reply.set_performative(ACLMessage.AGREE)
            reply.set_content(
                'Agent successfully identified.')
            self.agent.send(reply)

            # prepares and sends the update message to
            # all registered agents.
            if self.STATE == 0:
                reactor.callLater(10.0, self.notify)
                self.STATE = 1

    @inlineCallbacks
    def register_agent_in_db(self, sql_act):
        yield TWISTED_ENGINE.execute(sql_act)

    def handle_cancel(self, message):
        self.deregister(self, message.sender)
        display_message(self.agent.aid.name, message.content)

    def notify(self):
        message = ACLMessage(ACLMessage.INFORM)
        message.set_protocol(ACLMessage.FIPA_SUBSCRIBE_PROTOCOL)
        message.set_content(dumps(self.agent.agentInstance.table))
        message.set_system_message(is_system_message=True)
        self.STATE = 0
        super(PublisherBehaviour, self).notify(message)


class CompVerifyRegister(FipaRequestProtocol):
    def __init__(self, agent):
        """FIPA Request Behaviour to verify the user 
        registration"""
        super(CompVerifyRegister, self).__init__(agent=agent,
                                                 message=None,
                                                 is_initiator=False)

    def handle_request(self, message):
        super(CompVerifyRegister, self).handle_request(message)
        content = loads(message.content)
        display_message(self.agent.aid.name,
                        'Validating agent ' + message.sender.name + ' session.')
        if type(content) == dict:
            if content['ref'] == "REGISTER":
                user_login = content['content']['user_login']
                session_name = content['content']['session_name']

                # procedure to verify session user and data
                # of the requested session.

                # searches in the database if there is a session with this name.
                session = Session.query.filter_by(name=session_name).first()
                if session is None:
                    reply = message.create_reply()
                    reply.set_performative(ACLMessage.INFORM)
                    reply.set_content(dumps({'ref': 'REGISTER',
                                             'content': False}))
                    self.agent.call_later(1.0, self.agent.send, reply)
                else:
                    # verifies if the user is logged in the session.
                    users = session.users
                    for user in users:
                        if user.username == user_login['username']:
                            if user.verify_password(user_login['password']):
                                validation = True
                                display_message(self.agent.aid.name,
                                                'Session successfully validated.')
                                break
                            else:
                                validation = False
                                display_message(self.agent.aid.name,
                                                'Session not validated -> Incorrect password.')
                                break
                    else:
                        display_message(self.agent.aid.name,
                                        'Session not validated -> Incorrect password.')
                        validation = False

                    reply = message.create_reply()
                    reply.set_performative(ACLMessage.INFORM)
                    reply.set_content(dumps({'ref': 'REGISTER',
                                             'content': validation}))
                    self.agent.send(reply)

class AMS(Agent_):
    """This is the class that implements the AMS agent."""

    agents = list()
    users = list()
    user_login = dict()
    ams_debug = False

    def __init__(self, host='localhost', port=8000, main_ams=True, debug=False):

        self.session_name = str(uuid.uuid1())[:13]
        self.ams = {'name': host, 'port': port}

        self.ams_aid = AID('ams@' + str(host) + ':' + str(port))
        super(AMS, self).__init__(self.ams_aid, debug=debug)
        self.ams = {'name':str(host),'port':str(port)}
        super(AMS, self).update_ams(self.ams)      
        self.host = host
        self.port = port
        self.main_ams = main_ams

        self.agents_conn_time = dict()
        self.comport_ident = PublisherBehaviour(self)

        # message to check the connection.
        message = ACLMessage(ACLMessage.REQUEST)
        message.set_protocol(ACLMessage.FIPA_REQUEST_PROTOCOL)
        self.add_all(message)
        message.set_content('CONNECTION')
        message.set_system_message(is_system_message=True)

        self.comport_conn_verify = CompConnectionVerify(self, message)
        self.comport_send_conn_messages = ComportSendConnMessages(self, message, 10.0)
        self.comport_conn_verify_timed = ComportVerifyConnTimed(self, 20.0)
        self.comport_conn_verify_reg = CompVerifyRegister(self)

        self.system_behaviours.append(self.comport_ident)
        self.system_behaviours.append(self.comport_conn_verify)
        self.system_behaviours.append(self.comport_send_conn_messages)
        self.system_behaviours.append(self.comport_conn_verify_timed)
        self.system_behaviours.append(self.comport_conn_verify_reg)
        self.on_start()

    def react(self, message):
        super(AMS, self).react(message)

    def register_user(self, username, email, password):
        self.users.append(
            {'username': username, 'email': email, 'password': password})

    def _initialize_database(self):
        db.create_all()
        # searches in the database if there is a session with 
        # this name
        self.session = Session.query.filter_by(name=self.session_name).first()

        # in case there is not a session with this name
        if self.session is None:
            # clear out the database and creates new registers
            db.drop_all()
            db.create_all()

            # registers a new session in the database
            self.session = Session(name=self.session_name,
                                 date=datetime.now(),
                                 state='Active')
            db.session.add(self.session)
            db.session.commit()

            reactor.listenTCP(self.aid.port, self.agentInstance)

            # registers the users, in case they exist, in the database

            if len(self.users) != 0:
                users_db = list()
                for user in self.users:
                    u = User(username=user['username'],
                             email=user['email'],
                             password=user['password'],
                             session_id=self.session.id)
                    users_db.append(u)

                db.session.add_all(users_db)
                db.session.commit()

        # in case there is a session with this name
        else:
            self._verify_user_in_session(self.session)

if __name__ == '__main__':

    display_message('AMS', 'creating tables in database...')
    db.create_all()
    display_message('AMS', 'tables created in database.')

    ENGINE = create_engine('sqlite:///' + os.path.join(basedir, 'data.sqlite'))
    TWISTED_ENGINE = wrap_engine(reactor, ENGINE)
    TWISTED_ENGINE.run_callable = ENGINE.run_callable

    METADATA = MetaData()
    METADATA.bind = ENGINE
    AGENTS = Table('agents', METADATA, autoload=True, autoload_with=ENGINE)
    
    ams = AMS(port=int(sys.argv[4]))
    # instantiates AMS agent and calls listenTCP method
    # from Twisted to launch the agent
    ams_agent = AMS() # TODO: precisa implementar a passagem de parametros
    ams.register_user(username=sys.argv[1],
                      email=sys.argv[2],
                      password=sys.argv[3])
    ams._initialize_database()
    reactor.callLater(0.1,
                      display_message,
                      'ams@{}:{}'.format(ams.ams['name'], ams.ams['port']),
                      'PADE AMS service running right now....')
    reactor.run()