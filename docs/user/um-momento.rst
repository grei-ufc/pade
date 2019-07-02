Um momento Por Favor!
=====================

Com PADE é possível adiar a execução de um determinado trecho de código de forma bem simples! É só utilizar o método *call_later()* disponível na classe *Agent()*. 

Como utilizar o método call_later()
-----------------------------------

Para utilizar *call_later()*, os seguintes parâmetros devem ser especificados: tempo de atraso, metodo que deve ser chamado após este tempo e argumento do metodo utilizado, *call_later(tempo, metodo, *args)*. 

No código a seguir o *call_later()* é utilizado na classe *HelloAgent()* no método *on_start()* chamando o método *say_hello()* 10,0 segundos após a inicialização do agente:

::

    from pade.misc.utility import display_message, start_loop, call_later
    from pade.core.agent import Agent
    from pade.acl.messages import ACLMessage
    from pade.acl.aid import AID
    from sys import argv

    class HelloAgent(Agent):
        def __init__(self, aid):
            super(HelloAgent, self).__init__(aid=aid, debug=False)

        def on_start(self):
            super().on_start()
            self.call_later(10.0, self.say_hello)

        def say_hello(self):
            display_message(self.aid.localname, 'Hello, I\'m a agent!')


    if __name__ == '__main__':

        agents = list()

        hello_agent = HelloAgent(AID(name='hello_agent'))
        agents.append(hello_agent)

        start_loop(agents)
