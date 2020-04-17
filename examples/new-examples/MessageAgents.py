from pade.acl.aid import AID
from pade.acl.messages import ACLMessage
from pade.behaviours.types import OneShotBehaviour, CyclicBehaviour
from pade.core.agent import Agent
from pade.misc.utility import display, start_loop


# Customer Agent
class SenderAgent(Agent):
	def setup(self):
		self.add_behaviour(SendMessage(self))

class SendMessage(OneShotBehaviour):
	def action(self):
		message = ACLMessage(ACLMessage.INFORM)
		message.add_receiver(AID('receiver'))
		message.set_content('Hello! :)')
		self.send(message)
		display(self.agent, 'I sent a message to receiver.')


# Receiver Agent
class ReceiverAgent(Agent):
	def setup(self):
		self.add_behaviour(ReceiveMessage(self))

class ReceiveMessage(CyclicBehaviour):
	def action(self):
		message = self.read()
		display(self.agent, 'I received a message with the content: %s.' % message.content)


if __name__ == '__main__':
	agents = list()
	agents.append(ReceiverAgent('receiver'))
	agents.append(SenderAgent('sender'))
	start_loop(agents)