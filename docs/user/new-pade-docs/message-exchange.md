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

This is the main method to be used when you are reading messages within behaviours. The method takes and returns only the **first message** of behaviour messages queue. A simple implementation of receiving messages can be seen bellow.

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

The `read()` method will return an `ACLMessage` object that may be handled within the behaviour. Cool.

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


## Agent Behaviours on PADE
In this session we will approach quickly the new way to program behaviours in PADE. The used paradigm is based in JADE programming, so, if you want to know more about this agent-based programing style, see some examples with behaviours in JADE.

The first one thing to keep in mind while developing behaviours is that behaviours have two important methods to be implemented. They are: `action()` and `done()` methods.

The `action()` method is the most important to be implemented, because is it that will perform the actions of the behaviour (consequently, of the agent). All "hard code" of behaviour must be put on `action()` method.

Next, the `done()` method must implements the end of the behaviour, in other words, it must to tells the PADE when a behaviour finishes its actions. This method must returns a `boolean`, which indicates if a behaviour ended by returning `True`, otherwise, returning `False`. There are cases where you don't need to implement this method, because it is predefined, as we will see later.

To better understand how PADE executes behaviours actions, the diagram bellow synthesis the behaviours cycle within PADE scheduler.

![Behaviours life cycle diagram on PADE](images/behaviours_lifecycle.png)

At each execution, a behaviour will perform its `action()` method, executing soon after its `done()` method. If the `done()` method returns `True`, the behaviour will be executed again; if the `done()` method returns `False`, the behaviour will execute its `on_end()` method and, so, will ends. The `on_end()` method can be overridden to execute post-execution actions. It is useful for signalizes when a behaviour ended of for clearing control structures used in the behaviour execution.

Basically, behaviours may be of two types: finite behaviours or infinite behaviours. They do exactly what their names mean, that is, finite behaviors end at a definite time (its `done()` method will returns `True` in a determined time) and infinite behaviors never end (its `done()` method never will returns `True`). The classes, in PADE, that implement the finite behaviours are `OneShotBehaviour` and `WakeUpBehaviour`. In its turn, the classes that implement the infinite behaviours are `CyclicBehaviour` and`TickerBehaviour`. The `SimpleBehaviour` class is a general model, while `SequentialBehaviour` class models a special type of behaviour that will be discussed later.

To further explain the features of the behaviours classes in PADE, we will see each one of them separately in the next sub-sessions.

### OneShotBehaviour class
The `OneShotBehaviour` class is a class that models finite behaviours. Its main feature is that its `done()` method always returns `True`, always ending after its first execution. Let's look at an example by writing a `OneShotBehaviour` that makes an agent say "hello world".

```python
# Needed imports
from pade.behaviours.types import OneShotBehaviour
from pade.core.agent import Agent
from pade.misc.utility import display_message, start_loop

# Defining the HelloWorldAgent (inherits from Agent class)
class HelloWorldAgent(Agent):

	# This method will execute at agent startup
	def setup(self):
		# It adds the 'SayHello' behaviour in the agent
		self.add_behaviour(SayHello(self))


# Defining the SayHello behaviour
class SayHello(OneShotBehaviour):

	# This method executes the main actions of SayHello behaviour
	def action(self):
		# It shows a message, with date/hour information, in console
		display_message(self.agent, 'Hello world!')


# It starts the agent HelloWorldAgent with PADE
if __name__ == '__main__':
	# Defining a HelloWorldAgent object
	helloagent = HelloWorldAgent('hello')
	# Creating a list with agents that will be executed
	agents_list = [helloagent]
	# Passing the agent list to main loop of PADE
	start_loop(agents_list)
```
First, we defined the `HelloWorldAgent`, adding on it the behaviours that it will execute on its startup. We did it using two methods of `Agent` class:  with `Agent.setup()` method, we are able to put any code that configure the agent in its startup, including its initial behaviours; in its turn, the `Agent.add_behaviour(BaseBehaviour)` method is used to attach a behaviour to be executed by an agent.

> The `BaseBehaviour` class is the basic class from which all other behaviours inherit from, that is, all behavior classes general type is `BaseBehaviour`.

