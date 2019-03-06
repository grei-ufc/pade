Um momento Por Favor!
=====================

Com PADE é possível adiar a execução de um determinado trecho de código de forma bem simples! É só utilizar o método *call_later()* disponível na classe *Agent()*. 

Como utilizar o método call_later()
-----------------------------------

Para utilizar *call_later()*, os seguintes parâmetros devem ser especificados: tempo de atraso, metodo que deve ser chamado após este tempo e argumento do metodo utilizado, *call_later(tempo, metodo, *args)*. 

No código a seguir utiliza *call_later()* é utilizado na classe *Remetente()* no método *on_start()* para assegurar que todos os agentes já foram lançados na plataforma, chamando o método *send_message()* 4,0 segundos após a inicialização dos agentes:

::

    from pade.misc.utility import display_message, start_loop, call_later
    from pade.core.agent import Agent
    from pade.acl.messages import ACLMessage
    from pade.acl.aid import AID
    from sys import argv


    class Remetente(Agent):
        def __init__(self, aid):
            super(Remetente, self).__init__(aid=aid, debug=False)

        def on_start(self):
            call_later(5.0, self.send_message)
        
        def send_message(self):
            display_message(self.aid.localname, 'Enviando Mensagem...')
            message = ACLMessage(ACLMessage.INFORM)
            message.add_receiver(AID('destinatario'))
            message.set_content('Ola')
            self.send(message)

        def react(self, message):
            pass


    class Destinatario(Agent):
        def __init__(self, aid):
            super(Destinatario, self).__init__(aid=aid, debug=False)

        def react(self, message):
            display_message(self.aid.localname, 'Mensagem recebida')


    if __name__ == '__main__':

        destinatario_agent = Destinatario(AID(name='destinatario'))
        agents.append(destinatario_agent)

        remetente_agent = Remetente(AID(name='remetente'))
        agents.append(remetente_agent)

        start_loop(agents)
