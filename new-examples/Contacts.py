from pade.acl.aid import AID
from pade.acl.messages import ACLMessage
from pade.acl.filters import Filter
from pade.behaviours.types import OneShotBehaviour, CyclicBehaviour
from pade.core.agent import Agent
from pade.misc.utility import display, start_loop
# We use pickle ;)
import pickle


# User Agent
class User(Agent):
	def __init__(self, aid, name):
		super().__init__(aid)
		self.name = name.lower()

	def setup(self):
		self.add_behaviour(Search(self))
		self.add_behaviour(ShowInfos(self))

class Search(OneShotBehaviour):
	def action(self):
		message = ACLMessage(ACLMessage.REQUEST)
		message.add_receiver(AID('book'))
		message.set_content(self.agent.name)
		self.agent.send(message)
		display(self.agent, "I requested for %s's contact." % self.agent.name)

class ShowInfos(OneShotBehaviour):
	def action(self):
		message = self.read()
		# Deserializing the information
		contact = pickle.loads(message.content)
		# Filtering the message in a non-elegant way (use for one field only)
		if message.performative == ACLMessage.INFORM:
			form = "Contact info: \nName: {name}\nPhone: {phone}\nE-mail: {email}"
			display(self.agent, form.format(
				name=contact['name'],
				phone=contact['phone'],
				email=contact['email'])
			)
		elif message.performative == ACLMessage.FAILURE:
			display(self.agent, '{id}: {desc}'.format(
				id=contact['error'],
				desc=contact['description'])
			)


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

# Behaviour that deal with contact requisitions
class SearchContact(CyclicBehaviour):
	def action(self):
		f = Filter()
		f.set_performative(ACLMessage.REQUEST)
		message = self.read()
		if f.filter(message):
			reply = message.create_reply()
			contact = self.search(message.content)
			if contact != None: # If the searched contact exists
				reply.set_performative(ACLMessage.INFORM)
				# Here we will serialize the object to send
				reply.set_content(pickle.dumps(contact))
			else: # If the searched contact doesn't exist
				reply.set_performative(ACLMessage.FAILURE)
				reply.set_content(pickle.dumps({'error': 404, 'description': 'Contact not found.'}))
			self.agent.send(reply)

	def search(self, name):
		for contact in self.agent.contacts:
			if name == contact['name']:
				return contact
		return None



if __name__ == '__main__':
	agents = list()
	agents.append(User('user-1', 'charlot'))
	agents.append(User('user-2', 'diego'))
	agents.append(User('user-3', 'italo'))
	agents.append(User('user-4', 'sandra'))
	agents.append(User('user-5', 'ana'))
	agents.append(User('user-6', 'beto'))
	agents.append(ContactBook('book'))
	start_loop(agents)