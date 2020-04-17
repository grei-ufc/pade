from pade.acl.aid import AID
from pade.acl.messages import ACLMessage
from pade.behaviours.types import OneShotBehaviour, TickerBehaviour, WakeUpBehaviour, CyclicBehaviour
from pade.core.agent import Agent
from pade.misc.utility import display_message, start_loop


class SenderAgent(Agent):
	def setup(self):
		self.add_behaviour(SendMessage(self, 1, 0))

class SendMessage(TickerBehaviour):
	def __init__(self, agent, time, counter):
		super().__init__(agent, time)
		self.counter = counter

	def on_tick(self):
		message = ACLMessage(ACLMessage.INFORM)
		message.add_receiver(AID('receiver'))
		message.set_content('Message #%d' % self.counter)
		self.send(message)
		self.counter += 1
		display_message(self.agent, 'Message sent to receiver.')



# Receiver Agent
class ReceiverAgent(Agent):
	def setup(self):
		self.add_behaviour(ReceiveMessage(self))

class ReceiveMessage(CyclicBehaviour):
	def action(self):
		message = self.read()
		if message.sender.getLocalName() == 'sender':
			display_message(self.agent, 'This is:  %s.' % message.content)

if __name__ == '__main__':
	agents = list()
	agents.append(ReceiverAgent('receiver'))
	agents.append(SenderAgent('sender'))
	start_loop(agents)
