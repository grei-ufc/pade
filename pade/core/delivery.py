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

Message delivery module
-----------------------

This module contains the implementation of the message delivery service. If an
agent is unable to receive messages, this behaviour will postpone the message
and retry to send it, within a timeout. If the receiver is not available at the
timeout, the message is discarded.

@author: Italo Campos
"""

import datetime, queue
from pade.behaviours.types import CyclicBehaviour
from pade.misc.utility import display_message

class MessageDelivery(CyclicBehaviour):
	''' This class implements a default behaviour to ensure the messages
	delivery.

	MessageDelivery class executes the attempt to deliver a message to another
	agent. The sent messages remains in a queue until the max_wait time is
	reached.

	Attributes
	----------
	queue : queue.Queue
		The queue that saves the postponed messages.
	max_wait : float
		The max time to wait the receiver stay available.
	'''

	def __init__(self, agent, max_wait):
		'''
		Parameters
		----------
		agent : Agent
			The agent that executes the behaviour.
		max_wait : float
			The max time to wait the receiver stay available.
		'''

		super().__init__(agent)
		self.queue = queue.Queue()
		self.max_wait = max_wait


	def action(self):
		''' Runs the actions of the message delivery service.
		'''

		self.wait(0.5)
		package = self.queue.get()
		elapsed_time = datetime.datetime.now() - package['time_stamp']
		if elapsed_time.total_seconds() <= self.max_wait:
			if not self.agent.receiver_available(package['message'].receivers[0]):
				self.queue.put(package)
			else:
				self.agent.send(package['message'])
		else:
			display_message(self.agent, 'A message could not be delivered to the receiver %s.' % package['message'].receivers[0].getName())


	def deliver(self, message):
		''' Puts a message in the delivery queue.

		This method pack the passed message in a dict. This package allows the
		message to be managed by the service with a timestamp.

		Parameters
		----------
		message : ACLMessage
			The postponed message to be delivered.
		'''

		self.queue.put({'message': message,	'time_stamp': datetime.datetime.now()})