Recebendo Mensagens
===================

No PADE para que um agente possa receber mensagens, basta que o método react() seja implementado, dentro da classe que herda da classe `Agent()`.

Recebendo mensagens FIPA-ACL com PADE
-------------------------------------

No exemplo a seguir são implementados dois agentes distintos, o primeiro é o agente ```remetente``` modelado pela classe `Remetente()`, que tem o papel de enviar uma mensagem ao agente `destinatario` modelado pela classe `Destinatario`, que irá receber a mensagem enviada pelo agente `remetente` e por isso tem o método `react()` implementado.   

::

    from pade.misc.utility import display_message
    from pade.misc.common import set_ams, start_loop
    from pade.core.agent import Agent
    from pade.acl.aid import AID
    from pade.acl.messages import ACLMessage


    class Remetente(Agent):
        def __init__(self, aid):
            super(Remetente, self).__init__(aid=aid, debug=False)

        def on_start(self):
            display_message(self.aid.localname, 'Enviando Mensagem')
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

        set_ams('localhost', 8000, debug=False)

        agentes = list()

        destinatario = Destinatario(AID(name='destinatario'))
        destinatario.ams = {'name': 'localhost', 'port': 8000}
        agentes.append(destinatario)

        remetente = Remetente(AID(name='remetente'))
        remetente.ams = {'name': 'localhost', 'port': 8000}
        agentes.append(remetente)

        start_loop(agentes, gui=True)


Visualização via Interface Gráfica
----------------------------------

A seguir é possível observar a interface gráfica do PADE que mostra os agentes cadastrados no AMS.

.. figure:: ../img/janela_agentes.png
    :align: center
    :width: 4.5in

Ao clicar na mensagem recebida pelo agente `destinatario` é possível observar todos os dados contidos na mensagem:

.. figure:: ../img/janela_mensagem.png
    :align: center
    :width: 3.0in