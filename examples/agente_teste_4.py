# -*- coding: utf-8 -*-
from pade.misc.common import PadeSession
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


def config_agents():
    aa_1 = AgenteIniciante(AID(name='AI1'))

    aa_2 = AgenteParticipante(AID(name='AP1'), 150.0)

    aa_3 = AgenteParticipante(AID(name='AP2'), 100.0)

    agents = list([aa_1, aa_2, aa_3])

    s = PSession()
    s.add_all_agents(agents)
    s.register_user(username='lucassm',
                    email='lucas@gmail.com',
                    password='12345')
    return s

if __name__ == "__main__":

    s = config_agents()
    s.start_loop()
