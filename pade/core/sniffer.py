from pade.core.agent import Agent
from pade.acl.aid import AID
from pade.misc.utility import display_message, start_loop

from pade.web import flask_server
from pade.web.flask_server import AgentModel


from alchimia import wrap_engine
from twisted.internet.defer import inlineCallbacks
from twisted.internet import reactor
from sqlalchemy import create_engine, MetaData, Table

from pickle import loads, dumps
import random
import os

basedir = os.path.abspath(os.path.dirname(flask_server.__file__))

ENGINE = create_engine('sqlite:///{}/data.sqlite'.format(basedir))
TWISTED_ENGINE = wrap_engine(reactor, ENGINE)
TWISTED_ENGINE.run_callable = ENGINE.run_callable

METADATA = MetaData()
METADATA.bind = ENGINE
MESSAGES = Table('messages', METADATA, autoload=True, autoload_with=ENGINE)
AGENTS = Table('agents', METADATA, autoload=True, autoload_with=ENGINE)

class Sniffer(Agent):
    """This is the class that implements the AMS agent."""

    def __init__(self, host='localhost', port=8001, debug=False):
        self.sniffer_aid = AID('sniffer@' + str(host) + ':' + str(port))
        super(Sniffer, self).__init__(self.sniffer_aid, debug=debug)
        self.sniffer = {'name':str(host),'port':str(port)}      
        self.host = host
        self.port = port
        self.messages_buffer = dict()
        self.buffer_control = True
        self.agent_db_id = dict()

    def handle_store_messages(self):
        for sender, messages in self.messages_buffer.items():
            if self.agent_db_id.get(sender) == None:
                r = ENGINE.execute(AGENTS.select(AGENTS.c.name.is_(sender)))
                a = r.fetchall()
                if a != []:
                    agent_id = a[0][0]
                    self.agent_db_id[sender] = agent_id
                else:
                    print('Agent does not exist in database: {}'.format(sender))
                r.close()
            else:
                pass

            for message in messages:
                receivers = list()
                for receiver in message.receivers:
                    receivers.append(receiver.localname)

                insert_obj = MESSAGES.insert()
                sql_act = insert_obj.values(agent_id=self.agent_db_id[sender],
                                            sender=message.sender.name,
                                            date=message.datetime,
                                            performative=message.performative,
                                            protocol=message.protocol,
                                            content=message.content,
                                            conversation_id=message.conversationID,
                                            message_id=message.messageID,
                                            ontology=message.ontology,
                                            language=message.language,
                                            receivers=dumps(receivers))

                #reactor.callInThread(ENGINE.execute, sql_act)
                reactor.callLater(random.uniform(0.1, 0.5), self.register_message_in_db, sql_act)

                if self.debug:
                    display_message(self.aid.name, 'Message stored')

        self.messages_buffer = dict()
        self.buffer_control = True

    @inlineCallbacks
    def register_message_in_db(self, sql_act):
        yield TWISTED_ENGINE.execute(sql_act)

    def react(self, message):
        super(Sniffer, self).react(message)
        if 'ams' not in message.sender.name:
            content = loads(message.content)
            if content['ref'] == 'MESSAGE':
                _message = content['message']
                if self.messages_buffer.get(message.sender.name) == None:
                    self.messages_buffer[message.sender.name] = [_message]
                else:
                    messages = self.messages_buffer[message.sender.name]
                    messages.append(_message) 

                if self.buffer_control:
                    reactor.callLater(5.0, self.handle_store_messages)
                    self.buffer_control = False

if __name__ == '__main__':
    sniffer = Sniffer()
    start_loop([sniffer])
