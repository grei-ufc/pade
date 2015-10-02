Meu Primeiro Agente
===================


Agora já está na hora de construir um agente de verdade!

Construindo meu primeiro agente
-------------------------------

Para implementar seu primeiro agente abra seu editor de textos preferido e digite o seguinte código:

::

    from pade.misc.utility import display_message
    from pade.misc.common import set_ams, start_loop
    from pade.core.agent import Agent
    from pade.acl.aid import AID


    class AgenteHelloWorld(Agent):
        def __init__(self, aid):
            super(AgenteHelloWorld, self).__init__(aid=aid, debug=False)
            display_message(self.aid.localname, 'Hello World!')

    if __name__ == '__main__':

        set_ams('localhost', 8000, debug=False)

        agents = list()

        agente_hello = AgenteHelloWorld(AID(name='agente_hello'))
        agente_hello.ams = {'name': 'localhost', 'port': 8000}
        agents.append(agente_hello)

        start_loop(agents, gui=True)


Este já é um agente, mas não tem muita utilidade, não é mesmo! Executa apenas uma vez :(

Então como construir um agente que tenha seu comportamento executado de tempos em tempos?
