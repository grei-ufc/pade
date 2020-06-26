''' This example shows how the read_timeout() method works. This
example models an attendant that goes to drink water in each 3
seconds, and returns to attend customers. The customers request,
at different times, the call center services.
'''

from pade.acl.messages import ACLMessage
from pade.behaviours.types import CyclicBehaviour, WakeUpBehaviour
from pade.core.agent import Agent
from pade.misc.utility import display_message, start_loop


# Attendant Agent
class Attendant(Agent):
	def setup(self):
		self.add_behaviour(CheckQueue(self))


class CheckQueue(CyclicBehaviour):
	def action(self):
		# Receives a call
		call = self.agent.receive()
		# If there is at least one call to reply...
		if call != None: # You must handle None objects when using the receive method
			reply = call.create_reply() # Creates a reply
			reply.set_content('Here is your help.')
			self.agent.send(reply) # Sends the reply
			display_message(self.agent, 'Help sent to %s.' % call.sender.getName())
		# If there is no call to answer
		else:
			# Goes drink water by 10 seconds
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
		self.attendant = attendant # The address (AID) of attendant

	def setup(self):
		self.add_behaviour(Call(self, self.time))
		self.add_behaviour(CloseCall(self))


class Call(WakeUpBehaviour):
	def on_wake(self):
		# Preparing a message
		call = ACLMessage(ACLMessage.REQUEST)
		call.set_content('I need help!')
		call.add_receiver(self.agent.attendant)
		self.agent.send(call) # Sending a message
		display_message(self.agent, "I'm calling the Call Center.")


class CloseCall(CyclicBehaviour):
	def action(self):
		# The customer only ends the call when gets a response
		response = self.agent.receive()
		# If there's a response to this customer
		if response != None:
			display_message(self.agent, "I received help and I'm closing the call. Thank you. =)")
			display_message(self.agent, 'Help content: %s' % response.content)
		# If there is no messages still, the behaviour will block
		else:
			# Blocks the behaviour until a message arrives
			self.block()


if __name__ == '__main__':
	agents = list()
	# Creating an attendant agent
	attendant = Attendant('attendant')
	agents.append(attendant)
	# Passing the attendant address for each customer (attendant.aid)
	agents.append(Customer('customer-1', 2, attendant.aid))
	agents.append(Customer('customer-2', 10, attendant.aid))
	agents.append(Customer('customer-3', 20, attendant.aid))
	start_loop(agents)