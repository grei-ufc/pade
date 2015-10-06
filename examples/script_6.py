# -*- coding: utf-8 -*-

import sys
sys.path.insert(1, '/home/lucas/Dropbox/workspace/Twisted_Agents/')

from misc.common import set_ams, start_loop
from misc.utility import display_message
from core.agent import Agent
from acl.messages import ACLMessage
from acl.aid import AID
from behaviours.protocols import FipaRequestProtocol

class ComportamentoAluno(FipaRequestProtocol):

    def __init__(self, agent, message):
        super(ComportamentoAluno, self).__init__(
            agent, message, is_initiator=True)

    def handle_inform(self, message):
        FipaRequestProtocol.handle_inform(self, message)
        display_message(self.agent.aid.name, 'Resposta Recebida')


class ComportamentoProfessor(FipaRequestProtocol):

    def __init__(self, agent):
        super(ComportamentoProfessor, self).__init__(
            agent=agent, message=None, is_initiator=False)

    def handle_request(self, message):
        FipaRequestProtocol.handle_request(self, message)
        display_message(self.agent.aid.name, message.content)
        resposta = message.create_reply()
        resposta.set_performative(ACLMessage.INFORM)
        resposta.set_content('Essa e sua resposta')
        self.agent.send(resposta)


class Aluno(Agent):

    def __init__(self, aid):
        super(Aluno, self).__init__(aid=aid, debug=False)
        message = ACLMessage(ACLMessage.REQUEST)
        message.set_protocol(ACLMessage.FIPA_REQUEST_PROTOCOL)
        message.set_content('Essa e uma pergunta')
        message.add_receiver('professor')
        comportamento = ComportamentoAluno(self, message)
        self.behaviours.append(comportamento)


class Professor(Agent):

    def __init__(self, aid):
        super(Professor, self).__init__(aid=aid, debug=False)
        comportamento = ComportamentoProfessor(self)
        self.behaviours.append(comportamento)


if __name__ == '__main__':
    
    #set_ams('localhost', 8000)
    agents = list()

    professor = Professor(AID(name='professor'))
    agents.append(professor)

    aluno = Aluno(AID(name='aluno'))
    agents.append(aluno)

    start_loop(agents)
