''' This example shows how the data serialization works. Users send
requests to contact book about contacts information.
'''

from pade.acl.messages import ACLMessage
from pade.acl.filters import Filter
from pade.behaviours.types import OneShotBehaviour, CyclicBehaviour
from pade.core.agent import Agent
from pade.misc.utility import display, start_loop
# We use pickle ;)
import pickle


# User Agent
class User(Agent):
	def __init__(self, aid, contact_name, contact_book):
		super().__init__(aid)
		self.contact_name = contact_name.lower() # The name to be searched in the ContactBook
		self.contact_book = contact_book # Gets the AID of ContactBook

	def setup(self):
		self.add_behaviour(Search(self))
		self.add_behaviour(ShowInfos(self))


class Search(OneShotBehaviour):
	def action(self):
		message = ACLMessage(ACLMessage.REQUEST)
		message.add_receiver(self.agent.contact_book)
		message.set_content(self.agent.contact_name)
		self.agent.send(message)
		display(self.agent, "I requested for %s's contact." % self.agent.contact_name)


class ShowInfos(CyclicBehaviour):
	def action(self):
		message = self.agent.receive()
		if message != None:
			# Deserializing the received information
			contact = pickle.loads(message.content)
			if message.get_performative() == ACLMessage.INFORM:
				template = 'Contact info: \nName: {name}\nPhone: {phone}\nE-mail: {email}'
				# Showing the deserialized data
				display(self.agent, template.format(
					name=contact['name'],
					phone=contact['phone'],
					email=contact['email'])
				)
			elif message.performative == ACLMessage.FAILURE:
				# Showing the failure information
				display(self.agent, '{id}: {desc}'.format(
					id=contact['error'],
					desc=contact['description'])
				)
		else:
			self.block()



# Contact Book Agent
class ContactBook(Agent):
	def __init__(self, aid):
		super().__init__(aid)
		# Defining the contact list
		self.contacts = [
			{'name': 'ana', 'phone': '11 9999-5555', 'email': 'ana@example.com'},
			{'name': 'beto', 'phone': '11 8888-4444', 'email': 'beto@example.com'},
			{'name': 'charlot', 'phone': '11 7777-3333', 'email': ''},
			{'name': 'diego', 'phone': '11 6666-2222', 'email': 'diego@example.com'},
			{'name': 'sandra', 'phone': '11 5555-1111', 'email': 'sandra@example.com'},
		]

	def setup(self):
		self.add_behaviour(SearchContact(self))


# Behaviour that deal with the received contact requests
class SearchContact(CyclicBehaviour):
	def action(self):
		message_filter = Filter()
		message_filter.set_performative(ACLMessage.REQUEST)
		message = self.agent.receive(message_filter)
		if message != None:
			reply = message.create_reply() # Creates a reply to the sender
			contact = self.search(message.get_content())
			if contact != None: # If the searched contact exists
				# Setting the performative of the reply to INFORM
				reply.set_performative(ACLMessage.INFORM)
				# Here we will serialize the object to send
				reply.set_content(pickle.dumps(contact))
			else: # If the searched contact doesn't exist
				# Setting the performative of the reply to FAILURE
				reply.set_performative(ACLMessage.FAILURE)
				# Adding the reason of the FAILURE (using a dict)
				reply.set_content(pickle.dumps({'error': 404, 'description': 'Contact not found.'}))
			self.agent.send(reply)
		else:
			# Blocks the behaviour until the next message
			self.block()

	def search(self, name):
		for contact in self.agent.contacts:
			if name == contact['name']:
				return contact
		return None



if __name__ == '__main__':
	agents = list()
	contact_book = ContactBook('book')
	agents.append(contact_book)
	agents.append(User('user-1', 'charlot', contact_book.aid))
	agents.append(User('user-2', 'diego', contact_book.aid))
	agents.append(User('user-3', 'italo', contact_book.aid))
	agents.append(User('user-4', 'sandra', contact_book.aid))
	agents.append(User('user-5', 'ana', contact_book.aid))
	agents.append(User('user-6', 'beto', contact_book.aid))
	start_loop(agents)