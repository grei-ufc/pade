''' This example shows how the message exchange works in PADE. The
SenderAgent sends a message to ReceiverAgent.
'''

from pade.acl.messages import ACLMessage
from pade.behaviours.types import OneShotBehaviour, CyclicBehaviour
from pade.core.agent import Agent
from pade.misc.utility import display, start_loop


# Sender Agent
class SenderAgent(Agent):
	# We need to get the receiver AID. We did it in the __init__() method
	def __init__(self, name, receiver):
		# This super().__init__() call is needed
		super().__init__(name)
		self.receiver = receiver # Gets the receiver address (AID)

	def setup(self):
		# Adds the SendMessage behaviour
		self.add_behaviour(SendMessage(self))

class SendMessage(OneShotBehaviour):
	def action(self):
		# Create a message with INFORM performative
		message = ACLMessage(ACLMessage.INFORM)
		# Adds the address (AID) of the message recipient
		message.add_receiver(self.agent.receiver)
		# Adds some content
		message.set_content('Hello! :)')
		# Send the message to receiver
		self.agent.send(message)
		display(self.agent, 'I sent a message to receiver.')


# Receiver Agent
class ReceiverAgent(Agent):
	def setup(self):
		# Adds the ReceiveMessage behaviour
		self.add_behaviour(ReceiveMessage(self))

class ReceiveMessage(CyclicBehaviour):
	def action(self):
		# Receives the message from queue
		message = self.agent.receive()
		# If there is messages to receive
		if message != None:
			# Shows the message content
			display(self.agent, 'I received a message with the content: %s.' % message.content)
		else:
			# Blocks the behaviour until the next message arrives
			self.block()


if __name__ == '__main__':
	agents = list()
	# Creates a ReceiverAgent object
	receiver = ReceiverAgent('receiver')
	# Creates a SenderAgent object, passing the receiver AID
	sender = SenderAgent('sender', receiver.aid)
	start_loop([receiver, sender])
