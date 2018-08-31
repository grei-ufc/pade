#from pade.misc.common import start_loop, 
from pade.misc.common import PadeSession
from pade.misc.utility import display_message, call_in_thread

from pade.core.agent import Agent
from pade.acl.aid import AID
from pade.acl.messages import ACLMessage
from pade.behaviours.protocols import FipaSubscribeProtocol, TimedBehaviour

import random
import time

def my_time(a, b):
    print('------> I will sleep now!', a)
    time.sleep(10)
    print('------> I wake up now!', b)

class SubscribeInitiator(FipaSubscribeProtocol):

    def __init__(self, agent, message):
        super(SubscribeInitiator, self).__init__(agent,
                                                 message,
                                                 is_initiator=True)

    def handle_agree(self, message):
        display_message(self.agent.aid.name, message.content)

    def handle_inform(self, message):
        display_message(self.agent.aid.name, message.content)


class SubscribeParticipant(FipaSubscribeProtocol):

    def __init__(self, agent):
        super(SubscribeParticipant, self).__init__(agent,
                                                   message=None,
                                                   is_initiator=False)

    def handle_subscribe(self, message):
        self.register(message.sender)
        display_message(self.agent.aid.name, message.content)
        resposta = message.create_reply()
        resposta.set_performative(ACLMessage.AGREE)
        resposta.set_content('Subscribe message accepted')
        self.agent.send(resposta)

    def handle_cancel(self, message):
        self.deregister(self, message.sender)
        display_message(self.agent.aid.name, message.content)

    def notify(self, message):
        super(SubscribeParticipant, self).notify(message)


class Time(TimedBehaviour):

    def __init__(self, agent, notify):
        super(Time, self).__init__(agent, 1)
        self.notify = notify
        self.inc = 0

    def on_time(self):
        super(Time, self).on_time()
        message = ACLMessage(ACLMessage.INFORM)
        message.set_protocol(ACLMessage.FIPA_SUBSCRIBE_PROTOCOL)
        message.set_content(str(random.random()))
        self.notify(message)
        self.inc += 0.1


class AgentInitiator(Agent):

    def __init__(self, aid, message):
        super(AgentInitiator, self).__init__(aid)
        self.protocol = SubscribeInitiator(self, message)
        self.behaviours.append(self.protocol)


class AgentParticipant(Agent):

    def __init__(self, aid):
        super(AgentParticipant, self).__init__(aid)

        self.protocol = SubscribeParticipant(self)
        self.timed = Time(self, self.protocol.notify)

        self.behaviours.append(self.protocol)
        self.behaviours.append(self.timed)

        call_in_thread(my_time, 'a', 'b')

if __name__ == '__main__':

    editor = AgentParticipant(AID('editor'))

    msg = ACLMessage(ACLMessage.SUBSCRIBE)
    msg.set_protocol(ACLMessage.FIPA_SUBSCRIBE_PROTOCOL)
    msg.set_content('Subscription request')
    msg.add_receiver(editor.aid)

    subs1 = AgentInitiator(AID('subscriber_1'), msg)
   # subs1.ams = {'name': 'localhost', 'port': 5000}

    subs2 = AgentInitiator(AID('subscriber_2'), msg)
   #subs2.ams = {'name': 'localhost', 'port': 5000}

    agents = [editor, subs1, subs2]

    s = PadeSession()
    s.add_all_agents(agents)
    s.register_user(username='lucassm',
                    email='lucas@gmail.com',
                    password='12345')
    s.start_loop(debug=True)
