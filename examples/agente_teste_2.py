#!coding=utf-8
# Hello world temporal in PADE!
#
# Criado por Lucas S Melo em 21 de julho de 2015 - Fortaleza, Ceará - Brasil

from pade.behaviours.protocols import TimedBehaviour
from pade.misc.utility import display_message
from pade.misc.common import PadeSession
from pade.core.agent import Agent
from pade.acl.aid import AID


class ComportTemporal(TimedBehaviour):
    def __init__(self, agent, time):
        super(ComportTemporal, self).__init__(agent, time)

    def on_time(self):
        super(ComportTemporal, self).on_time()
        display_message(self.agent.aid.localname, 'Hello World!')


class AgenteHelloWorld(Agent):
    def __init__(self, aid):
        super(AgenteHelloWorld, self).__init__(aid=aid, debug=False)

        comp_temp = ComportTemporal(self, 1.0)

        self.behaviours.append(comp_temp)


def config_agents():
    agents = list()

    agente_1 = AgenteHelloWorld(AID(name='agente_1'))
    agente_2 = AgenteHelloWorld(AID(name='agente_2'))

    agents.append(agente_1)
    agents.append(agente_2)

    s = PadeSession()
    s.add_all_agents(agents)
    s.register_user(username='lucassm',
                    email='lucas@gmail.com',
                    password='12345')

    return s

if __name__ == '__main__':
    s = config_agents()
    s.start_loop()