After writing the agent, we defined the `SayHello` behaviour. The only one method needed to be implemented is the `SayHello.action()` method. This method defines the action that the agent will takes when performs this behaviour. To `OneShotBehaviour` no other method is needed to be implemented.

The last lines deal with the initiation of the agents within PADE's loop. While instantiating new agents, we need to give to they unique names. This names are passed to Agent constructor method under string form or by using an `AID` object. The `start_loop(list)` function receives a list of agents that will be executed on PADE. To start the agents, execute `pade start-runtime file_name.py` on a terminal and enjoy it!

### WakeUpBehaviour class
The `WakeUpBehaviour` too implements a finite behaviour, with the important difference that this behaviour will wait for a time to, then, perform its actions. Another important spot to focus is that this class implements its actions on `on_wake()` method, rather `action()` method. We can see an example bellow that models an agent that wait 5 seconds to do an ask.

``` python
# Needed imports
from pade.behaviours.types import WakeUpBehaviour
from pade.core.agent import Agent
from pade.misc.utility import display_message, start_loop

# Defining the LaterAgent (inherits from Agent class)
class LateAgent(Agent):

	# This method will execute at agent startup
	def setup(self):
		# The behaviour is created with two args, where
		# the second is a time (in seconds) to behaviour
		# waits.
		behaviour = AmILate(self, 5)
		# It adds a behaviour in the agent
		self.add_behaviour(behaviour)

# Defining the AmILate behaviour
class AmILate(WakeUpBehaviour):

	# This method executes the main actions of behaviour
	def on_wake(self):
		display_message(self.agent, 'Am I late?')

# It starts the agents with PADE
if __name__ == '__main__':
	# Defining a LateAgent object
	lateagent = LateAgent('late')
	# Creating a list with agents that will be executed
	agents_list = [lateagent]
	# Passing the agent list to main loop of PADE
	start_loop(agents_list)
```
Now, executing the `pade start-runtime file_name.py` command in a terminal, we will see the agent waiting 5 seconds before prints the ask "Am I late?" in the screen. However, this task is done only once, because it is a finite behaviour.

### SimpleBehaviour class
The `SimpleBehaviour` class is the simplest pre-implemented behaviour model in PADE (oh, really?). "Simple" means that you must program the `action()` and `done()` methods. The advantage of this behaviour model is that you can customize its end. Bellow there is an example where an agent counts and shows in console a counting from 1 to 10.

``` python
from pade.behaviours.types import SimpleBehaviour
from pade.core.agent import Agent
from pade.misc.utility import display, start_loop

class CounterAgent(Agent):
	def setup(self):
		self.add_behaviour(Count(self))

class Count(SimpleBehaviour):
	# Defining initial parameters to behaviour
	def __init__(self, agent):
		# This call to superclass is needed, passing the agent
		super().__init__(agent)
		# Defining counting variable
		self.counter = 1

	def action(self):
		display(self.agent, 'Counting #%d' % self.counter)
		self.counter += 1

	# This method indicates when the behaviour finishes.
	def done(self):
		if self.counter > 10:
			# The behaviour will dies when True is returned
			return True
		return False

	# This method is executed when the behaviour dies x_x
	def on_end(self):
		display(self.agent, 'Counting finished.')

if __name__ == '__main__':
	start_loop([CounterAgent('counter')])
```
This code will create an agent to count from 1 to 10. When the `CounterAgent.counter` variable reach the value 10, the `done()` method will return `True`, finishing the behaviour. We used too the `on_end()` method to signalizes when the counting is ended. 

### CyclicBehaviour class
This is a class that implements a infinite behaviours. The main difference between this class and those that implement finite behaviours (specially `OneShotBehavior`) is that the `done()` method of this class always returns `False`, never ending. The cyclic classes have a close relation with behaviours blocking and messages receiving , but it will be explained in the next docs.

Now, we will see an example of an agent that models a clock and shows a message every 1 second.

