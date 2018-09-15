#!coding=utf-8
# Hello world in PADE!
#
# Criado por Lucas S Melo em 21 de julho de 2015 - Fortaleza, Ceará - Brasil

from pade.misc.utility import display_message
from pade.misc.common import PadeSession
from pade.core.agent import Agent
from pade.acl.aid import AID


class AgenteHelloWorld(Agent):
    def __init__(self, aid):
        super(AgenteHelloWorld, self).__init__(aid=aid)
        display_message(self.aid.localname, 'Hello World!')


def config_agents():

    agents = list()

    agente_hello = AgenteHelloWorld(AID(name='agente_hello'))
    agents.append(agente_hello)

    s = PadeSession()
    s.add_all_agents(agents)
    s.register_user(username='lucassm', email='lucas@gmail.com', password='12345')

    return s

if __name__ == '__main__':

    s = config_agents()
    s.start_loop()
