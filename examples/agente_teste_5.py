from pade.misc.common import start_loop, set_ams
from pade.misc.utility import display_message
from pade.core.agent import Agent
from pade.acl.aid import AID
from pade.acl.messages import ACLMessage
from pade.behaviours.protocols import FipaSubscribeProtocol, TimedBehaviour
from numpy import sin


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
        resposta.set_content('Pedido de subscricao aceito')
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
        message.set_content(str(sin(self.inc)))

        self.notify(message)
        self.inc += 0.1


class AgenteInitiator(Agent):

    def __init__(self, aid, message):
        super(AgenteInitiator, self).__init__(aid)
        self.protocol = SubscribeInitiator(self, message)
        self.behaviours.append(self.protocol)


class AgenteParticipante(Agent):

    def __init__(self, aid):
        super(AgenteParticipante, self).__init__(aid)

        self.protocol = SubscribeParticipant(self)
        self.timed = Time(self, self.protocol.notify)

        self.behaviours.append(self.protocol)
        self.behaviours.append(self.timed)

if __name__ == '__main__':

    set_ams('localhost', 5000, debug=False)

    editor = AgenteParticipante(AID('editor'))
    editor.ams = {'name': 'localhost', 'port': 5000}

    msg = ACLMessage(ACLMessage.SUBSCRIBE)
    msg.set_protocol(ACLMessage.FIPA_SUBSCRIBE_PROTOCOL)
    msg.set_content('Pedido de subscricao')
    msg.add_receiver('editor')

    ass1 = AgenteInitiator(AID('assinante_1'), msg)
    ass1.ams = {'name': 'localhost', 'port': 5000}

    ass2 = AgenteInitiator(AID('assinante_2'), msg)
    ass2.ams = {'name': 'localhost', 'port': 5000}

    agentes = [editor, ass1, ass2]

    start_loop(agentes, gui=True)
