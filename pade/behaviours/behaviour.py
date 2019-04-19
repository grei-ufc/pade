'''
This file implements the needed Behaviour class extensions, in
order to PADE Scheduler be able to manage the agent behaviours.
'''

from pade.behaviours.protocols import Behaviour
from pade.acl.messages import ACLMessage

class BaseBehaviour(Behaviour):

	''' BaseBehaviour class ihnerits from Behaviour class and
	implements the basic methods for scheduled behaviours.
	'''

	def __init__(self, agent):
		''' This method initializes a new instance of BaseBehaviour
		class and explicitly calls the Behaviour.__init__() method.
		'''
		super().__init__(agent)
		# It sinalizes to Scheduler if this behaviour is blocked
		self.blocked = False		# Queue of received messages by the agent and unread by this behaviour
		self.messages = list()

	def read(self):
		''' It gets the first message in the local message queue.
		'''
		if self.messages != []:
			message = self.messages[0]
			self.messages = messages[1:]
			return self.messages[0]
		else:
			return None

	def receive(self, message):
		''' It sets a new message on local messages queue.
		'''
		if isinstance(message, ACLMessage):
			self.messages.append(message)
		else:
			raise ValueError('message object type must be ACLMessage!')


	def action(self):
		''' This is an abstract method that must be overridden in the
		child classes, writing the main actions of this behaviour.
		'''
		pass

	def done(self):
		''' This is an abstract method that must be overridden in the
		child classes, dealing with the finish of this behaviour.
		'''
		pass

	def block(self):
		''' This method blocks a behaviour until an event occurs
		in the system (the agent receives a message). This block method
		wait the finish of the self.action() execution, blocking the 
		behaviour afterwards.
		'''
		self.blocked = True

	def sleep(self, timeout):
		''' This method sleeps a behaviour until occurs a timeout. The
		behaviour will execute normally afterwards.
		'''
		sleep(timeout)

	def unblock(self):
		''' This method sinalizes to Scheduler to unblock this behaviour.
		'''
		self.blocked = False

	def blocked(self):
		''' It returns the status of this behaviour.
		'''
		return self.blocked