from pade.acl.aid import AID
from pade.acl.messages import ACLMessage
from pade.behaviours.types import CyclicBehaviour, SimpleBehaviour
from pade.core.agent import Agent
from pade.misc.utility import display_message, start_loop


# ==== Ping Agent ====

class PingAgent(Agent):
	def __init__(self, aid,):
		super().__init__(aid)
		# Attribute that indicates the start of the 'game'
		self.started = False

	def setup(self):
		# Adding behaviours to this agent
		self.add_behaviour(StartGame(self))
		self.add_behaviour(PingTurn(self))

class StartGame(SimpleBehaviour):
	def action(self):
		# Preparing a message to 'pong'
		message = ACLMessage(ACLMessage.INFORM)
		message.add_receiver(AID('pong'))
		message.set_content('PING')
		# Wait 1 second to save CPU
		self.wait(1)
		# Sending the message
		self.agent.send(message)

	# Defines when the behaviour ends
	def done(self):
		return self.agent.started

class PingTurn(CyclicBehaviour):
	def action(self):
		# Awaits for a message from self.receiver. The execution
		# of this behaviour will stops until some message arrives
		# at this agent. If you want to read a message without 
		# blocking the behaviour, use self.read(block = False) or
		# self.read_timeout(timeout). These methods returns None 
		# if don't have messages to agent. See docs to more details.
		message = self.read()
		if message.sender.getLocalName() == 'pong':
			# If it is the first reply
			if not self.agent.started:
				self.agent.started = True
			# Preparing a reply to self.receiver
			reply = message.create_reply()
			reply.set_content('PING')
			display_message(self.agent, 'Turn: %s' % message.content)
			# Wait a time before send the message
			#(Do you want to see the results, do not you?)
			self.wait(0.5)
			# Sending the message
			self.agent.send(reply)


# ==== Pong Agent ====

class PongAgent(Agent):
	def setup(self):
		self.add_behaviour(PongTurn(self))

class PongTurn(CyclicBehaviour):
	def action(self):
		# Awaits for a message from self.sender
		message = self.read()
		if message.sender.getLocalName() == 'ping':
			# Preparing a reply to self.sender
			reply = message.create_reply()
			reply.set_content('PONG')
			display_message(self.agent, 'Turn: %s' % message.content)
			#self.wait(0.5)
			# Sending the reply
			self.agent.send(reply)


# ==== Starting main loop of PADE ====

if __name__ == '__main__':
	ping = PingAgent('ping')
	pong = PongAgent('pong')
	start_loop([ping, pong])
