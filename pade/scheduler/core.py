'''
This file implements the basic functionalities of the PADE
Scheduler. The Scheduler aims to manage the agent behaviours,
so that PADE provides new methods to control the behaviours
of the system agents.
'''

from threading import Thread
from pade.behaviours.behaviour import BaseBehaviour

class Scheduler(object):
	''' Scheduler class basically executes the behaviours (under
	'task form') in the active tasks queue. This class too implements
	methods to block and unblock behavioiurs.
	'''

	def __init__(self, agent):
		self.agent = agent
		self.active_tasks = list() # Active tasks queue
		self.blocked_behaviours = list() # Blocked behaviours queue
		self.behaviours = list() # Behaviours queue
		self.running = False # It indicates if the scheduler is running

	def run(self):
		''' It executes all scheduled tasks in the active tasks queue.
		'''
		self.running = True
		while len(self.active_tasks) > 0:
			task = self.active_tasks[0]
			task.start()
			self.dequeue()
		self.running = False

	def enqueue(self, behaviour):
		''' It puts a behaviour, under the 'Task' form, on the end of active
		tasks queue.
		'''
		if isinstance(behaviour, BaseBehaviour):
			self.active_tasks.append(Task(behaviour, self))
			self.wakeup()
		else:
			raise ValueError('behaviour object type must be BaseBehaviour!')

	def dequeue(self):
		''' It removes the first task from active tasks queue.
		'''
		self.active_tasks = self.active_tasks[1:]

	def wakeup(self):
		''' It executes the Scheduler.run() method if the Scheduler
		intance is sleeping.
		'''
		if not self.running:
			self.run()

	def add_behaviour(self, behaviour):
		''' It adds, on the first time, a behaviour in the scheduler
		'''
		if isinstance(behaviour, BaseBehaviour):
			self.behaviours.append(behaviour)
			self.enqueue(behaviour)
		else:
			raise ValueError('behaviour object type must be BaseBehaviour!')

	def remove_behaviour(self, behaviour):
		''' It removes a behaviour from scheduler. It must be used when a
		behaviour finishes.
		'''
		try:
			self.behaviours.remove(behaviour)
		except ValueError:
			raise ValueError('failed to remove the required behaviour from scheduler.')

	def kill(self, thread):
		''' It kills a thread (reference) (X_X)
		'''
		try:
			del thread
		except NameError:
			raise NameError("this thread doesn't exists.")

	def receive_message(self, message):
		''' It passes the arrived message to all existing behaviours (all
		behaviours in the self.behaviours queue).
		'''
		for behaviour in self.behaviours:
			behaviour.receive(message)
		self.unblock_behaviours()

	def unblock_behaviours(self):
		''' It puts the behaviours from blocked behaviours queue to
		active tasks queue.
		'''
		activated_behaviours = []
		for behaviour in self.blocked_behaviours:
			behaviour.unblock()
			self.enqueue(behaviour)
			# It is needed to remove the behaviour form blocked list
			activated_behaviours.append(behaviour)
		# This for is needed because new behaviours may have been added
		# in the blocked behaviours queue.
		for behaviour in activated_behaviours:
			self.blocked_behaviours.remove(behaviour)
		#self.wakeup()

	def block(self, behaviour):
		''' It puts a behaviour to the blocked behaviours queue, after
		its BaseBehaviour.done() method was executed.
		'''
		if isinstance(behaviour, BaseBehaviour):
			self.blocked_behaviours.append(behaviour)
		else:
			raise ValueError('behaviour object type must be BaseBehaviour!')



class Task(Thread):
	''' The Task class manages each behaviour separately in an one thread,
	deciding whether a behaviour must goes to active queue or to blocked
	queue. Each instance of this class runs a behaviour once only.
	'''
	def __init__(self, behaviour, scheduler):
		super().__init__()
		self.behaviour = behaviour
		self.scheduler = scheduler

	def run(self):
		''' This method executes the BaseBehaviour.action() method, checking
		whether a behaviour is done or blocked, and re-scheduling the
		behaviour, if it is needed.
		'''
		self.behaviour.action() # Execute the behaviour actions
		if not self.behaviour.done(): # Verifies if the behaviour will execute again
			if self.behaviour.blocked(): # Verifies if the behaviour was blocked
				self.scheduler.block(self.behaviour) # Goes to blocked queue
			else:
				self.scheduler.enqueue(self.behaviour) # Goes to active queue
		else:
			self.scheduler.remove_behaviour(self.behaviour)
			self.scheduler.kill(self)