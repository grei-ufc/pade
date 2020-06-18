'''
This file contains the implementation of the message delivery 
service of message delivery. If an agent is unable to receive
messages, this behaviour will try to send it by a certain time. 
At the end, the message will be discarded.
'''

from datetime import datetime
from pade.behaviours.types import CyclicBehaviour
from queue import Queue
from pade.misc.utility import display_message

class MessageDelivery(CyclicBehaviour):
	''' DeliveryPostponedMessage class basically executes the attempt to deliver 
	the message behaviour. It stores the messages in a queue until the max_wait
	time is reach.
	'''

	def __init__(self, agent, max_wait):
		super().__init__(agent)
		self.queue = Queue()
		self.max_wait = max_wait

	def action(self):
		self.wait(0.5)
		package = self.queue.get()
		elapsed_time = datetime.now() - package['time_stamp']
		if elapsed_time.total_seconds() <= self.max_wait:
			if not self.agent.receiver_available(package['message'].receivers[0]):
				self.queue.put(package)
			else:
				self.agent.send(package['message'])
		else:
			display_message(self.agent, 'A message could not be delivered to the receiver %s.' % package['message'].receivers[0].getName())

	def deliver(self, message):
		self.queue.put({'message': message,	'time_stamp': datetime.now()})