''' This example shows how the data serialization works. Customers
send requests to supermarket about products from specific sections.
'''

from pade.acl.messages import ACLMessage
from pade.acl.filters import Filter
from pade.behaviours.types import OneShotBehaviour, CyclicBehaviour
from pade.core.agent import Agent
from pade.misc.utility import display, start_loop


# Customer Agent
class Customer(Agent):
	def __init__(self, aid, section, supermarket_aid):
		super().__init__(aid)
		self.section = section.lower()
		self.supermarket = supermarket_aid # Gets the AID of supermarket

	def setup(self):
		self.add_behaviour(RequestList(self))
		self.add_behaviour(PrintList(self))


class RequestList(OneShotBehaviour):
	def action(self):
		message = ACLMessage(ACLMessage.REQUEST)
		message.add_receiver(self.agent.supermarket)
		message.set_protocol(self.agent.section) # Defines the type of list required
		message.set_content('Please, give me this list')
		self.agent.send(message)
		display(self.agent, 'I requested for %s products.' % self.agent.section)


class PrintList(CyclicBehaviour):
	def action(self):
		# Setting a filter
		message_filter = Filter()
		# The object 'message_filter' is the 'model' of message you want to receive
		# The filter only accepts the agent's section messages
		message_filter.set_protocol(self.agent.section)
		# Receives only messages that matches the filter
		message = self.agent.receive(message_filter)
		if message != None: # If the method returns a message
			display(self.agent, 'I received this list: \n%s' % message.content)
		else:
			# Blocks the behaviour until the next message arrives
			self.block()



# Supermarket Agent
class Supermarket(Agent):
	def setup(self):
		self.add_behaviour(FruitList(self))
		self.add_behaviour(FoodList(self))
		self.add_behaviour(OfficeList(self))
		#self.add_behaviour(UnknownList(self))
		''' The behaviour above is consuming all the received
		messages before it reaches the target behaviour. This happens
		due to the UnknownList doesn't have filters, getting all the
		messages that arrives. This is a weak point of this
		implementation, requiring robust filters when dealing with
		many message exchange. '''


# Behaviour that deals with fruit requisitions
class FruitList(CyclicBehaviour):
	def action(self):
		# Setting the filter
		message_filter = Filter()
		# The object 'message_filter' is the 'model' of message you want to receive
		message_filter.set_performative(ACLMessage.REQUEST) # Only accept REQUEST messages
		message_filter.set_protocol('fruits') # Only accept messagens with 'fruits' in protocol field

		# Filtering the received message based on 'message_filter' filter
		message = self.agent.receive(message_filter)
		if message != None: # If a message was returned
			reply = message.create_reply() # Creates a reply to the sender
			reply.set_content('apple\nbanana\ncocoa\ncoconuts\ngrape\norange\nstrawberry')
			reply.set_performative(ACLMessage.INFORM)
			self.agent.send(reply) # Sends the reply to the sender
			display(self.agent, 'Fruit list sent to %s.' % message.sender.getName())
		else:
			# Blocks the behaviour until the next message arrives
			self.block()


# Behaviour that deals with food requisitions
class FoodList(CyclicBehaviour):
	def action(self):
		# Setting the filter
		message_filter = Filter()
		message_filter.set_performative(ACLMessage.REQUEST)
		message_filter.set_protocol('foods')

		# Filtering the received message based on 'message_filter' filter
		message = self.agent.receive(message_filter)
		# If there is messages that matches the filter
		if message != None:
			reply = message.create_reply() # Creates a reply to the sender
			reply.set_content('meat\nchicken\ncookies\nice cream\nbread')
			reply.set_performative(ACLMessage.INFORM)
			self.agent.send(reply)
			display(self.agent, 'Food list sent to %s.' % message.sender.getName())
		else:
			# Blocks the behaviour until the next message arrives
			self.block()


# Behaviour that deals with office requisitions
class OfficeList(CyclicBehaviour):
	def action(self):
		# Setting the filter
		message_filter = Filter()
		message_filter.set_performative(ACLMessage.REQUEST)
		message_filter.set_protocol('office')

		# Filtering the received message based on 'message_filter' filter
		message = self.agent.receive(message_filter)
		if message != None:
			reply = message.create_reply() # Creates a reply to the sender
			reply.set_content('pen\nclips\nscissors\npaper\npencil')
			reply.set_performative(ACLMessage.INFORM)
			self.agent.send(reply)
			display(self.agent, 'Office material list sent to %s.' % message.sender.getName())
		else:
			# Blocks the behaviour until the next message arrives
			self.block()


# Behaviour that deals with any other requisition
class UnknownList(CyclicBehaviour):
	def action(self):
		message = self.agent.receive()
		if message != None:	
			# Filtering the received message manually
			if not message.get_protocol() in ['fruits', 'foods', 'office']:
				reply = message.create_reply()
				reply.set_content('Unknown list')
				reply.set_performative(ACLMessage.INFORM)
				self.agent.send(reply)
				display(self.agent, 'Unknown requisition')
		else:
			# Blocks the behaviour until a new massage arrives
			self.block()


if __name__ == '__main__':
	agents = list()

	# Instantiating the supermarket
	supermarket = Supermarket('supermarket')
	# Puting the supermarket agent in the list of execution
	agents.append(supermarket)

	# Instantiating customers and passing the supermarket AID to them
	agents.append(Customer('customer-1', 'office', supermarket.aid))
	#agents.append(Customer('customer-2', 'house', supermarket.aid))
	agents.append(Customer('customer-3', 'fruits', supermarket.aid))
	agents.append(Customer('customer-4', 'foods', supermarket.aid))

	# Initiating loop with the passed agents
	start_loop(agents)
