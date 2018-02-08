# -*- coding: utf-8 -*-
from pade.misc.common import PadeSession
from pade.misc.utility import display_message
from pade.core.agent import Agent
from pade.acl.messages import ACLMessage
from pade.acl.aid import AID
from pade.behaviours.protocols import FipaContractNetProtocol


class CompContNet1(FipaContractNetProtocol):
    '''CompContNet1

       Initial FIPA-ContractNet Behaviour that sends CFP messages
       to other feeder agents asking for restoration proposals.
       This behaviour also analyzes the proposals and selects the
       one it judges to be the best.'''

    def __init__(self, agent, message):
        super(CompContNet1, self).__init__(
            agent=agent, message=message, is_initiator=True)
        self.cfp = message

    def handle_all_proposes(self, proposes):
        """
        """

        super(CompContNet1, self).handle_all_proposes(proposes)

        best_proposer = None
        higher_power = 0.0
        other_proposers = list()
        display_message(self.agent.aid.name, 'Analyzing proposals...')

        i = 1

        # logic to select proposals by the higher available power.
        for message in proposes:
            content = message.content
            power = float(content)
            display_message(self.agent.aid.name,
                            'Analyzing proposal {i}'.format(i=i))
            display_message(self.agent.aid.name,
                            'Power Offered: {pot}'.format(pot=power))
            i += 1
            if power > higher_power:
                if best_proposer is not None:
                    other_proposers.append(best_proposer)

                higher_power = power
                best_proposer = message.sender
            else:
                other_proposers.append(message.sender)

        display_message(self.agent.aid.name,
                        'The best proposal was: {pot} VA'.format(
                            pot=higher_power))

        if other_proposers != []:
            display_message(self.agent.aid.name,
                            'Sending REJECT_PROPOSAL answers...')
            answer = ACLMessage(ACLMessage.REJECT_PROPOSAL)
            answer.set_protocol(ACLMessage.FIPA_CONTRACT_NET_PROTOCOL)
            answer.set_content('')
            for agent in other_proposers:
                answer.add_receiver(agent)

            self.agent.send(answer)

        if best_proposer is not None:
            display_message(self.agent.aid.name,
                            'Sending ACCEPT_PROPOSAL answer...')

            answer = ACLMessage(ACLMessage.ACCEPT_PROPOSAL)
            answer.set_protocol(ACLMessage.FIPA_CONTRACT_NET_PROTOCOL)
            answer.set_content('OK')
            answer.add_receiver(best_proposer)
            self.agent.send(answer)

    def handle_inform(self, message):
        """
        """
        super(CompContNet1, self).handle_inform(message)

        display_message(self.agent.aid.name, 'INFORM message received')

    def handle_refuse(self, message):
        """
        """
        super(CompContNet1, self).handle_refuse(message)

        display_message(self.agent.aid.name, 'REFUSE message received')

    def handle_propose(self, message):
        """
        """
        super(CompContNet1, self).handle_propose(message)

        display_message(self.agent.aid.name, 'PROPOSE message received')


class CompContNet2(FipaContractNetProtocol):
    '''CompContNet2

       FIPA-ContractNet Participant Behaviour that runs when an agent
       receives a CFP message. A proposal is sent and if it is selected,
       the restrictions are analized to enable the restoration.'''

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

        display_message(self.agent.aid.name, 'CFP message rceceived')

        answer = self.message.create_reply()
        answer.set_performative(ACLMessage.PROPOSE)
        answer.set_content(str(self.agent.pot_disp))
        self.agent.send(answer)

    def handle_reject_propose(self, message):
        """
        """
        super(CompContNet2, self).handle_reject_propose(message)

        display_message(self.agent.aid.name,
                        'REJECT_PROPOSAL message received')

    def handle_accept_propose(self, message):
        """
        """
        super(CompContNet2, self).handle_accept_propose(message)

        display_message(self.agent.aid.name,
                        'ACCEPT_PROPOSE message received')

        answer = message.create_reply()
        answer.set_performative(ACLMessage.INFORM)
        answer.set_content('OK')
        self.agent.send(answer)


class AgentInitiator(Agent):

    def __init__(self, aid):
        super(AgentInitiator, self).__init__(aid=aid, debug=False)

        message = ACLMessage(ACLMessage.CFP)
        message.set_protocol(ACLMessage.FIPA_CONTRACT_NET_PROTOCOL)
        message.set_content('60.0')
        message.add_receiver(AID('AP1'))
        message.add_receiver(AID('AP2'))

        comp = CompContNet1(self, message)
        self.behaviours.append(comp)
        self.call_later(2.0, comp.on_start)


class AgentParticipant(Agent):

    def __init__(self, aid, pot_disp):
        super(AgentParticipant, self).__init__(aid=aid, debug=False)

        self.pot_disp = pot_disp

        comp = CompContNet2(self)

        self.behaviours.append(comp)


def config_agents():
    aa_1 = AgentInitiator(AID(name='AI1'))

    aa_2 = AgentParticipant(AID(name='AP1'), 150.0)

    aa_3 = AgentParticipant(AID(name='AP2'), 100.0)

    agents = list([aa_1, aa_2, aa_3])

    s = PadeSession()
    s.add_all_agents(agents)
    s.register_user(username='lucassm',
                    email='lucas@gmail.com',
                    password='12345')
    return s

if __name__ == "__main__":

    s = config_agents()
    s.start_loop()
