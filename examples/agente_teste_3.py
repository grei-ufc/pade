from pade.misc.common import PadeSession
from pade.misc.utility import display_message
from pade.core.agent import Agent
from pade.acl.messages import ACLMessage
from pade.acl.aid import AID
from pade.behaviours.protocols import FipaRequestProtocol
from pade.behaviours.protocols import TimedBehaviour

from datetime import datetime


class CompRequest(FipaRequestProtocol):
    """FIPA Request Behaviour of the Time agent.
    """
    def __init__(self, agent):
        super(CompRequest, self).__init__(agent=agent,
                                          message=None,
                                          is_initiator=False)

    def handle_request(self, message):
        super(CompRequest, self).handle_request(message)
        display_message(self.agent.aid.localname, 'request message received')
        now = datetime.now()
        reply = message.create_reply()
        reply.set_performative(ACLMessage.INFORM)
        reply.set_content(now.strftime('%d/%m/%Y - %H:%M:%S'))
        self.agent.send(reply)


class CompRequest2(FipaRequestProtocol):
    """FIPA Request Behaviour of the Clock agent.
    """
    def __init__(self, agent, message):
        super(CompRequest2, self).__init__(agent=agent,
                                           message=message,
                                           is_initiator=True)

    def handle_inform(self, message):
        display_message(self.agent.aid.localname, message.content)


class ComportTemporal(TimedBehaviour):
    """Timed Behaviour of the Clock agent"""
    def __init__(self, agent, time, message):
        super(ComportTemporal, self).__init__(agent, time)
        self.message = message

    def on_time(self):
        super(ComportTemporal, self).on_time()
        self.agent.send(self.message)


class TimeAgent(Agent):
    """Class that defines the Time agent."""
    def __init__(self, aid):
        super(TimeAgent, self).__init__(aid=aid, debug=False)

        self.comport_request = CompRequest(self)

        self.behaviours.append(self.comport_request)


class ClockAgent(Agent):
    """Class thet defines the Clock agent."""
    def __init__(self, aid):
        super(ClockAgent, self).__init__(aid=aid)

        # message that requests time of Time agent.
        message = ACLMessage(ACLMessage.REQUEST)
        message.set_protocol(ACLMessage.FIPA_REQUEST_PROTOCOL)
        message.add_receiver(AID(name='time'))
        message.set_content('time')

        self.comport_request = CompRequest2(self, message)
        self.comport_temp = ComportTemporal(self, 5.0, message)

        self.behaviours.append(self.comport_request)
        self.behaviours.append(self.comport_temp)


def config_agents():

    agents = list()

    a = TimeAgent(AID(name='time'))
    agents.append(a)

    a = ClockAgent(AID(name='clock'))
    agents.append(a)

    s = PadeSession()
    s.add_all_agents(agents)
    s.register_user(username='lucassm',
                    email='lucas@gmail.com',
                    password='12345')

    return s

if __name__ == '__main__':
    s = config_agents()
    s.start_loop()
