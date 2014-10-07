#! /usr/bin/ python
# -*- encoding: utf-8 -*-

from utils import set_ams, config_loop, start_loop, display_message
config_loop(gui=True)

from agent import Agent
from messages import ACLMessage
from aid import AID
from pickle import dumps, loads
from time import sleep



class Teste(Agent):
	def __init__(self, aid):
		Agent.__init__(self, aid)
		
	def on_start
on_start(self):
		Agent.on_start
on_start(self)
		display_message(self.aid.name, "Hello World")
		if 'Bob' in self.aid.name:
			message = ACLMessage(ACLMessage.INFORM)
			message.add_receiver(AID('Alice'))
			message.set_content('Ola Alice!')
			self.send(message)
	
	def react(self, message):
		Agent.react(self, message)
		display_message(self.aid.name, message.get_message())

if __name__ == '__main__':
	set_ams('localhost', 8000)
	
	agente = Teste(AID('Alice'))
	agente.set_ams('localhost', 8000)
	agente.start()
	
	agente = Teste(AID('Bob'))
	agente.set_ams('localhost', 8000)
	agente.start()
	
	start_loop()