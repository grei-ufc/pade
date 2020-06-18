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

Behaviours module
-----------------

This module implements the base of the Behaviours classes, in order to enable
the PADE Scheduler to manage the agent behaviours.

@author: Italo Campos
"""

from pade.behaviours.protocols import Behaviour
from pade.acl.messages import ACLMessage
import queue, time

class BaseBehaviour(Behaviour):
	''' The basic behaviour class.

	This class inherits from Behaviour class and implements the basic methods
	for scheduled behaviours.

	Attributes
	----------
	_messages : list
		The behaviour local message queue.
	_lock : threding.Lock()
		The lock object used to implement mutual exclusion.
	'''

	def __init__(self, agent):
		'''
		Parameters
		----------
		agent : Agent
			The agent which performs the behaviour.
		'''

		super().__init__(agent)
		# Queue of received messages by the agent and unread by this behaviour
		self._messages = queue.Queue()
		self._lock = None


	def read(self, block = True):
		''' Reads a message from the local queue.

		It gets the first message in the local message queue. It waits (by
		default) to receive a message, in case of the queue is empty.

		Parameters
		----------
		block : bool, optional
			Defines wheter the behaviour will block (block = True) or not
			(block = False) when the local message queue is empty (default is
			True).

		Returns
		-------
		ACLMessage
			The read message from the local queue.
		'''

		if block:
			return self._messages.get()
		else:
			try:
				return self._messages.get_nowait()
			except queue.Empty:
				return None


	def send(self, message):
		''' Sends a message for other agents.

		This method gets a message and passes it to self.agent.send() method.
		It was coded just to complement the pair read/send in the BaseBehaviour class.
		The method self.agent.send() can still be used directly in the code.

		Parameters
		----------
		message : ACLMessage
			The message to be sent.
		'''

		self.agent.send(message)


	def read_timeout(self, timeout):
		''' Reads the local queue waiting for a defined timeout.

		It tries to read the message queue twice until the end of timeout. In
		case of no messages, this method returns None.

		Parameters
		----------
		timeout : float
			The max timeout to wait when reading the local message queue.

		Returns
		-------
		ACLMessage
			The read message from the local queue.
		None
			In case of no messages in queue at the end of the timeout.
		'''

		message = self.read(block = False)
		if message != None:
			return message
		else:
			time.sleep(timeout)
			return self.read(block = False)


	def receive(self, message):
		''' Sets a new message in the local messages queue.

		Parameters
		----------
		message : ACLMessage
			The message to be put in the queue.

		Raises
		------
		ValueError
			If the passed object not is an ACLMessage object.
		'''

		if isinstance(message, ACLMessage):
			self._messages.put(message)
		else:
			raise ValueError('message object type must be ACLMessage!')



	def action(self):
		''' An abstract method that performs the actions of the behaviour.

		This method must be overridden in the subclasses.
		'''

		pass


	def done(self):
		''' Defines when the behaviour ends.

		This method must be overridden in the subclasses.
		'''

		pass


	def wait(self, timeout):
		''' Sleeps a behaviour until occurs a timeout.

		Parameters
		----------
		timeout : float
			The time to be waited.
		'''

		time.sleep(timeout)


	def on_end(self):
		''' Executes the final actions of the behaviou.

		The scheduler will call this method after the behaviour ends. May be
		overriden in subclasses.
		'''

		pass


	def has_messages(self):
		''' Checks whether the behaviour has messages in its messages queue.

		Returns
		-------
		bool
			True if the queue has messages; False otherwise.
		'''

		return self._messages.qsize() != 0


	def add_lock(self, lock):
		''' Adds a threading.Lock object to this behaviour.

		This allows the behaviour to execute the mutual exclusion.

		Parameters
		----------
		lock : threadong.Lock
			The lock object.
		'''

		self._lock = lock
	
	@property	
	def lock(self):
		''' Returns the added lock object.

		Raises
		------
		AttributeError
			If there is no a lock object added.

		Returns
		-------
		threading.Lock
			The local lock object.
		'''
		
		if self._lock != None:
			return self._lock
		else:
			raise(AttributeError('No such lock object added to this behaviour.'))