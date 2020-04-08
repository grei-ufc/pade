Recebendo Mensagens
===================

No Pade para que um agente possa receber mensagens, basta que o método react() seja implementado, dentro da classe que herda da classe `Agent()`.

Recebendo mensagens FIPA-ACL com PADE
-------------------------------------

No exemplo a seguir são implementados dois agentes distintos, o primeiro é o agente ```remetente``` modelado pela classe `Remetente()`, que tem o papel de enviar uma mensagem ao agente `destinatario` modelado pela classe `Destinatario`, que irá receber a mensagem enviada pelo agente `remetente` e por isso tem o método `react()` implementado.   

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
            super(Remetente, self).on_start()
            display_message(self.aid.localname, 'Enviando Mensagem...')
            call_later(8.0, self.sending_message)

        def sending_message(self):
            message = ACLMessage(ACLMessage.INFORM)
            message.add_receiver(AID('destinatario'))
            message.set_content('Ola')
            self.send(message)

        def react(self, message):
            super(Remetente, self).react(message)
            display_message(self.aid.localname, 'Mensagem recebida from {}'.format(message.sender.name))


    class Destinatario(Agent):
        def __init__(self, aid):
            super(Destinatario, self).__init__(aid=aid, debug=False)

        def react(self, message):
            super(Destinatario, self).react(message)
            display_message(self.aid.localname, 'Mensagem recebida from {}'.format(message.sender.name))


    if __name__ == '__main__':

        agents = list()
        port = int(argv[1])
        destinatario_agent = Destinatario(AID(name='destinatario@localhost:{}'.format(port)))
        agents.append(destinatario_agent)

        port += 1
        remetente_agent = Remetente(AID(name='remetente@localhost:{}'.format(port)))
        agents.append(remetente_agent)

        start_loop(agents)


.. Visualização via Interface Gráfica
.. ----------------------------------

.. A seguir é possível observar a interface gráfica do PADE que mostra os agentes cadastrados no AMS.

.. .. figure:: ../img/janela_agentes.png
..     :align: center
..     :width: 4.5in

.. Ao clicar na mensagem recebida pelo agente `destinatario` é possível observar todos os dados contidos na mensagem:

.. .. figure:: ../img/janela_mensagem.png
..     :align: center
..     :width: 3.0in