``` python
from pade.behaviours.types import CyclicBehaviour
from pade.core.agent import Agent
from pade.misc.utility import display_message, start_loop

class TicTacAgent(Agent):
	def setup(self):
		self.add_behaviour(NoiseBehaviour(self))

class NoiseBehaviour(CyclicBehaviour):
	def action(self):
		display_message(self.agent, 'Tic-tac!')
		self.wait(1) # The behaviour will sleep by 1 second

if __name__ == '__main__':
	tic = TicTacAgent('tictac')
	start_loop([tic])
```
There is not much difference between this code and the codes shown above, except that the `CyclicBehaviour` will execute indefinitely. Moreover, is common to use **blocking** and **waiting** methods with cyclic behaviours, like the `BaseBehaviour.wait(float)` method. This method will stop the behaviour until the `timeout` argument passed to it ends. It is useful, in our example, to make `TicTacAgent` shows messages within a limit of time (one second, like a clock).

### TickerBehaviour class
This is the another class that implements infinite behaviours. Like `WakeUpBehaviour`, objects from this class will wait a timeout to, then, execute its actions. The difference between the classes is that the `TickerBehaviour` will execute indefinitely. It is important to highlight that the method that implements actions on this class is the `on_tick()` method, rather `action()`.

We will remake the clock example, now using the `TickerBehaviour` class. The code follows bellow.

``` python
from pade.behaviours.types import TickerBehaviour
from pade.core.agent import Agent
from pade.misc.utility import display_message, start_loop

class TicTacAgent(Agent):
	def setup(self):
		self.add_behaviour(NoiseBehaviour(self, 1))

class NoiseBehaviour(TickerBehaviour):
	def on_tick(self):
		display_message(self.agent, 'Tic-tac!')

if __name__ == '__main__':
	start_loop([TicTacAgent('tictac')])
```

### SequentialBehaviour class
This is the most different class implementing behaviours in PADE. All behaviours in PADE are scheduled parallel, however, some times is necessary perform behaviours in a sequential mode. The `SequentialBehaviour` class implements sequential behaviours, by adding its sub-behaviours. The sub-behaviours are added one by one, following an order, which defines the order that the behaviours will be executed. 

Unlike others behaviours, a `SequentialBehaviour` does not require implementation of any of its action methods, simply adding this behaviour to an agent to run its sub-behaviours. The example bellow shows a simple implementation of this class.

``` python
from pade.behaviours.types import OneShotBehaviour, SequentialBehaviour
from pade.core.agent import Agent
from pade.misc.utility import display, start_loop

class SequentialAgent(Agent):
	def setup(self):
		# Defining the sequential behaviour
		sequential = SequentialBehaviour(self)
		# Adding sub-behaviours into 'sequential'
		sequential.add_subbehaviour(Count1_10(self))
		sequential.add_subbehaviour(Count11_20(self))
		sequential.add_subbehaviour(Count21_30(self))
		# Adding 'sequential' into agent
		self.add_behaviour(sequential)

# Behaviour that counts from 1 to 10
class Count1_10(OneShotBehaviour):
	def action(self):
		for num in range(1,11):
			display(self.agent, num)

# Behaviour that counts from 11 to 20
class Count11_20(OneShotBehaviour):
	def action(self):
		for num in range(11,21):
			display(self.agent, num)

# Behaviour that counts from 21 to 30
class Count21_30(OneShotBehaviour):
	def action(self):
		for num in range(21,31):
			display(self.agent, num)

# Starting loop
if __name__ == '__main__':
	start_loop([SequentialAgent('seq')])
```
In the above example, we used three `OneShotBehaviour` implementations that do different counting. However, the instantiation of `SequentialBehaviour` object is which defines the execution order of these behaviours. We used the `add_subbehaviour(BaseBehavior)` method to add any `BaseBehaviour` subclass as sub-behaviour of `sequential` object. The adding order defines the execution order of `sequential` sub-behaviours. To test it, try to swap the order in which the behaviours are added in `sequential` and see what happens with your counting.

Finally, we used the `Agent.add_behaviour(BaseBehaviour)` method to add the `sequential` object to the agent. At this moment, the `sequential` behaviour will execute its sub-behaviours.



> Note: You can add any `BaseBehaviour` subclass to a `SequentialBehaviour` object, however, it is recommended to use only finite behaviours. In theory, you will create a `SequentialBehaviour` object to be finalized in some time, but it will never happen if one of its sub-behaviours is a cyclic behaviour. =P

