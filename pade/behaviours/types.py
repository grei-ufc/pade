"""Framework for Intelligent Agents Development - PADE

The MIT License (MIT)

Copyright (c) 2019 Lucas S Melo

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

Behaviour types module
----------------------

This module implements the BaseBehaviour class extensions. These subclasses are
used to model the agent behaviours of various types.

@author: Italo Campos
"""

from pade.behaviours.base import BaseBehaviour
from pade.acl.messages import ACLMessage


class SimpleBehaviour(BaseBehaviour):
	''' Class that implements the SimpleBehaviour.

	SimpleBehaviour class models a basic behaviour. The action() method must be
	overridden in the subclasses to define the behaviour actions. The done()
	method must indicate (by returning True) when this behaviour will finalize.
	'''

	def action(self):
		'''  An abstract method that performs the actions of the behaviour.

		This method can be overridden in the subclasses.
		'''

		pass


	def done(self):
		''' Defines when the behaviour ends.

		This method must be overridden in the subclasses, defining exactly when
		the behaviour will ends (by returning True).
		'''

		pass



class OneShotBehaviour(BaseBehaviour):
	''' This class models a finite behaviour.

	OneShotBehaviour are behaviours that executes its action() method only 
	once.
	'''

	def action(self):
		'''  An abstract method that performs the actions of the behaviour.

		This method can be overridden in the subclasses.
		'''

		pass


	def done(self):
		''' Defines when the behaviour ends.

		This method always returns True and should not be overridden in the
		subclasses. By returning True, the behaviour will execute only once.
		'''

		return True



class CyclicBehaviour(BaseBehaviour):
	''' This class models an infinite behaviour.

	CyclicBehaviour are behaviours that executes its action() method until the
	end of the agent.
	'''

	def action(self):
		'''  An abstract method that performs the actions of the behaviour.

		This method can be overridden in the subclasses.
		'''

		pass


	def done(self):
		''' Defines when the behaviour ends.

		This method always returns False and should not be overridden in the
		subclasses. By returning False, the behaviour will execute
		indefinitely.
		'''

		return False



class WakeUpBehaviour(OneShotBehaviour):
	''' This class models a finite behaviour that waits a timeout before
	performs its actions.

	WakeUpBehaviour class models a finite behaviour that executes its actions
	after a timeout. The actions of this class must be implemented into the
	on_wake() method.

	Attributes
	----------
	time : float
		The amount of time (in seconds) to be waited before the behaviour
		performs its actions.
	'''

	def __init__(self, agent, time):
		'''
		Parameters
		----------
		agent : Agent
			The agent that executes the behaviour.
		time : float
			The amount of time (in seconds) to be waited before the behaviour
			performs its actions.
		'''

		super().__init__(agent)
		self.time = time


	def action(self):
		''' This method performs the actions of the behaviour.

		This method should not be overridden in the subclasses. Use the method
		on_wake() to write the actions of this behaviour.
		'''

		self.wait(self.time)
		self.on_wake()


	def on_wake(self):
		'''  An abstract method that performs the actions of the behaviour.

		This method can be overridden in the subclasses.
		'''

		pass



class TickerBehaviour(CyclicBehaviour):
	''' This class models an infinite behaviour that waits a timeout before
	performs its actions.

	TickerBehaviour class models an infinite behaviour that always waits a
	timeout before execute its actions. The actions of this class must be
	implemented into the on_tick() method.

	Attributes
	----------
	time : float
		The amount of time (in seconds) to be waited before each execution of
		the behaviour.
	'''

	def __init__(self, agent, time):
		'''
		Parameters
		----------
		agent : Agent
			The agent that executes the behaviour.
		time : float
			The amount of time (in seconds) to be waited before each execution
			of the behaviour.
		'''

		super().__init__(agent)
		self.time = time


	def action(self):
		''' This method performs the actions of the behaviour.

		This method should not be overridden in the subclasses. Use the method
		on_tick() to write the actions of this behaviour.
		'''

		self.wait(self.time)
		self.on_tick()


	def on_tick(self):
		'''  An abstract method that performs the actions of the behaviour.

		This method can be overridden in the subclasses.
		'''

		pass



class SequentialBehaviour(OneShotBehaviour):
	''' This class models the sequential-compound behaviours in PADE.

	SequentialBehaviour models a sequential-compound behaviour. This classe
	adds other non-compound behaviours (like OneShotBehaviour or 
	SimpleBehaviour) as sub-behaviours, and performs them sequentially. The
	execution order is defined as the sub-behavious are added. No overrides are
	required for this class.

	Attributes
	----------
	_subbehaviours : list
		The list of added subbehaviours.
	'''

	def __init__(self, agent):
		'''
		Parameters
		----------
		agent : Agent
			The agent that holds the behaviour.
		'''

		super().__init__(agent)
		self.subbehaviours = list()


	def action(self):
		''' This method performs the actions of the behaviour.

		This method executes sequentially the sub-behaviours. This method
		should not be overridden in the subclasses.
		'''

		for behaviour in self.subbehaviours:
			behaviour.action()
			while not behaviour.done():
				behaviour.action()
			behaviour.on_end()


	def add_subbehaviour(self, behaviour):
		''' Adds sub-behaviours in this sub-behaviour local list.

		Parameters
		----------
		behaviour : BaseBehaviour
			The behaviour to be added as sub-behaviour.
		'''

		self.subbehaviours.append(behaviour)


	def receive(self, message):
		''' Passes the received message to the sub-behaviours.

		Parameters
		----------
		message : ACLMessage
			The message to be passed to the sub-behaviours.

		Raises
		------
		ValueError
			If the passed object is not an ACLMessage.
		'''
		
		if isinstance(message, ACLMessage):
			for behaviour in self.subbehaviours:
				behaviour.messages.put(message)
		else:
			raise ValueError('message object type must be ACLMessage!')