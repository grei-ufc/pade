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
		message.set_ontology(self.agent.section) # Defines the type of list required
		message.set_content('Please, give me this list')
		self.send(message)
		display(self.agent, 'I requested for %s products.' % self.agent.section)

class PrintList(CyclicBehaviour):
	def action(self):
		# Setting a filter
		f = Filter()
		# The object 'f' is the 'model' of message you want to receive
		f.set_ontology(self.agent.section) # The filter only accept agent's section messages
		if self.agent.has_messages():
			message = self.agent.read(f)
			if message != None: # Filtering the message
				display(self.agent, 'I received this list: \n%s' % message.content)


# Supermarket Agent
class Supermarket(Agent):
	def setup(self):
		self.add_behaviour(FruitList(self))
		self.add_behaviour(FoodList(self))
		self.add_behaviour(OfficeList(self))
		#self.add_behaviour(UnknownList(self)) # Removed because we don't have a 'not' filter yet

# Behaviour that deals with fruit requisitions
class FruitList(CyclicBehaviour):
	def action(self):
		# Setting the filter
		f = Filter()
		# The object 'f' is the 'model' of message you want to receive
		f.set_performative(ACLMessage.REQUEST) # Only accept REQUEST messages
		f.set_ontology('fruits') # Only accept messagens with 'fruits' in ontology field
		
		# Filtering the received message based on 'f' filter
		if self.agent.has_messages(): # If the message satisfies the filter 'f'
			message = self.agent.read(f)
			if message != None:
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
		f.set_ontology('foods')
		
		# Filtering the received message based on 'f' filter
		if self.agent.has_messages(): # If the message satisfies the filter 'f'
			message = self.agent.read(f)
			if message != None:
				reply = message.create_reply() # Creates a reply to the sender
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
		f.set_ontology('office')
		
		# Filtering the received message based on 'f' filter
		if self.agent.has_messages(): # If the message satisfies the filter 'f'
			message = self.agent.read(f)
			if message != None:
				reply = message.create_reply() # Creates a reply to the sender
				reply = message.create_reply()
				reply.set_content('pen\nclips\nscissors\npaper\npencil')
				reply.set_performative(ACLMessage.INFORM)
				self.send(reply)
				display(self.agent, 'Office material list sent to %s.' % message.sender.getName())

# Behaviour that deals with any other requisition
class UnknownList(CyclicBehaviour):
	def action(self):
		if self.agent.has_messages():
			message = self.agent.read()
			
			# Filtering the received message manually
			if not message.ontology in ['fruits', 'foods', 'office']:
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
	#agents.append(Customer('customer-2', 'house', supermarket.aid)) # Removed because we don't have a 'not' filter yet
	agents.append(Customer('customer-3', 'fruits', supermarket.aid))
	agents.append(Customer('customer-4', 'foods', supermarket.aid))

	# Initiating loop with the passed agents
	start_loop(agents)