## Classes and methods
Here you will find a summary about the classes and their methods. Use it to aid your development.

### SimpleBehaviour
- **\_\_init__(agent)**:  initiate the agent.
	- _Arguments:_
		- `agent`: object from `Agent` class. Indicates which agent hold it.
	- _Returns:_
		- `None`

- **read(block = True)**:  reads the first message from the messages queue. If there is no messages to read and the `block` argument follows the standard (`True`), the method will block the behaviour until a message arrives. If the `block` argument is set to `False`, the method will try to read a message only once, and, then, can return an `ACLMessage` object or `None` object.
	- _Arguments:_
		- `block`: set the mode of the method to wait a message arrives (blocking) or not (non blocking).
	- _Returns:_
		- `ACLMessage`: if `block` argument is set to`False` and there is at least one message in the messages queue.
		- `None`: if `block` argument is set to`False` and there are no messages in the messages queue.

- **read_timeout(timeout)**: tries to read the first message from the messages queue. If there is no messages to read, the behaviour is blocked and will wait by the time passed to this method. When a timeout occurs, this method tries to read the messages queue again and can return an `ACLMessage` object, if there is at least one message in the messages queue, or `None` object, if there is no messages in the messages queue.
	- _Arguments:_
		- `timeout`: a float parameter that indicates the time that the behaviour will wait in the cases where the messages queue is empty.
	- _Returns:_
		- `ACLMessage`: if there is at least one message in the messages queue.
		- `None`: if there are no messages in the messages queue.

- **receive(message)**: receive an message and put it on the behaviours messages queue. Is used to get a message to the system and pass it to behaviours.
	- _Arguments:_
		- `message`: an`ACLMessage` object..
	- _Returns:_
		- `None`

- **action()**: executes the actions of this behaviour. Can be overridden.
	- _Returns:_
		- `None`

- **done()**: indicates when the behaviour finished its actions. Must be overridden.
	- _Returns:_
		- `bool`: by returning `True`, the behaviour will end. By returning `False`, the behaviour will execute again.

- **wait(timeout)**: stops execution of the behaviour for `timeout` seconds.
	- _Arguments:_
		- `timeout`: a float parameter that indicates the time that the behaviour will wait.
	- _Returns:_
		- `None`

- **on_end()**: last one method to be executed by a behaviour. It is executed when the behaviour ends. Can be overridden.
	- _Returns:_
		- `None`

- **has_messages()**: verifies if the messages queue of this behaviour has messages.
	- _Returns:_
		- `bool`: by returning `True`, the behaviour has messages in its queue. By returning `False`, the behaviour don't has messages in its queue.


### OneShotBehaviour
- **\_\_init__(agent)**:  initiate the agent.
	- _Arguments:_
		- `agent`: object from `Agent` class. Indicates which agent hold it.
	- _Returns:_
		- `None`

- **read(block = True)**:  reads the first message from the messages queue. If there is no messages to read and the `block` argument follows the standard (`True`), the method will block the behaviour until a message arrives. If the `block` argument is set to `False`, the method will try to read a message only once, and, then, can return an `ACLMessage` object or `None` object.
	- _Arguments:_
		- `block`: set the mode of the method to wait a message arrives (blocking) or not (non blocking).
	- _Returns:_
		- `ACLMessage`: if `block` argument is set to`False` and there is at least one message in the messages queue.
		- `None`: if `block` argument is set to`False` and there are no messages in the messages queue.

- **read_timeout(timeout)**: tries to read the first message from the messages queue. If there is no messages to read, the behaviour is blocked and will wait by the time passed to this method. When a timeout occurs, this method tries to read the messages queue again and can return an `ACLMessage` object, if there is at least one message in the messages queue, or `None` object, if there is no messages in the messages queue.
	- _Arguments:_
		- `timeout`: a float parameter that indicates the time that the behaviour will wait in the cases where the messages queue is empty.
	- _Returns:_
		- `ACLMessage`: if there is at least one message in the messages queue.
		- `None`: if there are no messages in the messages queue.

