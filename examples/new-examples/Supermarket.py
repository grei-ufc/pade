from pade.acl.aid import AID
from pade.acl.messages import ACLMessage
from pade.acl.filters import Filter
from pade.behaviours.types import OneShotBehaviour, CyclicBehaviour
from pade.core.agent import Agent
from pade.misc.utility import display, start_loop


# Customer Agent
class Customer(Agent):
	def __init__(self, aid, session):
		super().__init__(aid)
		self.session = session.lower()

	def setup(self):
		self.add_behaviour(RequestList(self))
		self.add_behaviour(PrintList(self))

class RequestList(OneShotBehaviour):
	def action(self):
		message = ACLMessage(ACLMessage.REQUEST)
		message.add_receiver(AID('supermarket'))
		message.set_ontology(self.agent.session) # Defines the tipe of list required
		message.set_content('Please, give me this list')
		self.send(message)
		display(self.agent, 'I requested for %s products.' % self.agent.session)

class PrintList(OneShotBehaviour):
	def action(self):
		# Setting a filter
		f = Filter()
		f.set_performative(ACLMessage.INFORM) # Accept only INFORM messages
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

# Behaviour that deal with fruit requisitions
class FruitList(CyclicBehaviour):
	def action(self):
		# Setting a filter
		f = Filter()
		f.set_performative(ACLMessage.REQUEST) # Accept only REQUEST messages
		f.set_ontology('fruits')

		# Reveiving a message and filtering it
		message = self.read()
		if f.filter(message): # If the message satisfies the filter
			reply = message.create_reply()
			reply.set_content('apple\nbanana\ncocoa\ncoconuts\ngrape\norange\nstrawberry')
			reply.set_performative(ACLMessage.INFORM)
			self.send(reply)
			display(self.agent, 'Fruit list sent to %s.' % message.sender.getLocalName())

# Behaviour that deal with food requisitions
class FoodList(CyclicBehaviour):
	def action(self):
		f = Filter()
		f.set_performative(ACLMessage.REQUEST)
		f.set_ontology('foods')
		message = self.read()
		if f.filter(message): # If the message satisfies the filter
			reply = message.create_reply()
			reply.set_content('meat\nchicken\ncookies\nice cream\nbread')
			reply.set_performative(ACLMessage.INFORM)
			self.send(reply)
			display(self.agent, 'Food list sent to %s.' % message.sender.getLocalName())

# Behaviour that deal with office requisitions
class OfficeList(CyclicBehaviour):
	def action(self):
		f = Filter()
		f.set_performative(ACLMessage.REQUEST)
		f.set_ontology('office')
		message = self.read()
		if f.filter(message):
			reply = message.create_reply()
			reply.set_content('pen\nclips\nscissors\npaper\npencil')
			reply.set_performative(ACLMessage.INFORM)
			self.send(reply)
			display(self.agent, 'Office material list sent to %s.' % message.sender.getLocalName())

# Behaviour that deal with any requisitions
class UnknownList(CyclicBehaviour):
	def action(self):
		message = self.read()
		if not message.ontology in ['fruits', 'foods', 'office']:
			reply = message.create_reply()
			reply.set_content('Unknown list')
			reply.set_performative(ACLMessage.INFORM)
			self.send(reply)
			display(self.agent, 'Unknown requisition')


if __name__ == '__main__':
	agents = list()
	# Instantiating customers
	agents.append(Customer('customer-1', 'office'))
	agents.append(Customer('customer-2', 'house'))
	agents.append(Customer('customer-3', 'fruits'))
	agents.append(Customer('customer-4', 'foods'))
	# Instantiating the supermarket
	agents.append(Supermarket('supermarket'))
	start_loop(agents)