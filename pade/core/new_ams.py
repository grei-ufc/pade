from pade.core.agent import Agent_
from pade.acl.messages import ACLMessage
from pade.acl.aid import AID
from pade.behaviours.protocols import TimedBehaviour, FipaRequestProtocol, FipaSubscribeProtocol
from pade.misc.utility import display_message
from pade.acl.filters import Filter
from pade.web.flask_server import db, AgentModel, Message, Session

from pickle import dumps, loads
from datetime import datetime

from terminaltables import AsciiTable

# Behaviour that sends the connection verification messages.

class ComportSendConnMessages(TimedBehaviour):
    def __init__(self, agent, message, time):
        super(ComportSendConnMessages, self).__init__(agent, time)
        self.message = message

    def on_time(self):
        super(ComportSendConnMessages, self).on_time()
        self.agent.add_all(self.message)
        self.agent.send(self.message)
        display_message(self.agent.aid.name, 'Connection...')

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
            if delta.total_seconds() > 30.0:
                desconnect_agents.append(agent_name)
                self.agent.agentInstance.table.pop(agent_name)

        for agent_name in desconnect_agents:
            self.agent.agents_conn_time.pop(agent_name)

        display_message(self.agent.aid.name, 'verifing connections...')
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
        display_message(self.agent.aid.localname, message.content)
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

            a = AgentModel(name=sender.localname,
                      session_id=self.agent.session.id,
                      date=datetime.now(),
                      state='Active')
            db.session.add(a)
            db.session.commit()

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
            message = ACLMessage(ACLMessage.INFORM)
            message.set_protocol(ACLMessage.FIPA_SUBSCRIBE_PROTOCOL)
            message.set_content(dumps(self.agent.agentInstance.table))
            message.set_system_message(is_system_message=True)            
            self.notify(message)

    def handle_cancel(self, message):
        self.deregister(self, message.sender)
        display_message(self.agent.aid.name, message.content)

    def notify(self, message):
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

    def __init__(self, host, port, session, main_ams=True, debug=False):
        self.ams_aid = AID('ams@' + str(host) + ':' + str(port))
        super(AMS, self).__init__(self.ams_aid)
        self.ams = {'name':str(host),'port':str(port)}
        super(AMS,self).update_ams(self.ams)      
        self.host = host
        self.port = port
        self.session = session
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
        self.comport_send_conn_messages = ComportSendConnMessages(self, message, 4.0)
        self.comport_conn_verify_timed = ComportVerifyConnTimed(self, 10.0)
        self.comport_conn_verify_reg = CompVerifyRegister(self)

        self.system_behaviours.append(self.comport_ident)
        self.system_behaviours.append(self.comport_conn_verify)
        self.system_behaviours.append(self.comport_send_conn_messages)
        self.system_behaviours.append(self.comport_conn_verify_timed)
        self.system_behaviours.append(self.comport_conn_verify_reg)
        self.on_start()

    def handle_store_messages(self, message, sender):

        m = Message(sender=message.sender.localname,
                    date=message.datetime,
                    performative=message.performative,
                    protocol=message.protocol,
                    content=message.content,
                    conversation_id=message.conversationID,
                    message_id=message.messageID,
                    ontology=message.ontology,
                    language=message.language)

        receivers = list()
        for receiver in message.receivers:
            receivers.append(receiver.localname)
        m.receivers = receivers

        a = AgentModel.query.filter_by(name=sender.localname).all()[0]
        m.agent_id = a.id

        db.session.add(m)
        db.session.commit()

        display_message(self.aid.name, 'Message stored')

    def react(self, message):
        super(AMS, self).react(message)
        
        try:
            content = loads(message.content)
            if content['ref'] == 'MESSAGE':
                _message = content['message']
                if _message.sender.localname != 'ams':
                    self.handle_store_messages(_message, message.sender)
        except:
            pass

