''' This example shows how the read_timeout() method works. This
example models an attendant that goes to drink water in each 3
seconds, and returns to attend customers. The customers request,
at different times, the call center services.
'''

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
		# Waits for a call for 3 seconds (using the read_timeout() method)
		call = self.read_timeout(3)
		# If there is at least one call to reply...
		if call != None: # You must handle None objects when using read_timeout()
			reply = call.create_reply() # Creates a reply
			reply.set_content('Here is your help.')
			self.send(reply) # Sends the reply
			display_message(self.agent, 'Help sent to %s.' % call.sender.getName())
		else:
			# Goes to drink water
			display_message(self.agent, "I'm gonna drink water.")
			self.wait(10)
			display_message(self.agent, 'I returned from water. e.e')


# Customer Agent
class Customer(Agent):
	# We're using the __init__() method to handle the input 
	# parameters for this agent
	def __init__(self, aid, time, attendant):
		# This super().__init__(aid) call is needed
		super().__init__(aid)
		self.time = time # The time to customer make a call
		self.attendant = attendant # The address of attendant

	def setup(self):
		self.add_behaviour(Call(self, self.time))
		self.add_behaviour(CloseCall(self))

class Call(WakeUpBehaviour):
	def on_wake(self):
		# Preparing a message
		call = ACLMessage(ACLMessage.REQUEST)
		call.set_content('I need help!')
		call.add_receiver(self.agent.attendant)
		self.send(call) # Sending a message
		display_message(self.agent, "I'm making a call.")


class CloseCall(OneShotBehaviour):
	def action(self):
		# The customer only ends the call when gets a response
		response = self.read()
		# You don't need to handle None objects, because the read()
		# method always returns an ACLMessage object. The behaviour
		# will remain blocked until a message arrives.
		display_message(self.agent, " received help and I'm closing the call. Thank you. =)")
		display_message(self.agent, 'Help content: %s' % response.content)


if __name__ == '__main__':
	agents = list()
	attendant = Attendant('attendant')
	agents.append(attendant)
	# Passing the attendant address for each customer
	agents.append(Customer('customer-1', 2, attendant.aid))
	agents.append(Customer('customer-2', 10, attendant.aid))
	agents.append(Customer('customer-3', 20, attendant.aid))
	start_loop(agents)