- **receive(message)**: receive an message and put it on the behaviours messages queue. Is used to get a message to the system and pass it to behaviours.
	- _Arguments:_
		- `message`: an`ACLMessage` object..
	- _Returns:_
		- `None`

- **action()**: executes the actions of this behaviour. Can be overridden.
	- _Returns:_
		- `None`

- **done()**: indicates when the behaviour finished its actions. Always returns `True`. It should not be overridden.
	- _Returns:_
		- `True`

- **wait(timeout)**: stops execution of the behaviour for `timeout` seconds.
	- _Arguments:_
		- `timeout`: a float parameter that indicates the time that the behaviour will wait.
	- _Returns:_
		- `None`

- **on_end()**: last one method to be executed by a behaviour. It is executed when the behaviour ends. Can be overridden.
	- _Returns:_
		- `None`

- **has_messages()**: verifies if the messages queue of this behaviour has messages.
	- _Returns:_
		- `bool`: by returning `True`, the behaviour has messages in its queue. By returning `False`, the behaviour don't has messages in its queue.


### CyclicBehaviour
- **\_\_init__(agent)**:  initiate the agent.
	- _Arguments:_
		- `agent`: object from `Agent` class. Indicates which agent hold it.
	- _Returns:_
		- `None`

- **read(block = True)**:  reads the first message from the messages queue. If there is no messages to read and the `block` argument follows the standard (`True`), the method will block the behaviour until a message arrives. If the `block` argument is set to `False`, the method will try to read a message only once, and, then, can return an `ACLMessage` object or `None` object.
	- _Arguments:_
		- `block`: set the mode of the method to wait a message arrives (blocking) or not (non blocking).
	- _Returns:_
		- `ACLMessage`: if `block` argument is set to`False` and there is at least one message in the messages queue.
		- `None`: if `block` argument is set to`False` and there are no messages in the messages queue.

- **read_timeout(timeout)**: tries to read the first message from the messages queue. If there is no messages to read, the behaviour is blocked and will wait by the time passed to this method. When a timeout occurs, this method tries to read the messages queue again and can return an `ACLMessage` object, if there is at least one message in the messages queue, or `None` object, if there is no messages in the messages queue.
	- _Arguments:_
		- `timeout`: a float parameter that indicates the time that the behaviour will wait in the cases where the messages queue is empty.
	- _Returns:_
		- `ACLMessage`: if there is at least one message in the messages queue.
		- `None`: if there are no messages in the messages queue.

- **receive(message)**: receive an message and put it on the behaviours messages queue. Is used to get a message to the system and pass it to behaviours.
	- _Arguments:_
		- `message`: an`ACLMessage` object..
	- _Returns:_
		- `None`

- **action()**: executes the actions of this behaviour. Can be overridden.
	- _Returns:_
		- `None`

- **done()**: indicates when the behaviour finished its actions. Always returns `False`. It should not be overridden.
	- _Returns:_
		- `False`

- **wait(timeout)**: stops execution of the behaviour for `timeout` seconds.
	- _Arguments:_
		- `timeout`: a float parameter that indicates the time that the behaviour will wait.
	- _Returns:_
		- `None`

- **on_end()**: last one method to be executed by a behaviour. It is executed when the behaviour ends. Can be overridden.
	- _Returns:_
		- `None`

- **has_messages()**: verifies if the messages queue of this behaviour has messages.
	- _Returns:_
		- `bool`: by returning `True`, the behaviour has messages in its queue. By returning `False`, the behaviour don't has messages in its queue.


### WakeUpBehaviour
- **\_\_init__(agent, time)**:  initiate the agent.
	- _Arguments:_
		- `agent`: object from `Agent` class. Indicates which agent hold it.
		- `time`: a float parameter that indicates the time that the behaviour will wait before performs its `on_wake()` method.
	- _Returns:_
		- `None`

