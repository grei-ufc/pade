# Message Exchange
##### PADE Update (LAAI | UFPA), released at 4-22-2019, updated at 4-24-2020



## Content
- [Introduction](#introduction)
- [The read() methods](#the-read-methods)
- [Filtering messages](#filtering-messages)
- [Passing objects into messages](#passing-objects-into-messages)
- [Contact us](#contact-us)



## Introduction

This doc explains the message exchange between agents in PADE. We will consider that you already have some experience with behaviours in PADE. If don't, consider to read the documentation related to this.

The message exchange style in PADE is similar to the style used in [JADE](https://jade.tilab.com/), with few differences. Below we have sections that explains separately each feature of message exchanging.


## The _read\()_ methods

This is the main set of methods to be used when you are reading messages within behaviours. These methods lie in _Behaviour_ classes and their main function is take and return the **first message** from behaviour messages queue. As a first step, let's to see a simple implementation of receiving messages using the default `read()` method.

``` python
from pade.behaviours.types import CyclicBehaviour
from pade.core.agent import Agent
from pade.misc.utility import display, start_loop


class ReceiverAgent(Agent):
	def setup(self):
		self.add_behaviour(ReceiveMessage(self))


class ReceiveMessage(CyclicBehaviour):
	def action(self):
		message = self.read() # Receives the message here
		display(self.agent, 'I received a message with the content: %s' % message.content)


if __name__ == '__main__':
	start_loop([ReceiverAgent('agent')])
```

The `read()` method will return an `ACLMessage` object that may be handled within the `ReceiveMessage` behaviour. Cool! However, let's to create an agent to send something to our `ReceiverAgent`. Adding some code to the above code, we can watch the magic happen.

``` python
from pade.acl.messages import ACLMessage
from pade.behaviours.types import OneShotBehaviour, CyclicBehaviour
from pade.core.agent import Agent
from pade.misc.utility import display, start_loop


# Sender Agent
class SenderAgent(Agent):
	# We need to get the receiver AID. We did it in the __init__() method
	def __init__(self, name, receiver):
		# This super().__init__() call is needed
		super().__init__(name)
		self.receiver = receiver # Gets the receiver address (AID)

	def setup(self):
		# Adds the SendMessage behaviour
		self.add_behaviour(SendMessage(self))

class SendMessage(OneShotBehaviour):
	def action(self):
		# Create a message with INFORM performative
		message = ACLMessage(ACLMessage.INFORM)
		# Adds the address (AID) of the message recipient
		message.add_receiver(self.agent.receiver)
		# Adds some content
		message.set_content('Hello! :)')
		# Send the message to receiver
		self.send(message)
		display(self.agent, 'I sent a message to receiver.')


# Receiver Agent
class ReceiverAgent(Agent):
	def setup(self):
		# Adds the ReceiveMessage behaviour
		self.add_behaviour(ReceiveMessage(self))

class ReceiveMessage(CyclicBehaviour):
	def action(self):
		# Receives (reads) the message from queue
		message = self.read()
		# Shows the message content
		display(self.agent, 'I received a message with the content: %s.' % message.content)


if __name__ == '__main__':
	agents = list()
	# Creates a ReceiverAgent object
	receiver = ReceiverAgent('receiver')
	# Creates a SenderAgent object, passing the receiver AID
	sender = SenderAgent('sender', receiver.aid)
	start_loop([receiver, sender])
```

To send a message in PADE, we need to add the address of the message recipient. That address is the AID, an unique agent identifier which ensures the correct delivery of the messages in the system.  You can add an AID in a message with the `ACLMessage.add_recipient(AID)` method.

The `read()` method reads the message queue and return the first message, if it exists. If not, the `read()` will block the behaviour and wait for a message to arrive. When that happens, the `read()` will return the message. We say, then, that the read() method blocks the behaviour.

An important spot to highlight is that the `read()` method has three variants, which differ in the way the agent waits for a message. These three variants are described below.

- **read(_block_ = True)**: This is the default method used within behaviours (equivalent to `read()`). Using this method, the _behaviour will stay blocked_ until it receives a message in its message queue. When you are using this method, it is not needed to handle its return, because it will always return an `ACLMessage` object, never `None`.

- **read(_block_ = False)**: When you use this method, the behaviour _will not block_. The behaviour will attempt to read its message queue once. If the queue has messages, the method will return the first one in an `ACLMessage` object; if the message queue is empty, the method will return `None`.

- **read_timeout(_timeout_)**: By using this method, you will need to pass it a _timeout_ argument. When called, the method will try to read the message queue once. If the queue has messages, the method will return the first one; otherwise, the method will wait for _timeout_ seconds and attempt to read the queue again. If the queue remains empty, the method returns `None`; otherwise, returns an `ACLMessage` with the read message. 

Then, when you are programming with the `read()` method, be careful about using each `read()` type: you may need some handling for `None` objects depending the chosen method.

Next, we present an example that models a call center. Each attendant often check the call queue. If the queue is empty, the attendant waits by 3 seconds and, if the queue remains empty, then he/she goes drink water and returns after 10 seconds. The customer who calls the call center waits for a response and, after being answered, ends the call. This example give us some idea about how the `read()` methods work.

``` python
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
		# If there is at least a call to reply...
		if call != None: # You must handle None objects when using read_timeout()
			reply = call.create_reply() # Creates a reply
			reply.set_content('Here is your help.')
			self.send(reply) # Sends the reply
			display_message(self.agent, 'Help sent to %s.' % call.sender.getName())
		else:
			# Goes to drink water
			display_message(self.agent, 'I am going to drink water.')
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
		display_message(self.agent, 'I am making a call.')


class CloseCall(OneShotBehaviour):
	def action(self):
		# The customer only ends the call when gets a response
		response = self.read()
		# You don't need to handle None objects, because the read()
		# method always returns an ACLMessage object. The behaviour
		# will remain blocked until a message arrives.
		display_message(self.agent, 'I received help and I am closing the call. Thank you. =)')
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
```

Note that the attendant doesn't waits indefinitely, it uses the `read_timeout(timeout)` method and waits for a time interval. In other hand, the customers wait indefinitely for a response of attendants, using the `read()` method. The `read(block = False)` method works similarly to `read_timeout(timeout)`. The difference between them is that the `read(block = False)` method doesn't wait any time, but immediately returns an `ACLMessage` or a `None` object.



## Filtering messages

Message filtering is very useful when programming agents, as the agents receive too many messages during its life cycle. In PADE, the filtering can be made within behaviours, choosing the better treating for each type of received message.

The filtering is implemented by the `pade.acl.filter.Filter` class and uses an object to 'models' the type of message that you want to receive. To clarify, the code below shows a implementation of a customer that requests a product list from a supermarket, filtering through sessions.

```python
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

class PrintList(OneShotBehaviour):
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
		f.set_ontology('fruits') # Only accept messagens with 'fruits' in ontology field

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
		f.set_ontology('foods')
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
		f.set_ontology('office')
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
	agents.append(Customer('customer-2', 'house', supermarket.aid))
	agents.append(Customer('customer-3', 'fruits', supermarket.aid))
	agents.append(Customer('customer-4', 'foods', supermarket.aid))

	# Initiating loop with the passed agents
	start_loop(agents)
```

Note that each behaviour that handles different customers requests has a specific filter. The `ACLMessage` fields used to filter the messages were two: `performative` and `ontology` (if you want, see FIPA ACL fields specifications for a more detailed explanation about these fields). More fields can be used to filter messages in PADE; we listed them below:

- `performative`: A constant that describes the communicative act (see FIPA specifications);
- `sender`: An AID object that describes the message sender;
- `conversation_id`: A string used to specify an identifier to the conversation;
- `protocol`: A string used to specify the message protocol;
- `ontology`: A string used to specify the ontology;
- `language`: A string used to specify the language used in the message.



## Passing objects into messages

Messages in PADE are transported under string form. Then, we can't simply pass complex objects to other agents within messages. To do this, we need of **serialization**, which consists of passing the object data in bytes form. Here we use `pickle` library, that works well by serializing many types of data. However, you can use any other that you prefer. To use `pickle`, two methods are the most important: `pickle.dumps(data)`, which serializes the data, and; `pickle.loads(serialized_data)` that deserializes the data to the original object form.

Knowing it, we are able to solve a lot of problems involving the data exchange in multi-agent systems. To give you an example, we will model a contact book that answers the requests of users for contact data. These responses are passed under Python dictionaries. See the code below:

``` python
from pade.acl.messages import ACLMessage
from pade.acl.filters import Filter
from pade.behaviours.types import OneShotBehaviour, CyclicBehaviour
from pade.core.agent import Agent
from pade.misc.utility import display, start_loop
# We use pickle ;)
import pickle


# User Agent
class User(Agent):
	def __init__(self, aid, name, contact_book):
		super().__init__(aid)
		self.name = name.lower() # The name to be searched in the ContactBook
		self.contact_book = contact_book # Gets the AID of ContactBook

	def setup(self):
		self.add_behaviour(Search(self))
		self.add_behaviour(ShowInfos(self))

class Search(OneShotBehaviour):
	def action(self):
		message = ACLMessage(ACLMessage.REQUEST)
		message.add_receiver(self.agent.contact_book)
		message.set_content(self.agent.name)
		self.send(message)
		display(self.agent, "I requested for %s's contact." % self.agent.name)

class ShowInfos(OneShotBehaviour):
	def action(self):
		message = self.read()
		# Deserializing the received information
		contact = pickle.loads(message.content)
		# Filtering the message
		f = Filter()
		f.set_performative(ACLMessage.INFORM)
		if f.filter(message):
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
			reply = message.create_reply() # Creates a reply to sender
			contact = self.search(message.content)
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
			self.send(reply)

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
```

The `SearchContact` behaviour receives requests and answers to them by serializing a dictionary with contact information. After, the behaviour sends the reply to the requester. The `ShowInfos` behaviour, in its turn, gets the serialized information and deserializes it into a dictionary again. Then, the behaviour shows the correct contact information in the screen. Note that we used the `ACLMessage.performative` field to control when a contact is found or not. ;)


## Contact us
All the presented code examples can be found at the `pade/examples/behaviours-and-messages/` directory of this repository.

That is all. We hope you enjoy PADE. If you find a bug or need any specific help, feel free to visit us or submit an _issue_ on [GitHub](https://github.com/grei-ufc/pade). We appreciate contributions to make PADE better. ;)

> Written by [@italocampos](https://github.com/italocampos) with [StackEdit](https://stackedit.io/).

---

[Universidade Federal do Pará](https://portal.ufpa.br)  
[Laboratory of Applied Artificial Intelligence](http://www.laai.ufpa.br)
Instituto de Ciências Exatas e Naturais  
Faculdade de Computação  
Belém-PA, Brasil  

[Universidade Federal do Ceará](http://www.ufc.br/)  
[Grupo de Redes Elétricas Inteligentes](https://github.com/grei-ufc)  
Fortaleza-CE, Brasil