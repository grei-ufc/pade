#! /usr/bin/ python
# -*- encoding: utf-8 -*-

from utils import config_loop, start_loop, set_ams, display_message
config_loop(gui=True)

from agent import Agent
from messages import ACLMessage
from aid import AID


class Teste(Agent):

    def __init__(self, aid):
        Agent.__init__(self, aid)
        
    def on_start(self):
        Agent.on_start(self)
        display_message(self.aid.name, "Hello World")

        if 'agente_teste_iniciante' in self.aid.name:
            message = ACLMessage(ACLMessage.INFORM)
            message.add_receiver('agente_teste_participante')
            message.set_content('Ola Agente!')
            self.send(message)
            display_message(self.aid.name, 'Enviando mensagem...')
    
    def react(self, message):
        Agent.react(self, message)
        display_message(self.aid.name, 'Uma mensagem recebida')

        if 'agente_teste_participante' in self.aid.name:
            resposta = message.create_reply()
            resposta.set_content('Ola tambem agente!')
            self.send(resposta)

if __name__ == '__main__':
    
    set_ams('localhost', 8000)

    agente_teste_iniciante = Teste(AID('agente_teste_iniciante'))

    agente_teste_participante = Teste(AID('agente_teste_participante'))

    agentes = list()

    print id(agente_teste_iniciante)
    print id(agente_teste_participante)

    agentes.append(agente_teste_participante)
    agentes.append(agente_teste_iniciante)
    
    start_loop(agentes)