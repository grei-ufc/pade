''' This example shows how TickerBehaviour works in PADE. Also, the
example shows how the message delivery systems works in PADE. Note
that no message is lost. A SenderAgent periodically sends messages to
ReceiverAgent.
'''

from pade.acl.aid import AID
from pade.acl.messages import ACLMessage
from pade.behaviours.types import OneShotBehaviour, TickerBehaviour, WakeUpBehaviour, CyclicBehaviour
from pade.core.agent import Agent
from pade.misc.utility import display_message, start_loop


class SenderAgent(Agent):
	def __init__(self, name, receiver):
		super().__init__(name)
		self.receiver = receiver # Gets the receiver AID

	def setup(self):
		self.add_behaviour(SendMessage(self, 1, 0))

class SendMessage(TickerBehaviour):
	def __init__(self, agent, time, counter):
		super().__init__(agent, time)
		self.counter = counter # Gets initial number of the counter

	def on_tick(self):
		message = ACLMessage(ACLMessage.INFORM)
		message.add_receiver(self.agent.receiver)
		message.set_content('Message #%d' % self.counter)
		self.send(message)
		self.counter += 1
		display_message(self.agent, 'Message sent to receiver.')



# Receiver Agent
class ReceiverAgent(Agent):
	def __init__(self, name, sender):
		super().__init__(name)
		self.sender = sender # Gets the local name of sender

	def setup(self):
		self.add_behaviour(ReceiveMessage(self))

class ReceiveMessage(CyclicBehaviour):
	def action(self):
		message = self.read()
		if message.sender.getLocalName() == self.agent.sender:
			display_message(self.agent, 'This is:  %s.' % message.content)



if __name__ == '__main__':
	receiver = ReceiverAgent('receiver', 'sender')
	sender = SenderAgent('sender', receiver.aid)
	start_loop([receiver, sender])
