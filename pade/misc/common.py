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

"""
 Utility Module
 --------------------

 This Python module provides configuration methods of twisted loop
 where the agents will be executed. This module integrates Qt4 loop
 and twisted loop in case the graphic interface is used. Furthermore,
 this module provoides methods to launch AMS and Sniffer by command line
 and methods for displaying information on terminal.
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
import threading
import uuid
import datetime
from pickle import dumps, loads

class FlaskServerProcess(multiprocessing.Process):
    """
        This class implements the thread that executes
        the web server with Flask application.
    """
    def __init__(self):
        multiprocessing.Process.__init__(self)

    def run(self):
        run_server()

class PadeSession(object):

    agents = list()
    users = list()
    user_login = dict()
    ams_debug = False

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
        self.agents.append(agent)

    def add_all_agents(self, agents):
        self.agents = self.agents + agents

    def register_user(self, username, email, password):
        self.users.append(
            {'username': username, 'email': email, 'password': password})

    def log_user_in_session(self, username, email, password):
        self.user_login['username'] = username
        self.user_login['email'] = email
        self.user_login['password'] = password

    def _verify_remote_session(self):
        vua_aid = AID('valid_user_agent')
        vua_aid.setPort(self.agents[0].aid.port)
        vua_aid.setHost(self.agents[0].aid.host)
        valid_user_agent = ValidadeUserAgent(vua_aid,
                                             self.user_login,
                                             self.name,
                                             self)
        reactor.callLater(1.0, self._listen_agent, valid_user_agent)
        reactor.run()

    def _verify_user_in_session(self, db_session):
        # in case it is an active session
        if db_session.state == 'Active':
            users = db_session.users
            print(users)
            # iterates through registered users in the database.S
            for user in users:
                if user.username == self.user_login['username']:
                    if user.verify_password(self.user_login['password']):
                        break
                    else:
                        raise UserWarning('The password is wrong!')
            else:
                raise UserWarning('The username is wrong!')
        # in case it is not an active session
        else:
            raise UserWarning('This session name has been used before. Please, choose another!')

    def _initialize_database(self):
        db.create_all()
        # searches in the database if there is a session with 
        # this name
        db_session = Session.query.filter_by(name=self.name).first()

        # in case there is not a session with this name
        if db_session is None:
            # clear out the database and creates new registers
            db.drop_all()
            db.create_all()

            # registers a new session in the database
            db_session = Session(name=self.name,
                                 date=datetime.datetime.now(),
                                 state='Active')
            db.session.add(db_session)
            db.session.commit()

            # instantiates AMS agent and calls listenTCP method
            # from Twisted to launch the agent
            ams_agent = AMS(host=self.ams['name'],
                            port=self.ams['port'],
                            session=db_session,
                            debug=self.ams_debug)
            reactor.listenTCP(ams_agent.aid.port, ams_agent.agentInstance)

            # registers the users, in case they exist, in the database

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

        # in case there is a session with this name
        else:

            self._verify_user_in_session(db_session)

    def start_loop(self, ams_debug=False, multithreading=False):
        """
            Runs twisted loop
        """
        self.ams_debug = ams_debug

        if self.remote_ams:
            self._verify_remote_session()
            
        else:

            # instantiates the class responsible for launching the web
            # server process with the Flask application
            p1 = FlaskServerProcess()
            p1.daemon = True

            p1.start()

            # verifies the session in the database.
            # If there is not a session, one is created,
            # the AMS is initialized, and the 
            # users are registered.
            # If there is an existing session,
            # verifies the user that intends to
            # log in.
            # 
            self._initialize_database()

            i = 1.0
            agents_process = list()
            for agent in self.agents:
                a = AgentProcess(agent, self.ams, i)
                # a.daemon = True
                a.start()
                agents_process.append(a)
                i += 0.1
            print('-----')
            print(reactor)
            reactor.run()


    def __listen_agent(self, agent):
        reactor.callInThread(self._listen_agent, agent)

    def _listen_agent(self, agent):
        # Connects agent to AMS
        agent.update_ams(self.ams)
        agent.on_start()
        # Connects agent to port used in communication
        ILP = reactor.listenTCP(agent.aid.port, agent.agentInstance)
        agent.ILP = ILP

class CompRegisterUser(FipaRequestProtocol):
    """FIPA Request Behaviour to register the user
    uario"""
    def __init__(self, agent, message, session):
        self.session = session
        super(CompRegisterUser, self).__init__(agent=agent,
                                               message=message,
                                               is_initiator=True)
        

    def handle_inform(self, message):
        super(CompRegisterUser, self).handle_inform(message)
        content = loads(message.content)
        if type(content) == dict:
            if content['ref'] == "REGISTER":
                user_login = content['content']
                print(user_login)
                if user_login:
                    i = 1.0
                    for agent in self.session.agents:
                        reactor.callLater(i, self.session._listen_agent, agent)
                        i += 0.2

                    self.agent.pause_agent()

                else:
                    reactor.stop()
                    raise Exception('User authentication failed.')
                    
class ValidadeUserAgent(Agent):

    def __init__(self, aid, user_login, session_name, session):
        super(ValidadeUserAgent, self).__init__(aid=aid, debug=True)
        self.user_login = user_login
        self.session_name = session_name
        self.session= session
        super(ValidadeUserAgent,self).update_ams(session.ams)
        message = ACLMessage(ACLMessage.REQUEST)
        message.set_protocol(ACLMessage.FIPA_REQUEST_PROTOCOL)
        content = dumps({
        'ref': 'REGISTER',
        'content': {'user_login': self.user_login, 'session_name': self.session_name}})
        message.set_content(content)
        ams_aid = AID('ams@' + self.ams['name'] + ':' + str(self.ams['port']))
        message.add_receiver(ams_aid)
        message.set_system_message(is_system_message=True)
        self.comport_register_user = CompRegisterUser(self, message, self.session)
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
