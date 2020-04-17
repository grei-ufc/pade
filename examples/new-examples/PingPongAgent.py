from pade.acl.aid import AID
from pade.acl.messages import ACLMessage
from pade.behaviours.types import CyclicBehaviour, OneShotBehaviour
from pade.core.agent import Agent
from pade.misc.utility import display_message, start_loop


# ==== Ping Agent ====

class PingAgent(Agent):
	def setup(self):
		# Adding behaviours to this agent
		self.add_behaviour(StartGame(self))
		self.add_behaviour(PingTurn(self))

class StartGame(OneShotBehaviour):
	def action(self):
		# Preparing a message to 'pong'
		message = ACLMessage(ACLMessage.INFORM)
		message.add_receiver(AID('pong'))
		message.set_content('PING')
		# Sending the message
		self.send(message)

class PingTurn(CyclicBehaviour):
	def action(self):
		# Awaits for a message from 'pong'. The execution of this
		# behaviour will stops until some message arrives at this
		# agent. If you want to read a message without blocking the
		# behaviour, use self.read(block = False) or 
		# self.read_timeout(timeout). These methods returns None 
		# if don't have messages to agent. See docs to more details.
		message = self.read()
		if message.sender.getLocalName() == 'pong':
			# Preparing a reply to self.receiver
			reply = message.create_reply()
			reply.set_content('PING')
			display_message(self.agent, 'Turn: %s' % message.content)
			# Wait a time before send the message
			#(Do you want to see the results, do not you?)
			self.wait(0.5)
			# Sending the message
			self.send(reply)


# ==== Pong Agent ====

class PongAgent(Agent):
	def setup(self):
		self.add_behaviour(PongTurn(self))

class PongTurn(CyclicBehaviour):
	def action(self):
		message = self.read()
		if message.sender.getLocalName() == 'ping':
			# Preparing a reply to 'ping'
			reply = message.create_reply()
			reply.set_content('PONG')
			display_message(self.agent, 'Turn: %s' % message.content)
			self.wait(0.5)
			# Sending the reply
			self.send(reply)


# ==== Starting main loop of PADE ====

if __name__ == '__main__':
	ping = PingAgent('ping')
	pong = PongAgent('pong')
	start_loop([ping, pong])
