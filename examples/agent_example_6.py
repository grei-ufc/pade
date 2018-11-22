from pade.misc.utility import display_message, start_loop, call_in_thread
from pade.core.agent import Agent
from pade.acl.aid import AID
from pade.acl.messages import ACLMessage
from pade.behaviours.protocols import FipaSubscribeProtocol, TimedBehaviour
from sys import argv
import random
import time 


def my_time(a, b):
    print('------> I will sleep now!', a)
    time.sleep(10)
    print('------> I wake up now!', b)


class SubscriberProtocol(FipaSubscribeProtocol):

    def __init__(self, agent, message):
        super(SubscriberProtocol, self).__init__(agent,
                                                 message,
                                                 is_initiator=True)

    def handle_agree(self, message):
        display_message(self.agent.aid.name, message.content)

    def handle_inform(self, message):
        display_message(self.agent.aid.name, message.content)


class PublisherProtocol(FipaSubscribeProtocol):

    def __init__(self, agent):
        super(PublisherProtocol, self).__init__(agent,
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
        super(PublisherProtocol, self).notify(message)


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


class AgentSubscriber(Agent):

    def __init__(self, aid, message):
        super(AgentSubscriber, self).__init__(aid)

        self.call_later(8.0, self.launch_subscriber_protocol, message)

    def launch_subscriber_protocol(self, message):
        self.protocol = SubscriberProtocol(self, message)
        self.behaviours.append(self.protocol)
        self.protocol.on_start()


class AgentPublisher(Agent):

    def __init__(self, aid):
        super(AgentPublisher, self).__init__(aid)

        self.protocol = PublisherProtocol(self)
        self.timed = Time(self, self.protocol.notify)

        self.behaviours.append(self.protocol)
        self.behaviours.append(self.timed)

        call_in_thread(my_time, 'a', 'b')

if __name__ == '__main__':

    agents_per_process = 2
    c = 0
    agents = list()
    for i in range(agents_per_process):
        port = int(argv[1]) + c        
        k = 10000
        participants = list()

        agent_name = 'agent_publisher_{}@localhost:{}'.format(port, port)
        participants.append(agent_name)
        agent_pub_1 = AgentPublisher(AID(name=agent_name))
        agents.append(agent_pub_1)

        msg = ACLMessage(ACLMessage.SUBSCRIBE)
        msg.set_protocol(ACLMessage.FIPA_SUBSCRIBE_PROTOCOL)
        msg.set_content('Subscription request')
        msg.add_receiver(agent_pub_1.aid)

        agent_name = 'agent_subscriber_{}@localhost:{}'.format(port + k, port + k)
        participants.append(agent_name)
        agent_sub_1 = AgentSubscriber(AID(name=agent_name), msg)
        agents.append(agent_sub_1)

        agent_name = 'agent_subscriber_{}@localhost:{}'.format(port - k, port - k)
        agent_sub_2 = AgentSubscriber(AID(name=agent_name), msg)
        agents.append(agent_sub_2)

        c += 1000

    start_loop(agents)
