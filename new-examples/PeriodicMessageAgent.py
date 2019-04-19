from pade.acl.aid import AID
from pade.acl.messages import ACLMessage
from pade.behaviours.types import OneShotBehaviour, TickerBehaviour, WakeUpBehaviour, CyclicBehaviour
from pade.core.agent import Agent
from pade.misc.utility import display_message, start_loop


class SenderAgent(Agent):
	def setup(self):
		self.add_behaviour(SendMessageLater(self, 10))


class ResendMessage(TickerBehaviour):
	def __init__(self, agent, time):
		super().__init__(agent, time)
		self.counter = 1

	def on_tick(self):
		self.agent.add_behaviour(SendMessage(self.agent, self.counter))
		self.counter += 1

class SendMessage(OneShotBehaviour):
	def __init__(self, agent, counter):
		super().__init__(agent)
		self.counter = counter

	def action(self):
		message = ACLMessage(ACLMessage.INFORM)
		message.add_receiver(AID('receiver'))
		message.set_content('Message #%d' % self.counter)
		self.agent.send(message)
		display_message(self.agent, 'Message sent to pong.')

class SendMessageLater(WakeUpBehaviour):
	def on_wake(self):
		self.agent.add_behaviour(SendMessage(self.agent, 0))
		self.agent.add_behaviour(ResendMessage(self.agent, 0.5))


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
