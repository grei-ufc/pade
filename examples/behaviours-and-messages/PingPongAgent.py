from pade.acl.aid import AID
from pade.acl.messages import ACLMessage
from pade.behaviours.types import CyclicBehaviour, OneShotBehaviour
from pade.core.agent import Agent
from pade.misc.utility import display_message, start_loop


# ==== Ping Agent ====

class PingAgent(Agent):
	def __init__(self, name, pong_aid):
		super().__init__(name)
		self.pong = pong_aid # Gets the pong AID

	def setup(self):
		# Adding behaviours to this agent
		self.add_behaviour(StartGame(self))
		self.add_behaviour(PingTurn(self))

class StartGame(OneShotBehaviour):
	def action(self):
		# Preparing a message to 'pong'
		message = ACLMessage(ACLMessage.INFORM)
		message.add_receiver(self.agent.pong)
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
		if self.agent.has_messages():
			message = self.agent.read()
			if message.sender == self.agent.pong:
				# Preparing a reply to self.receiver
				reply = message.create_reply()
				reply.set_content('PING')
				display_message(self.agent, 'Turn: %s' % message.content)
				# Wait a time before send the message
				#(Do you want to see the results, don't you?)
				self.wait(0.5)
				# Sending the message
				self.send(reply)


# ==== Pong Agent ====

class PongAgent(Agent):
	def __init__(self, name, ping_aid):
		super().__init__(name)
		self.ping = ping_aid # Gets the ping AID

	def setup(self):
		self.add_behaviour(PongTurn(self))

class PongTurn(CyclicBehaviour):
	def action(self):
		if self.agent.has_messages():
			message = self.agent.read()
			if message.sender == self.agent.ping:
				# Preparing a reply to 'ping'
				reply = message.create_reply()
				reply.set_content('PONG')
				display_message(self.agent, 'Turn: %s' % message.content)
				self.wait(0.5)
				# Sending the reply
				self.send(reply)


# ==== Starting main loop of PADE ====

if __name__ == '__main__':
	ping_aid = AID('ping') # Creates an AID for ping
	pong_aid = AID('pong') # Creates an AID for pong
	# Creates a PingAgent using the AID ping_aid and passing the address (AID) of PongAgent (pong_aid)
	ping = PingAgent(ping_aid, pong_aid)
	# Creates a PongAgent using the AID pong_aid and passing the address (AID) of PingAgent (ping_aid)
	pong = PongAgent(pong_aid, ping_aid)
	start_loop([ping, pong])
