from pade.acl.aid import AID
from pade.acl.messages import ACLMessage
from pade.behaviours.types import WakeUpBehaviour, CyclicBehaviour
from pade.core.agent import Agent
from pade.misc.utility import display_message, start_loop


# Sender Agent
class SenderAgent(Agent):
	def setup(self):
		self.add_behaviour(SendMessageLater(self, 10))

class SendMessageLater(WakeUpBehaviour):
	def on_wake(self):
		message = ACLMessage(ACLMessage.INFORM)
		message.add_receiver(AID('pong'))
		message.set_content('Hello, pong, ping is here!')
		self.agent.send(message)
		display_message(self.agent, 'Message sent to pong.')


# Receiver Agent
class ReceiverAgent(Agent):
	def setup(self):
		self.add_behaviour(ReceiveMessage(self))

class ReceiveMessage(CyclicBehaviour):
	def action(self):
		message = self.read()
		if message.sender.getLocalName() == 'ping':
			display_message(self.agent, 'I received a message from %s.' % message.sender.getLocalName())
		else:
			display_message(self.agent, 'I received a message from another agent.')


if __name__ == '__main__':
	agents = list()
	agents.append(ReceiverAgent('pong'))
	agents.append(SenderAgent('ping'))
	start_loop(agents)