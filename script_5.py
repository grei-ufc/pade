#! /usr/bin/ python
# -*- encoding: utf-8 -*-

from utils import setAMS, configLoop, startLoop, displayMessage
configLoop(gui=True)

from agent import Agent
from messages import ACLMessage
from aid import AID
from pickle import dumps, loads
from time import sleep



class Teste(Agent):
	def __init__(self, aid):
		Agent.__init__(self, aid)
		
	def onStart(self):
		Agent.onStart(self)
		displayMessage(self.aid.name, "Hello World")
		message = ACLMessage(ACLMessage.INFORM)
		message.addReceiver(AID('Alice'))
		message.setContent('Ola Alice!')
		self.send(message)
	
	def react(self, message):
		Agent.react(self, message)
		displayMessage(self.aid.name, message.getMsg())

if __name__ == '__main__':
	setAMS('localhost', 8000)
	
	agente = Teste(AID('Alice'))
	agente.setAMS('localhost', 8000)
	agente.start()
	
	agente = Teste(AID('Bob'))
	agente.setAMS('localhost', 8000)
	agente.start()
	
	startLoop()