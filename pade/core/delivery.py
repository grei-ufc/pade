from datetime import datetime
from pade.behaviours.types import CyclicBehaviour
from queue import Queue
from pade.misc.utility import display

class DeliverPostponedMessage(CyclicBehaviour):
	def __init__(self, agent, max_wait):
		super().__init__(agent)
		self.queue = Queue()
		self.max_wait = max_wait

	def action(self):
		self.wait(0.5)
		package = self.queue.get()
		time_elapsed = datetime.now() - package['time_stamp']
		if time_elapsed.total_seconds() <= self.max_wait:
			if not self.agent.receiver_available(package['message'].receivers[0]):
				self.queue.put(package)
			else:
				self.agent.send(package['message'])

	def deliver(self, message):
		self.queue.put({'message': message,	'time_stamp': datetime.now()})