- **read(block = True)**:  reads the first message from the messages queue. If there is no messages to read and the `block` argument follows the standard (`True`), the method will block the behaviour until a message arrives. If the `block` argument is set to `False`, the method will try to read a message only once, and, then, can return an `ACLMessage` object or `None` object.
	- _Arguments:_
		- `block`: set the mode of the method to wait a message arrives (blocking) or not (non blocking).
	- _Returns:_
		- `ACLMessage`: if `block` argument is set to`False` and there is at least one message in the messages queue.
		- `None`: if `block` argument is set to`False` and there are no messages in the messages queue.

- **read_timeout(timeout)**: tries to read the first message from the messages queue. If there is no messages to read, the behaviour is blocked and will wait by the time passed to this method. When a timeout occurs, this method tries to read the messages queue again and can return an `ACLMessage` object, if there is at least one message in the messages queue, or `None` object, if there is no messages in the messages queue.
	- _Arguments:_
		- `timeout`: a float parameter that indicates the time that the behaviour will wait in the cases where the messages queue is empty.
	- _Returns:_
		- `ACLMessage`: if there is at least one message in the messages queue.
		- `None`: if there are no messages in the messages queue.

- **receive(message)**: receive an message and put it on the behaviours messages queue. Is used to get a message to the system and pass it to behaviours.
	- _Arguments:_
		- `message`: an`ACLMessage` object..
	- _Returns:_
		- `None`

- **action()**: executes the default actions of the system. It should not be overridden.
	- _Returns:_
		- `None`

- **on_wake()**: executes the actions of this behaviour after timeout. Can be overridden.
	- _Returns:_
		- `None`

- **done()**: indicates when the behaviour finished its actions. Always returns `True`. It should not be overridden.
	- _Returns:_
		- `True`

- **wait(timeout)**: stops execution of the behaviour for `timeout` seconds.
	- _Arguments:_
		- `timeout`: a float parameter that indicates the time that the behaviour will wait.
	- _Returns:_
		- `None`

- **on_end()**: last one method to be executed by a behaviour. It is executed when the behaviour ends. Can be overridden.
	- _Returns:_
		- `None`

- **has_messages()**: verifies if the messages queue of this behaviour has messages.
	- _Returns:_
		- `bool`: by returning `True`, the behaviour has messages in its queue. By returning `False`, the behaviour don't has messages in its queue.


### TickerBehaviour
- **\_\_init__(agent, time)**:  initiate the agent.
	- _Arguments:_
		- `agent`: object from `Agent` class. Indicates which agent hold it.
		- `time`: a float parameter that indicates the time that the behaviour will wait before performs its `on_tick()` method.
	- _Returns:_
		- `None`

- **read(block = True)**:  reads the first message from the messages queue. If there is no messages to read and the `block` argument follows the standard (`True`), the method will block the behaviour until a message arrives. If the `block` argument is set to `False`, the method will try to read a message only once, and, then, can return an `ACLMessage` object or `None` object.
	- _Arguments:_
		- `block`: set the mode of the method to wait a message arrives (blocking) or not (non blocking).
	- _Returns:_
		- `ACLMessage`: if `block` argument is set to`False` and there is at least one message in the messages queue.
		- `None`: if `block` argument is set to`False` and there are no messages in the messages queue.

- **read_timeout(timeout)**: tries to read the first message from the messages queue. If there is no messages to read, the behaviour is blocked and will wait by the time passed to this method. When a timeout occurs, this method tries to read the messages queue again and can return an `ACLMessage` object, if there is at least one message in the messages queue, or `None` object, if there is no messages in the messages queue.
	- _Arguments:_
		- `timeout`: a float parameter that indicates the time that the behaviour will wait in the cases where the messages queue is empty.
	- _Returns:_
		- `ACLMessage`: if there is at least one message in the messages queue.
		- `None`: if there are no messages in the messages queue.

- **receive(message)**: receive an message and put it on the behaviours messages queue. Is used to get a message to the system and pass it to behaviours.
	- _Arguments:_
		- `message`: an`ACLMessage` object..
	- _Returns:_
		- `None`

- **action()**: executes the default actions of the system. It should not be overridden.
	- _Returns:_
		- `None`

- **on_tick()**: executes the actions of this behaviour after timeout. Can be overridden.
	- _Returns:_
		- `None`

- **done()**: indicates when the behaviour finished its actions. Always returns `False`. It should not be overridden.
	- _Returns:_
		- `False`

