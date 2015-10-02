Protocolos
==========

O PADE tem suporte aos protocolos mais utilizados estabelecidos pela FIPA, são eles:

* :ref:`FIPA-Request`
* :ref:`FIPA-Contract-Net`
* :ref:`FIPA-Subscribe`

No PADE qualquer protocolo deve ser implementado como uma classe que extende a classe do protocolo desejado, por exemplo para implementar o protocolo FIPA-Request, deve ser implementada uma classe que implementa a herança da classe FipaRequestProtocol:

::

    from pade.behaviours.protocols import FipaRequestProtocol


    class ProtocoloDeRequisicao(FipaRequestProtocol):

        def __init__(self):
            super(ProtocoloDeRequisicao, self).__init__()

.. _FIPA-Request:

FIPA-Request
------------

O protocolo FIPA-Request é o mais simples de se utilizar e constitui uma padronização do ato de requisitar alguma tarefa ou informação de um agente iniciador para um agente participante.

O diagrama de comunicação do protocolo FIPA-Request está mostrado na Figura abaixo:

.. image:: ../img/seq_diag_request.png
    :align: center
    :width: 4.5in

Para exemplificar o protocolo FIPA-Request, iremos utilizar como exemplo a interação entre dois agentes, um agente relogio, que a cada um segundo exibe na tela a data e o horário atuais, mas com um problema, o agente relogio não sabe calcular nem a data, e muito menos o horário atual. Assim, ele precisa requisitar estas informações do agente horario que consegue calcular estas informações.

Dessa forma, será utilizado o protocolo FIPA-Request, para que estas informações sejam trocadas entre os dois agentes, sendo o agente relógio o iniciante, no processo de requisição e o agente horário, o participante, segue o código do exemplo:

::
    
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


Na primeira parte do código são importadas todos módulos e classes necessários à construção dos agentes, logo em seguida as classes que implementam o protocolo são definidas, as classes ComptRequest e ComptRequest2 que serão associadas aos comportamentos dos agentes horario e relogio, respectivamente. Como o agente relogio precisa, a cada segundo enviar requisição ao agente horario, então também deve ser associado a este agente um comportamento temporal, definido na classe ComportTemporal que envia uma solicitação ao agente horario, a cada segundo.

Em seguida, os agente propriamente ditos, são definidos nas classes AgenteHoraio e AgenteRelogio que estendem a classe Agent, nessas classes é que os comportamentos e protocolos são associados a cada agente.

Na ultima parte do código, é definida uma função main que indica a localização do agente ams, instancia os agentes e dá inicio ao loop de execução.

.. _FIPA-Contract-Net:

FIPA-Contract-Net
-----------------

O protocolo FIPA-Contract-Net é utilizado para situações onde é necessário realizar algum tipo de negociação entre agentes. Da mesma forma que no protocolo FIPA-Request, no protocolo FIPA-ContractNet existem dois tipos de agentes, um agente que inicia a negociação, ou agente iniciante, fazendo solicitação de propostas e um ou mais agentes que participam da negociação, ou agentes pasticipantes, que repondem às solicitações de propostas do agente iniciante. Veja:

.. figure:: ../img/seq_diag_contract.png
    :align: center
    :width: 4.5in


Um exemplo de utilização do protocolo FIPA-ContractNet na negociação é mostrado abaixo, com a solicitação de um agente iniciante por potência elétrica a outros dois agentes participantes:

