# Doc 2: Message Exchange
##### PADE Update (LAAI | UFPA), released at 4-22-2019



## Content
- [Introduction](#introduction)
- [The read() methods](#the-read-methods)
- [Filtering messages](#cyclic-behaviours-and-messages)
- [Passing objects into messages](#passing-objects-into-messages)
- [Contact us](#contact-us)


## Introduction
This is the second part of PADE documentation after the updates provided by [LAAI](http://www.laai.ufpa.br/) Research Group. If you did not read the first part of this documentation (which explains behaviours in PADE), we recommend you to see this [doc first](https://github.com/italocampos/pade/blob/master/docs/user/new-pade-docs/pade-updates.md). 

This doc explains the message exchange between agents in PADE, taking into account the style of behaviours programing proposed by this update. We will consider that you already have some experience with message exchange in PADE, if don't, see the [main PADE doc](https://github.com/italocampos/pade/blob/master/docs/user/enviando-mensagens.rst).


## The _read\()_ methods

This is the main set of methods to be used when you are reading messages within behaviours. These methods lie in _Behaviour_ classes and their main function is take and return the **first message** from behaviour messages queue. As a first step, let's to see a simple implementation of receiving messages using de default `read()` method.

``` python
from pade.behaviours.types import CyclicBehaviour
from pade.core.agent import Agent
from pade.misc.utility import display, start_loop


class ReceiverAgent(Agent):
	def setup(self):
		self.add_behaviour(ReceiveMessage(self))


class ReceiveMessage(CyclicBehaviour):
	def action(self):
		message = self.read()
		display(self.agent, 'I received a message with the content: %s' % message.content)


if __name__ == '__main__':
	start_loop([ReceiverAgent('agent')])
```

The `read()` method will return an `ACLMessage` object that may be handled within the behaviour. Cool! However, let's to create an agent to send something to our `ReceiverAgent`. Add some code to above code and watch the magic happen.

``` python
from pade.acl.aid import AID
from pade.acl.messages import ACLMessage
from pade.behaviours.types import OneShotBehaviour, CyclicBehaviour
from pade.core.agent import Agent
from pade.misc.utility import display, start_loop


# Sender Agent
class SenderAgent(Agent):
	def setup(self):
		self.add_behaviour(SendMessage(self))

class SendMessage(OneShotBehaviour):
	def action(self):
		message = ACLMessage(ACLMessage.INFORM)
		message.add_receiver(AID('receiver'))
		message.set_content('Hello! :)')
		self.agent.send(message)
		display(self.agent, 'I sent a message to receiver.')


# Receiver Agent
class ReceiverAgent(Agent):
	def setup(self):
		self.add_behaviour(ReceiveMessage(self))

class ReceiveMessage(CyclicBehaviour):
	def action(self):
		message = self.read()
		display(self.agent, 'I received a message with the content: %s.' % message.content)


if __name__ == '__main__':
	agents = list()
	agents.append(ReceiverAgent('receiver'))
	agents.append(SenderAgent('sender'))
	start_loop(agents)
```
The `read()` method read the message queue on behaviour and return the first message, if it exists. If not, the `read()` will wait for a message arrival to, then, return it. The read() method, so, blocks the behaviour.

An important spot to highlight is that the `read()` method has three variants, which differ in the form how the agent waits for a message (is blocked). These three variants are described bellow.

- **read(_block_ = True)**: It is the default method used within behaviours (it is equivalent to `read()`). Using this method, the _behaviour will block_ until receive a message in its message queue and return it. When you are using this method, it is not needed to handle its return, because it will always return an `ACLMessage` object, never `None`.

- **read(_block_ = False)**: When you use this method, the behaviour _will not block_ and will attempt to read its message queue once. If the queue has at least one message, the method will return an `ACLMessage`; if the message queue is empty, the method will return `None`.

- **read_timeout(_timeout_)**: By using this method, you will need to pass it a _timeout_ argument. When called, the method will try to read the message queue once. If the queue has messages, the method will return the first; if does not, the method will wait for _timeout_ seconds and attempt to read the queue again. If the queue remains empty, the method returns `None`; otherwise, returns an `ACLMessage`. 

So, when you are programming with the `read()` method, be careful about using each `read()` type, for you may need some handling for `None` objects.

Next, we present an example that models a call center. Each attendant often check the call queue. If the queue is empty, the attendant waits by 3 seconds and, if the queue remains empty, then he/she goes drink water and returns after 10 seconds. The customer, who called to call center, waits by a response and, after the service, ends the call. This example give us some idea about how the `read()` methods work.

``` python
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
```
Note that the attendant doesn't waits indefinitely, but, using the `read_timeout(timeout)` method, waits for a time interval. In other hand, the customers wait indefinitely for a response of attendants, using the `read()` method. The `read(block = False)` method works similarly to `read_timeout(timeout)`, but, waits for no time, immediately returning an `ACLMessage` or a `None` object.


## Filtering messages
Message filtering is so useful to agent programming, once the agents receive messages during all of its life cycle. In PADE, the filtering can be made within behaviours, choosing the better treating for each message type received.

The filtering is implemented by the `pade.acl.filter.Filter` class and uses an object to 'model' the type of message that you want to receive. To clarify, the code below shows a implementation of a customer that request a product list from a supermarket, filtering through sessions.

```python
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
		self.agent.send(message)
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
			self.agent.send(reply)
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
			self.agent.send(reply)
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
			self.agent.send(reply)
			display(self.agent, 'Office material list sent to %s.' % message.sender.getLocalName())

# Behaviour that deal with any requisitions
class UnknownList(CyclicBehaviour):
	def action(self):
		message = self.read()
		if not message.ontology in ['fruits', 'foods', 'office']:
			reply = message.create_reply()
			reply.set_content('Unknown list')
			reply.set_performative(ACLMessage.INFORM)
			self.agent.send(reply)
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
```

Note that in each behaviour that handles the customer request, there is a specific filter. The `ACLMessage` fields used to filter the message were two: `performative` and `ontology` (if you want, see FIPA ACL fields specifications for a more detailed explanation about these fields). More fields can be used to filter messages in PADE; we listed them below:

- `sender`: An AID object that describes the message sender;
- `performative`: A constant that describes the communicative act (see FIPA specifications);
- `protocol`: A string used to specify the message protocol;
- `ontology`: A string used to specify the ontology;
- `sender_local_name`: A string used to specify  the local name of an agent. This field has less priority than `sender` field, i. e., if there is a value to `sender`, this field will not be used.

## Passing objects into messages
Messages in PADE are transported under string form. Then, we can't simply pass complex objects to other agents within messages. To do this, we need of **serialization**, which consists of passing the object data in bytes form. We use, by default, the `pickle` library, that works well by serializing many types of data. Two methods are the most important: `pickle.dumps(data)`, which serializes the data, and; `pickle.loads(serialized_data)` that de-serializes data to normal object form.

Knowing it, we are able to solve a lot of problems involving the data exchange in multiagent systems. To give you an example, we will model a contact book that answers the requests of users for contact data. These responses are passed under Python dictionaries. See the code below:

``` python
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
```
The `SearchContact` behaviour receives requests and answers them by serializing the contact information and sending it to requester. The `ShowInfos` behaviour, in its turn, gets the serialized information and de-serializes it into a dictionary to, then, shows the correct contact information. Note that we used the `ACLMessage.performative` field to control when a contact is found or not. ;)


## Contact us
That is all. We hope you enjoy PADE. If you find a bug or need any specific help, fell free to submit us an _issue_ on [GitHub](https://github.com/italocampos/pade) or [e-mail us](mailto:italo.ramon.campos@gmail.com). If you want, fork the [original PADE project](https://github.com/grei-ufc/pade) to propose improvements and help us to make PADE better. ;)

[Laboratory of Applied Artificial Intelligence](http://www.laai.ufpa.br)
+ [Filipe Saraiva](mailto:saraiva@ufpa.br) (Project coordinator)
+ [Italo Campos](mailto:italo.ramon.campos@gmail.com) (Update programmer)

[Universidade Federal do Pará](https://portal.ufpa.br)  
Instituto de Ciências Exatas e Naturais  
Faculdade de Computação  
Belém-PA, Brasil  

[Universidade Federal do Ceará](http://www.ufc.br/)  
[Grupo de Redes Elétricas Inteligentes](https://github.com/grei-ufc)  
Fortaleza-CE, Brasil  

[comment]: # ([Federal University of Pará]\(https://portal.ufpa.br\))  
[comment]: # (Exact and Natural Sciences Institute)  
[comment]: # (Computation Faculty)  
[comment]: # (Belém-PA, Brazil)  

[comment]: # ([Federal University of Ceará]\(http://www.ufc.br/\)\)  
[comment]: # ([Smart Grids Group]\(https://github.com/grei-ufc\)\)  
[comment]: # ()  
[comment]: # ()  
[comment]: # (Fortaleza-CE, Brazil)  
