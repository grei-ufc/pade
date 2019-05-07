from pade.acl.aid import AID
from pade.acl.messages import ACLMessage
from pade.behaviours.types import CyclicBehaviour, WakeUpBehaviour, OneShotBehaviour
from pade.core.agent import Agent
from pade.misc.utility import display_message, start_loop


# Attendant Agent
class Attendant(Agent):
	def setup(self):
		self.add_behaviour(CheckQueue(self))

class CheckQueue(CyclicBehaviour):
	def action(self):
		# Waits for a call by 3 seconds (using the read_timeout() method)
		call = self.read_timeout(3)
		# If there is at least a call to reply...
		if call != None: # You must handle None objects when using read_timeout()
			reply = call.create_reply() # Create a reply
			reply.set_content('Here is your help.')
			self.agent.send(reply) # Sending the reply
			display_message(self.agent, 'Help sent to %s.' % call.sender.getLocalName())
		else:
			# Goes drink water
			display_message(self.agent, 'I am going to drink water.')
			self.wait(10)
			display_message(self.agent, 'I returned from water. e.e')


# Customer Agent
class Customer(Agent):
	def __init__(self, aid, time):
		super().__init__(aid)
		self.time = time # The time to customer make a call

	def setup(self):
		self.add_behaviour(Call(self, self.time))
		self.add_behaviour(CloseCall(self))

class Call(WakeUpBehaviour):
	def on_wake(self):
		# Preparing a message
		call = ACLMessage(ACLMessage.REQUEST)
		call.set_content('I need help!')
		call.add_receiver('attendant')
		self.agent.send(call) # Sending a message
		display_message(self.agent, 'I am making a call.')


class CloseCall(OneShotBehaviour):
	def action(self):
		# The customer only ends the call when gets a response
		response = self.read()
		# You don't need to handle None objects, because read() returns always ACLMessage objects
		display_message(self.agent, 'I received help and I am closing the call. Thank you. =)')
		display_message(self.agent, 'Help content: %s' % response.content)


if __name__ == '__main__':
	agents = list()
	agents.append(Attendant('attendant'))
	agents.append(Customer('customer-1', 2))
	agents.append(Customer('customer-2', 10))
	agents.append(Customer('customer-3', 20))
	start_loop(agents)