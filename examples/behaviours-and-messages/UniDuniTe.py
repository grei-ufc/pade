''' This example shows how all the messages reaches correctly the
SequentialBehaviour sub-behaviours. An agent sends a message to other
in a different order than the expected. All the messages should be handled.
'''

from pade.behaviours.types import OneShotBehaviour, SequentialBehaviour, SimpleBehaviour
from pade.acl.messages import ACLMessage
from pade.acl.filters import Filter
from pade.core.agent import Agent
from pade.misc.utility import display, start_loop

# The sender agent
class Sender(Agent):
	def __init__(self, aid, receiver):
		super().__init__(aid)
		self.receiver = receiver

	def setup(self):
		self.add_behaviour(SendMessage(self))


# The behaviour that send the messages
class SendMessage(OneShotBehaviour):
	def action(self):
		# Sending the first message
		message1 = ACLMessage(ACLMessage.INFORM)
		message1.set_protocol('tê')
		message1.set_content('tê')
		message1.add_receiver(self.agent.receiver)
		self.agent.send(message1)
		display(self.agent, 'I sent "tê".')
		# Waits for a time
		self.wait(2)

		# Sending the second message
		message2 = ACLMessage(ACLMessage.INFORM)
		message2.set_protocol('duni')
		message2.set_content('duni')
		message2.add_receiver(self.agent.receiver)
		self.agent.send(message2)
		display(self.agent, 'I sent "duni".')
		# Waits for another another time
		self.wait(2)

		# Sending the third message
		message3 = ACLMessage(ACLMessage.INFORM)
		message3.set_protocol('uni')
		message3.set_content('uni')
		message3.add_receiver(self.agent.receiver)
		self.agent.send(message3)
		display(self.agent, 'I sent "uni".')


# The receiver agent
class Receiver(Agent):
	def setup(self):
		self.add_behaviour(BlockBehaviour(self))

	def setup(self):
		# These behaviours will receive the messages in the reverse
		# sending order due to its addiction in the SequentialBehaviour
		sequential = SequentialBehaviour(self)
		sequential.add_subbehaviour(ReceiveMessage(self, 'uni'))
		sequential.add_subbehaviour(ReceiveMessage(self, 'duni'))
		sequential.add_subbehaviour(ReceiveMessage(self, 'tê'))
		self.add_behaviour(sequential)


# The behaviour that receive messages
class ReceiveMessage(SimpleBehaviour):
	def __init__(self, agent, word):
		super().__init__(agent)
		self.word = word
		self._done = False

	def action(self):
		msg_filter = Filter()
		msg_filter.set_performative(ACLMessage.INFORM)
		msg_filter.set_protocol(self.word)
		message = self.agent.receive(msg_filter)
		if message != None:
			display(self.agent, message.get_content().upper() + '!')
			self._done = True
		else:
			self.block()

	def done(self):
		return self._done


if __name__ == '__main__':
	receiver = Receiver('receiver')
	sender = Sender('sender', receiver.aid)
	start_loop([sender, receiver])