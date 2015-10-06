from pade.misc.common import start_loop, set_ams
from pade.misc.utility import display_message
from pade.core.agent import Agent
from pade.acl.messages import ACLMessage
from pade.acl.aid import AID
from pade.behaviours.protocols import FipaRequestProtocol
from pade.behaviours.protocols import TimedBehaviour

from datetime import datetime


class CompRequest(FipaRequestProtocol):
    """Comportamento FIPA Request
    do agente Horario"""
    def __init__(self, agent):
        super(CompRequest, self).__init__(agent=agent,
                                          message=None,
                                          is_initiator=False)

    def handle_request(self, message):
        super(CompRequest, self).handle_request(message)
        display_message(self.agent.aid.localname, 'mensagem request recebida')
        now = datetime.now()
        reply = message.create_reply()
        reply.set_performative(ACLMessage.INFORM)
        reply.set_content(now.strftime('%d/%m/%Y - %H:%M:%S'))
        self.agent.send(reply)


class CompRequest2(FipaRequestProtocol):
    """Comportamento FIPA Request
    do agente Relogio"""
    def __init__(self, agent, message):
        super(CompRequest2, self).__init__(agent=agent,
                                           message=message,
                                           is_initiator=True)

    def handle_inform(self, message):
        display_message(self.agent.aid.localname, message.content)


class ComportTemporal(TimedBehaviour):
    """Comportamento FIPA Request
    do agente Relogio"""
    def __init__(self, agent, time, message):
        super(ComportTemporal, self).__init__(agent, time)
        self.message = message

    def on_time(self):
        super(ComportTemporal, self).on_time()
        self.agent.send(self.message)


class AgenteHorario(Agent):
    """Classe que define o agente Horario"""
    def __init__(self, aid):
        super(AgenteHorario, self).__init__(aid=aid, debug=False)

        self.comport_request = CompRequest(self)

        self.behaviours.append(self.comport_request)


class AgenteRelogio(Agent):
    """Classe que define o agente Relogio"""
    def __init__(self, aid):
        super(AgenteRelogio, self).__init__(aid=aid)

        # mensagem que requisita horario do horario
        message = ACLMessage(ACLMessage.REQUEST)
        message.set_protocol(ACLMessage.FIPA_REQUEST_PROTOCOL)
        message.add_receiver(AID(name='horario'))
        message.set_content('time')

        self.comport_request = CompRequest2(self, message)
        self.comport_temp = ComportTemporal(self, 1.0, message)

        self.behaviours.append(self.comport_request)
        self.behaviours.append(self.comport_temp)


def main():
    agentes = list()
    set_ams('localhost', 8000, debug=False)

    a = AgenteHorario(AID(name='horario'))
    a.ams = {'name': 'localhost', 'port': 8000}
    agentes.append(a)

    a = AgenteRelogio(AID(name='relogio'))
    a.ams = {'name': 'localhost', 'port': 8000}
    agentes.append(a)

    start_loop(agentes, gui=True)

if __name__ == '__main__':
    main()
