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

        if 'test_agent_initiator' in self.aid.name:
            message = ACLMessage(ACLMessage.INFORM)
            message.add_receiver('test_agent_participant')
            message.set_content('Hello Agent!')
            self.send(message)
            display_message(self.aid.name, 'Sending Message...')
    
    def react(self, message):
        Agent.react(self, message)
        display_message(self.aid.name, 'One message received')

        if 'test_agent_participant' in self.aid.name:
            resposta = message.create_reply()
            resposta.set_content('Hello to you too, Agent!')
            self.send(resposta)

if __name__ == '__main__':
    
    set_ams('localhost', 8000)

    test_agent_initiator = Teste(AID('test_agent_initiator'))

    test_agent_participant = Teste(AID('test_agent_participant'))

    agents = list()

    print id(test_agent_initiator)
    print id(test_agent_participant)

    agents.append(test_agent_participant)
    agents.append(test_agent_initiator)
    
    start_loop(agents)