::

    from pade.misc.common import start_loop, set_ams
    from pade.misc.utility import display_message
    from pade.core.agent import Agent
    from pade.acl.messages import ACLMessage
    from pade.acl.aid import AID
    from pade.behaviours.protocols import FipaContractNetProtocol


    class CompContNet1(FipaContractNetProtocol):
        '''CompContNet1

           Comportamento FIPA-ContractNet Iniciante que envia mensagens
           CFP para outros agentes alimentadores solicitando propostas
           de restauração. Este comportamento também faz a analise das
           das propostas e analisa-as selecionando a que julga ser a
           melhor'''

        def __init__(self, agent, message):
            super(CompContNet1, self).__init__(
                agent=agent, message=message, is_initiator=True)
            self.cfp = message

        def handle_all_proposes(self, proposes):
            """
            """

            super(CompContNet1, self).handle_all_proposes(proposes)

            melhor_propositor = None
            maior_potencia = 0.0
            demais_propositores = list()
            display_message(self.agent.aid.name, 'Analisando propostas...')

            i = 1

            # lógica de seleção de propostas pela maior potência disponibilizada
            for message in proposes:
                content = message.content
                potencia = float(content)
                display_message(self.agent.aid.name,
                                'Analisando proposta {i}'.format(i=i))
                display_message(self.agent.aid.name,
                                'Potencia Ofertada: {pot}'.format(pot=potencia))
                i += 1
                if potencia > maior_potencia:
                    if melhor_propositor is not None:
                        demais_propositores.append(melhor_propositor)

                    maior_potencia = potencia
                    melhor_propositor = message.sender
                else:
                    demais_propositores.append(message.sender)

            display_message(self.agent.aid.name,
                            'A melhor proposta foi de: {pot} VA'.format(
                                pot=maior_potencia))

            if demais_propositores != []:
                display_message(self.agent.aid.name,
                                'Enviando respostas de recusa...')
                resposta = ACLMessage(ACLMessage.REJECT_PROPOSAL)
                resposta.set_protocol(ACLMessage.FIPA_CONTRACT_NET_PROTOCOL)
                resposta.set_content('')
                for agente in demais_propositores:
                    resposta.add_receiver(agente)

                self.agent.send(resposta)

            if melhor_propositor is not None:
                display_message(self.agent.aid.name,
                                'Enviando resposta de aceitacao...')

                resposta = ACLMessage(ACLMessage.ACCEPT_PROPOSAL)
                resposta.set_protocol(ACLMessage.FIPA_CONTRACT_NET_PROTOCOL)
                resposta.set_content('OK')
                resposta.add_receiver(melhor_propositor)
                self.agent.send(resposta)

        def handle_inform(self, message):
            """
            """
            super(CompContNet1, self).handle_inform(message)

            display_message(self.agent.aid.name, 'Mensagem INFORM recebida')

        def handle_refuse(self, message):
            """
            """
            super(CompContNet1, self).handle_refuse(message)

            display_message(self.agent.aid.name, 'Mensagem REFUSE recebida')

        def handle_propose(self, message):
            """
            """
            super(CompContNet1, self).handle_propose(message)

            display_message(self.agent.aid.name, 'Mensagem PROPOSE recebida')


    class CompContNet2(FipaContractNetProtocol):
        '''CompContNet2

           Comportamento FIPA-ContractNet Participante que é acionado
           quando um agente recebe uma mensagem do Tipo CFP enviando logo
           em seguida uma proposta e caso esta seja selecinada realiza as
           as análises de restrição para que seja possível a restauração'''

        def __init__(self, agent):
            super(CompContNet2, self).__init__(agent=agent,
                                               message=None,
                                               is_initiator=False)

        def handle_cfp(self, message):
            """
            """
            self.agent.call_later(1.0, self._handle_cfp, message)

        def _handle_cfp(self, message):
            """
            """
            super(CompContNet2, self).handle_cfp(message)
            self.message = message

            display_message(self.agent.aid.name, 'Mensagem CFP recebida')

            resposta = self.message.create_reply()
            resposta.set_performative(ACLMessage.PROPOSE)
            resposta.set_content(str(self.agent.pot_disp))
            self.agent.send(resposta)

        def handle_reject_propose(self, message):
            """
            """
            super(CompContNet2, self).handle_reject_propose(message)

            display_message(self.agent.aid.name,
                            'Mensagem REJECT_PROPOSAL recebida')

        def handle_accept_propose(self, message):
            """
            """
            super(CompContNet2, self).handle_accept_propose(message)

            display_message(self.agent.aid.name,
                            'Mensagem ACCEPT_PROPOSE recebida')

            resposta = message.create_reply()
            resposta.set_performative(ACLMessage.INFORM)
            resposta.set_content('OK')
            self.agent.send(resposta)


    class AgenteIniciante(Agent):

        def __init__(self, aid):
            super(AgenteIniciante, self).__init__(aid=aid, debug=False)

            message = ACLMessage(ACLMessage.CFP)
            message.set_protocol(ACLMessage.FIPA_CONTRACT_NET_PROTOCOL)
            message.set_content('60.0')
            message.add_receiver(AID('AP1'))
            message.add_receiver(AID('AP2'))

            comp = CompContNet1(self, message)
            self.behaviours.append(comp)
            self.call_later(2.0, comp.on_start)


    class AgenteParticipante(Agent):

        def __init__(self, aid, pot_disp):
            super(AgenteParticipante, self).__init__(aid=aid, debug=False)

            self.pot_disp = pot_disp

            comp = CompContNet2(self)

            self.behaviours.append(comp)

    if __name__ == "__main__":

        set_ams('localhost', 5000, debug=False)

        aa_1 = AgenteIniciante(AID(name='AI1'))
        aa_1.ams = {'name': 'localhost', 'port': 5000}

        aa_2 = AgenteParticipante(AID(name='AP1'), 150.0)
        aa_2.ams = {'name': 'localhost', 'port': 5000}

        aa_3 = AgenteParticipante(AID(name='AP2'), 100.0)
        aa_3.ams = {'name': 'localhost', 'port': 5000}

        agents_list = list([aa_1, aa_2, aa_3])

        start_loop(agents_list, gui=True)

