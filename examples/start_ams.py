#!coding=utf-8
# start_ams in PADE!
#
# Criado por Lucas S Melo em 03 de outubro de 2018 - Fortaleza, Ceará - Brasil

from pade.misc.common import PadeSession

def config_agents():

    agents = list()

    s = PadeSession()
    s.add_all_agents(agents)
    s.register_user(username='pade_user', email='user@pade.com', password='12345')

    return s

if __name__ == '__main__':

    s = config_agents()
    s.start_loop()
