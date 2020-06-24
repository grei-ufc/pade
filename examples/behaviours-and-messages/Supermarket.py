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
		self.send(message)
		display(self.agent, 'I requested for %s products.' % self.agent.section)

class PrintList(CyclicBehaviour):
	def action(self):
		# Setting a filter
		f = Filter()
		# The object 'f' is the 'model' of message you want to receive
		f.set_performative(ACLMessage.INFORM) # The filter only accept INFORM messages
		message = self.read()
		if f.filter(message): # Filtering the message
			display(self.agent, 'I received this list: \n%s' % message.content)


# Supermarket Agent
class Supermarket(Agent):
	def setup(self):
		self.add_behaviour(FruitList(self))
		self.add_behaviour(FoodList(self))
		self.add_behaviour(OfficeList(self))
		self.add_behaviour(UnknownList(self))

# Behaviour that deals with fruit requisitions
class FruitList(CyclicBehaviour):
	def action(self):
		# Setting the filter
		f = Filter()
		# The object 'f' is the 'model' of message you want to receive
		f.set_performative(ACLMessage.REQUEST) # Only accept REQUEST messages
		f.set_protocol('fruits') # Only accept messagens with 'fruits' in ontology field

		# Receiving a message
		message = self.read()
		# Filtering the received message based on 'f' filter
		if f.filter(message): # If the message satisfies the filter 'f'
			reply = message.create_reply() # Creates a reply to the sender
			reply.set_content('apple\nbanana\ncocoa\ncoconuts\ngrape\norange\nstrawberry')
			reply.set_performative(ACLMessage.INFORM)
			self.send(reply) # Sends the reply to the sender
			display(self.agent, 'Fruit list sent to %s.' % message.sender.getName())

# Behaviour that deals with food requisitions
class FoodList(CyclicBehaviour):
	def action(self):
		# Setting the filter
		f = Filter()
		f.set_performative(ACLMessage.REQUEST)
		f.set_protocol('foods')
		message = self.read()

		# Filtering the received message
		if f.filter(message): # If the message satisfies the filter 'f'
			reply = message.create_reply()
			reply.set_content('meat\nchicken\ncookies\nice cream\nbread')
			reply.set_performative(ACLMessage.INFORM)
			self.send(reply)
			display(self.agent, 'Food list sent to %s.' % message.sender.getName())

# Behaviour that deals with office requisitions
class OfficeList(CyclicBehaviour):
	def action(self):
		# Setting the filter
		f = Filter()
		f.set_performative(ACLMessage.REQUEST)
		f.set_protocol('office')
		message = self.read()

		# Filtering the received message
		if f.filter(message):
			reply = message.create_reply()
			reply.set_content('pen\nclips\nscissors\npaper\npencil')
			reply.set_performative(ACLMessage.INFORM)
			self.send(reply)
			display(self.agent, 'Office material list sent to %s.' % message.sender.getName())

# Behaviour that deals with any other requisition
class UnknownList(CyclicBehaviour):
	def action(self):
		message = self.read()

		# Filtering the received message manually
		if not message.get_protocol() in ['fruits', 'foods', 'office']:
			reply = message.create_reply()
			reply.set_content('Unknown list')
			reply.set_performative(ACLMessage.INFORM)
			self.send(reply)
			display(self.agent, 'Unknown requisition')


if __name__ == '__main__':
	agents = list()

	# Instantiating the supermarket
	supermarket = Supermarket('supermarket')
	# Puting the supermarket agent in the list of execution
	agents.append(supermarket)

	# Instantiating customers and passing the supermarket AID to them
	agents.append(Customer('customer-1', 'office', supermarket.aid))
	agents.append(Customer('customer-2', 'house', supermarket.aid))
	agents.append(Customer('customer-3', 'fruits', supermarket.aid))
	agents.append(Customer('customer-4', 'foods', supermarket.aid))

	# Initiating loop with the passed agents
	start_loop(agents)