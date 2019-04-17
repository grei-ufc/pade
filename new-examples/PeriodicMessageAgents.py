from pade.acl.aid import AID
from pade.acl.messages import ACLMessage
from pade.behaviours.types import OneShotBehaviour, TickerBehaviour, WakeUpBehaviour, CyclicBehaviour
from pade.core.agent import Agent
from pade.misc.utility import display_message, start_loop


class SenderAgent(Agent):
	def setup(self):
		#self.add_behaviour(SendMessage(self))
		self.add_behaviour(SendMessageLater(self, 10))


class ReceiverAgent(Agent):
	def setup(self):
		self.add_behaviour(ReceiveMessage(self))


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
		message.add_receiver(AID('pong'))
		message.set_content('Message #%d' % self.counter)
		self.agent.send(message)
		display_message(self.agent, 'Message sent to pong.')


class SendMessageLater(WakeUpBehaviour):
	def __init__(self, agent, time):
		super().__init__(agent, time)

	def on_wake(self):
		self.agent.add_behaviour(SendMessage(self.agent, 0))
		self.agent.add_behaviour(ResendMessage(self.agent, 1))


class ReceiveMessage(CyclicBehaviour):
	def action(self):
		#display_message(self.agent, 'The message queue has size %d' % len(self.messages))
		#display_message(self.agent, 'SIZE: %d' % len(self.messages))
		message = self.read()
		if message != None and message.sender.getLocalName() == 'ping':
			display_message(self.agent, 'This is:  %s.' % message.content)
		else:
			#self.sleep(0.5)
			self.block()


if __name__ == '__main__':
	agents = list()
	agents.append(ReceiverAgent('pong'))
	agents.append(SenderAgent('ping'))
	start_loop(agents)