O código que implementa os agentes que se comunicam utilizando o protocolo FIPA-ContractNet, definine as duas classes do protocolo, a primeira implementa o comportamento do agente Iniciante (CompContNet1) e a segunda implementa o comportamento do agente participante (CompContNet2). Note que para a classe iniciante é necessário que uma mensagem do tipo CFP (call for proposes) seja montada e o método on_start() seja chamado, isso é feito dentro da classe que implementa os agente iniciante, AgenteIniciante(), já a classe AgenteParticipante(), implementa os agentes que participarão da negociação como propositores.

É possível observar as mensagens da negociação na intergace gráfica do PADE, veja:

.. image:: ../img/contract_net/ACLMessage_todas.png
    :align: center
    :width: 4.5in

.. _FIPA-Subscribe:

FIPA-Subscribe
--------------

O protocolo FIPA-Subscribe, implementa o comportamento de editor-assinante, que conssiste na presença de um agente editor que pode aceitar a associação de outros agentes interessados, agentes assinantes, em algum tipo de informação que este agente possua, assinando a informação e recebendo mensagem sempre que esta informação for disponibilizada pelo agente editor. Veja:

.. figure:: ../img/seq_diag_subscribe.png
    :align: center
    :width: 4.5in

Para assinar a informação o agente precisa enviar uma mensagem SUSBCRIBE para o agente editor. Que por sua vez pode aceitar ou recusar a assinatura (AGREE/REFUSE). Quando uma informação é atualizada, então o editor publica esta informação para todos os seus assinantes, enviando-os mensagens INFORM.

O código que implementa um agente editor e dois agentes assinantes utilizando PADE pode ser visualizado abaixo:

::
    
    from pade.misc.common import start_loop, set_ams
    from pade.misc.utility import display_message
    from pade.core.agent import Agent
    from pade.acl.aid import AID
    from pade.acl.messages import ACLMessage
    from pade.behaviours.protocols import FipaSubscribeProtocol, TimedBehaviour
    from numpy import sin


    class SubscribeInitiator(FipaSubscribeProtocol):

        def __init__(self, agent, message):
            super(SubscribeInitiator, self).__init__(agent,
                                                     message,
                                                     is_initiator=True)

        def handle_agree(self, message):
            display_message(self.agent.aid.name, message.content)

        def handle_inform(self, message):
            display_message(self.agent.aid.name, message.content)


    class SubscribeParticipant(FipaSubscribeProtocol):

        def __init__(self, agent):
            super(SubscribeParticipant, self).__init__(agent,
                                                       message=None,
                                                       is_initiator=False)

        def handle_subscribe(self, message):
            self.register(message.sender)
            display_message(self.agent.aid.name, message.content)

            resposta = message.create_reply()
            resposta.set_performative(ACLMessage.AGREE)
            resposta.set_content('Pedido de subscricao aceito')
            self.agent.send(resposta)

        def handle_cancel(self, message):
            self.deregister(self, message.sender)
            display_message(self.agent.aid.name, message.content)

        def notify(self, message):
            super(SubscribeParticipant, self).notify(message)


    class Time(TimedBehaviour):

        def __init__(self, agent, notify):
            super(Time, self).__init__(agent, 1)
            self.notify = notify
            self.inc = 0

        def on_time(self):
            super(Time, self).on_time()
            message = ACLMessage(ACLMessage.INFORM)
            message.set_protocol(ACLMessage.FIPA_SUBSCRIBE_PROTOCOL)
            message.set_content(str(sin(self.inc)))

            self.notify(message)
            self.inc += 0.1


    class AgenteInitiator(Agent):

        def __init__(self, aid, message):
            super(AgenteInitiator, self).__init__(aid)
            self.protocol = SubscribeInitiator(self, message)
            self.behaviours.append(self.protocol)


    class AgenteParticipante(Agent):

        def __init__(self, aid):
            super(AgenteParticipante, self).__init__(aid)

            self.protocol = SubscribeParticipant(self)
            self.timed = Time(self, self.protocol.notify)

            self.behaviours.append(self.protocol)
            self.behaviours.append(self.timed)

    if __name__ == '__main__':

        set_ams('localhost', 5000, debug=False)

        editor = AgenteParticipante(AID('editor'))
        editor.ams = {'name': 'localhost', 'port': 5000}

        msg = ACLMessage(ACLMessage.SUBSCRIBE)
        msg.set_protocol(ACLMessage.FIPA_SUBSCRIBE_PROTOCOL)
        msg.set_content('Pedido de subscricao')
        msg.add_receiver('editor')

        ass1 = AgenteInitiator(AID('assinante_1'), msg)
        ass1.ams = {'name': 'localhost', 'port': 5000}

        ass2 = AgenteInitiator(AID('assinante_2'), msg)
        ass2.ams = {'name': 'localhost', 'port': 5000}

        agentes = [editor, ass1, ass2]

        start_loop(agentes, gui=True)