- **wait(timeout)**: stops execution of the behaviour for `timeout` seconds.
	- _Arguments:_
		- `timeout`: a float parameter that indicates the time that the behaviour will wait.
	- _Returns:_
		- `None`

- **on_end()**: last one method to be executed by a behaviour. It is executed when the behaviour ends. Can be overridden.
	- _Returns:_
		- `None`

- **has_messages()**: verifies if the messages queue of this behaviour has messages.
	- _Returns:_
		- `bool`: by returning `True`, the behaviour has messages in its queue. By returning `False`, the behaviour don't has messages in its queue.



### SequentialBehaviour
- **\_\_init__(agent)**:  initiate the agent.
	- _Arguments:_
		- `agent`: object from `Agent` class. Indicates which agent hold it.
	- _Returns:_
		- `None`

- **read(block = True)**:  reads the first message from the messages queue. If there is no messages to read and the `block` argument follows the standard (`True`), the method will block the behaviour until a message arrives. If the `block` argument is set to `False`, the method will try to read a message only once, and, then, can return an `ACLMessage` object or `None` object.
	- _Arguments:_
		- `block`: set the mode of the method to wait a message arrives (blocking) or not (non blocking).
	- _Returns:_
		- `ACLMessage`: if `block` argument is set to`False` and there is at least one message in the messages queue.
		- `None`: if `block` argument is set to`False` and there are no messages in the messages queue.

- **read_timeout(timeout)**: tries to read the first message from the messages queue. If there is no messages to read, the behaviour is blocked and will wait by the time passed to this method. When a timeout occurs, this method tries to read the messages queue again and can return an `ACLMessage` object, if there is at least one message in the messages queue, or `None` object, if there is no messages in the messages queue.
	- _Arguments:_
		- `timeout`: a float parameter that indicates the time that the behaviour will wait in the cases where the messages queue is empty.
	- _Returns:_
		- `ACLMessage`: if there is at least one message in the messages queue.
		- `None`: if there are no messages in the messages queue.

- **receive(message)**: receive an message and put it on the sub-behaviours messages queue. Is used to get a message to the system and pass it to its sub-behaviours.
	- _Arguments:_
		- `message`: an`ACLMessage` object..
	- _Returns:_
		- `None`

- **action()**: executes the default actions of the system. It should not be overridden.
	- _Returns:_
		- `None`

- **done()**: indicates when the behaviour finished its actions. Always returns `True`. It should not be overridden.
	- _Returns:_
		- `True`

- **wait(timeout)**: stops execution of the behaviour for `timeout` seconds.
	- _Arguments:_
		- `timeout`: a float parameter that indicates the time that the behaviour will wait.
	- _Returns:_
		- `None`

- **on_end()**: last one method to be executed by a behaviour. It is executed when the behaviour ends. Can be overridden.
	- _Returns:_
		- `None`

- **has_messages()**: verifies if the messages queue of this behaviour has messages.
	- _Returns:_
		- `bool`: by returning `True`, the behaviour has messages in its queue. By returning `False`, the behaviour don't has messages in its queue.


## Contact us
If you find a bug or need any specific help, fell free to submit us an _issue_ on [GitHub](https://github.com/italocampos/pade) or [e-mail us](mailto:italo.ramon.campos@gmail.com). If you want, fork the [original PADE project](https://github.com/grei-ufc/pade) to propose improvements and help us to make PADE better. ;)

[Laboratory of Applied Artificial Intelligence](http://www.laai.ufpa.br)
+ [Filipe Saraiva](mailto:saraiva@ufpa.br) (Project coordinator)
+ [Italo Campos](mailto:italo.ramon.campos@gmail.com) (Update programmer)

[Universidade Federal do Pará](https://portal.ufpa.br)  
Instituto de Ciências Exatas e Naturais  
Faculdade de Computação  
Belém-PA, Brasil

[comment]: # ([Federal University of Pará]\(https://portal.ufpa.br\))
[comment]: # (Exact and Natural Sciences Institute)
[comment]: # (Computation Faculty)
[comment]: # (Belém-PA, Brazil)

