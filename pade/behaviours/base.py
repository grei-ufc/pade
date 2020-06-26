'''
This file implements the needed Behaviour class extensions, in
order to PADE Scheduler be able to manage the agent behaviours.
'''

from pade.behaviours.protocols import Behaviour
from pade.acl.messages import ACLMessage
from time import sleep

class BaseBehaviour(Behaviour):

	''' BaseBehaviour class ihnerits from Behaviour class and
	implements the basic methods for scheduled behaviours.
	'''

	def __init__(self, agent):
		''' This method initializes a new instance of BaseBehaviour
		class and explicitly calls the Behaviour.__init__() method.
		'''
		super().__init__(agent)
		# Lock object (to ensure the mutual exclusion, when needed)
		self.__lock = None

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

	def wait(self, timeout):
		''' This method sleeps a behaviour until occurs a timeout. The
		behaviour will execute normally afterwards.
		'''
		sleep(timeout)


	def on_end(self):
		''' The scheduler will calls this method after the self.done()
		method returns True and before the end of this behaviour. It is
		the last action of a behaviour.
		'''
		pass

	def add_lock(self, lock):
		''' Adds a threading.Lock object to this behaviour, allowing 
		it to execute the mutual exclusion correctly.
		'''
		self.__lock = lock
	

	def lock(self):
		''' Tries to acquire the lock of the threading.Lock object.
		The behaviour will block if fails.
		'''
		self.__lock.acquire()
	

	def unlock(self):
		''' Releases the lock of the threading.Lock object, allowing
		the other behaviours to acquire it.
		'''
		self.__lock.release()
